/* XSS unit test for sanitizeEmailHtml + safePreview helpers
 * Loads with jsdom -> simulates browser globals -> imports DOMPurify
 * Re-implements the same FORBID_TAGS/FORBID_ATTR config used in
 * /app/frontend/src/utils/sanitize.js to assert behaviour.
 */
const { JSDOM } = require("jsdom");
const dom = new JSDOM("<!DOCTYPE html><html><body></body></html>");
global.window = dom.window;
global.document = dom.window.document;
global.HTMLElement = dom.window.HTMLElement;
global.Node = dom.window.Node;
global.NodeFilter = dom.window.NodeFilter;
global.DocumentFragment = dom.window.DocumentFragment;
global.Element = dom.window.Element;
global.Text = dom.window.Text;

const DOMPurify = require("/app/frontend/node_modules/dompurify")(dom.window);

const FORBID_TAGS = [
  "script","iframe","object","embed","link","base","form",
  "input","button","textarea","select","option",
];
const FORBID_ATTR = [
  "onerror","onload","onclick","onmouseover","onmouseout",
  "onfocus","onblur","onsubmit","onchange","onkeydown",
  "onkeyup","onkeypress","formaction","srcdoc",
];

DOMPurify.addHook("afterSanitizeAttributes", (node) => {
  if (node.tagName === "A" && node.getAttribute("target") === "_blank") {
    node.setAttribute("rel", "noopener noreferrer");
  }
});

const sanitizeEmailHtml = (html) =>
  DOMPurify.sanitize(html || "", {
    WHOLE_DOCUMENT: true,
    ADD_TAGS: ["style"],
    ADD_ATTR: ["target","rel"],
    FORBID_TAGS, FORBID_ATTR,
    ALLOW_DATA_ATTR: false,
  });

let failures = 0;
function expect(name, cond, extra="") {
  console.log((cond ? "PASS" : "FAIL") + ": " + name + (extra && !cond ? " | " + extra : ""));
  if (!cond) failures++;
}

// Malicious payload from the review request
const malicious = '<img src=x onerror=alert(1)><script>alert(2)</script><a target=_blank href=https://example.com>hi</a>';
const out = sanitizeEmailHtml(malicious);
console.log("---- sanitised payload ----");
console.log(out);
console.log("---------------------------");

expect("strips onerror attribute", !/onerror/i.test(out));
expect("strips <script> tag", !/<script/i.test(out));
expect("anchor gains rel=\"noopener noreferrer\"", /rel="noopener noreferrer"/.test(out));
expect("keeps anchor href", /href="https:\/\/example\.com"/.test(out));
expect("keeps anchor text", />hi</.test(out));

// Verify other forbidden tags
const tagPayload = "<iframe src=x></iframe><object></object><embed><form><input><button>X</button><textarea></textarea><select><option>1</option></select><link>";
const tagOut = sanitizeEmailHtml(tagPayload);
expect("strips <iframe>", !/<iframe/i.test(tagOut));
expect("strips <object>", !/<object/i.test(tagOut));
expect("strips <embed>", !/<embed/i.test(tagOut));
expect("strips <form>", !/<form/i.test(tagOut));
expect("strips <input>", !/<input/i.test(tagOut));
expect("strips <button>", !/<button/i.test(tagOut));
expect("strips <textarea>", !/<textarea/i.test(tagOut));
expect("strips <select>", !/<select/i.test(tagOut));
expect("strips <link>", !/<link/i.test(tagOut));

// Email template features that MUST still render
const emailTemplate = '<style>.x{color:red}</style><div style="background:#000;color:#FFD700;padding:20px"><h1>Hello</h1><table><tr><td style="border:1px solid gold">cell</td></tr></table><a href="https://wa.me/1" target="_blank" style="background:gold;color:black;padding:10px">Book Consultation</a></div>';
const tplOut = sanitizeEmailHtml(emailTemplate);
console.log("---- email template output ----");
console.log(tplOut);
console.log("-------------------------------");
expect("keeps <style> block", /<style/.test(tplOut));
expect("keeps inline style on div", /style="background:#000/.test(tplOut) || /style="background: ?#000/.test(tplOut));
expect("keeps inline style on anchor (CTA button)", /style="background:gold/.test(tplOut) || /background: ?gold/.test(tplOut));
expect("keeps table markup", /<table/.test(tplOut) && /<td/.test(tplOut));
expect("CTA anchor target=_blank kept + rel hardened", /target="_blank"/.test(tplOut) && /rel="noopener noreferrer"/.test(tplOut));

// formaction + srcdoc payloads
const advanced = '<a href="javascript:alert(1)">x</a><img srcdoc="alert(1)"><input formaction="javascript:alert(1)">';
const advOut = sanitizeEmailHtml(advanced);
expect("strips javascript: href", !/javascript:/i.test(advOut));
expect("strips srcdoc attr", !/srcdoc/i.test(advOut));
expect("strips formaction attr", !/formaction/i.test(advOut));

// openSafePdfPreview scheme check (re-implement)
const openSafePdfPreviewCheck = (dataUrl) => {
  if (typeof dataUrl !== "string" || !dataUrl.startsWith("data:application/pdf;")) return null;
  return dataUrl.replace(/"/g, "%22");
};
expect("rejects non-pdf data URL", openSafePdfPreviewCheck("data:text/html;base64,PHNjcmlwdD4=") === null);
expect("rejects javascript: URL", openSafePdfPreviewCheck("javascript:alert(1)") === null);
expect("rejects http URL", openSafePdfPreviewCheck("http://evil.com/file.pdf") === null);
expect("accepts valid pdf data URL", openSafePdfPreviewCheck("data:application/pdf;base64,AAAA") === "data:application/pdf;base64,AAAA");
expect("escapes quotes in URL", openSafePdfPreviewCheck('data:application/pdf;base64,AA"BB').includes("%22"));

console.log("\nTotal failures: " + failures);
process.exit(failures === 0 ? 0 : 1);
