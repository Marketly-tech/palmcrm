import DOMPurify from "dompurify";

/**
 * Safely open HTML content in a new browser window for print/PDF.
 *
 * Hardening:
 *  • Uses Blob URLs (never document.write) so the new window's origin and
 *    cookies stay isolated.
 *  • DOMPurify strips <script>/<iframe>/<object>/<embed>, all on* event-handler
 *    attributes, and javascript:/srcdoc payloads.
 *  • `noopener,noreferrer` rel hook prevents the new window from accessing
 *    `window.opener`.
 */
const FORBID_TAGS = ["script", "iframe", "object", "embed", "base", "form"];
const FORBID_ATTR = [
  "onerror", "onload", "onclick", "onmouseover", "onmouseout",
  "onfocus", "onblur", "onsubmit", "onchange", "onkeydown",
  "onkeyup", "onkeypress", "formaction", "srcdoc",
];

DOMPurify.addHook("afterSanitizeAttributes", (node) => {
  if (node.tagName === "A" && node.getAttribute("target") === "_blank") {
    node.setAttribute("rel", "noopener noreferrer");
  }
});

export const openSafePreviewWindow = (htmlContent) => {
  const sanitized = DOMPurify.sanitize(htmlContent || "", {
    WHOLE_DOCUMENT: true,
    ADD_TAGS: ["style", "meta"],
    ADD_ATTR: ["target", "rel"],
    FORBID_TAGS,
    FORBID_ATTR,
    ALLOW_DATA_ATTR: false,
  });
  const blob = new Blob([sanitized], { type: "text/html; charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const win = window.open(url, "_blank", "noopener,noreferrer");
  if (win) {
    setTimeout(() => URL.revokeObjectURL(url), 60000);
  }
  return win;
};

/**
 * Safely open a PDF data URL in a new browser window using an iframe.
 *
 * The wrapper HTML is built from a static string template and the data URL is
 * scheme-checked (must start with `data:application/pdf;`) before being
 * stamped into the iframe src — preventing javascript: or arbitrary-origin
 * URLs from sneaking through.
 */
export const openSafePdfPreview = (dataUrl) => {
  if (typeof dataUrl !== "string" || !dataUrl.startsWith("data:application/pdf;")) {
    return null;
  }
  // The data URL itself is safe (pdf MIME, base64 payload only). We still
  // sanitize-encode just the URL string so an embedded quote can't break out
  // of the src="" attribute.
  const safeUrl = dataUrl.replace(/"/g, "%22");
  const html = `<!DOCTYPE html><html><head><title>PDF Preview</title></head><body style="margin:0;"><iframe src="${safeUrl}" style="width:100%;height:100vh;border:none;"></iframe></body></html>`;
  const blob = new Blob([html], { type: "text/html; charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const win = window.open(url, "_blank", "noopener,noreferrer");
  if (win) {
    setTimeout(() => URL.revokeObjectURL(url), 60000);
  }
  return win;
};
