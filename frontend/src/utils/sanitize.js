/**
 * Strict HTML sanitizer for rendering server-generated email/document
 * previews via dangerouslySetInnerHTML.
 *
 * Why a dedicated helper?
 *  • Centralises DOMPurify config so every preview surface gets identical
 *    protection (no drift across components).
 *  • Explicitly blocks <script>/<iframe>/<object>/<embed>, on* event-handler
 *    attributes, javascript:/data:-as-script URLs — defence-in-depth even
 *    though the source HTML is server-generated.
 *  • Keeps the layout-critical bits emails need: inline `style=` attributes,
 *    `<style>` blocks, `<table>` markup, anchor links with `target=_blank`.
 */
import DOMPurify from "dompurify";

const FORBID_TAGS = [
  "script", "iframe", "object", "embed", "link", "base", "form",
  "input", "button", "textarea", "select", "option",
];

const FORBID_ATTR = [
  "onerror", "onload", "onclick", "onmouseover", "onmouseout",
  "onfocus", "onblur", "onsubmit", "onchange", "onkeydown",
  "onkeyup", "onkeypress", "formaction", "srcdoc",
];

// Allow target=_blank for CTA buttons; the noopener/noreferrer hook below
// auto-hardens those anchors so they can't manipulate window.opener.
DOMPurify.addHook("afterSanitizeAttributes", (node) => {
  if (node.tagName === "A" && node.getAttribute("target") === "_blank") {
    node.setAttribute("rel", "noopener noreferrer");
  }
});

export const sanitizeEmailHtml = (html) =>
  DOMPurify.sanitize(html || "", {
    WHOLE_DOCUMENT: true,
    ADD_TAGS: ["style"],
    ADD_ATTR: ["target", "rel"],
    FORBID_TAGS,
    FORBID_ATTR,
    ALLOW_DATA_ATTR: false,
  });

/**
 * Sanitise a plain attribute value (e.g. a filename used inside an alt attr).
 * Uses strict-text mode — strips ALL HTML tags.
 */
export const sanitizeText = (value) =>
  DOMPurify.sanitize(value || "", { ALLOWED_TAGS: [], ALLOWED_ATTR: [] });
