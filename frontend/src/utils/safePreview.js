import DOMPurify from "dompurify";

/**
 * Safely open HTML content in a new browser window for print/PDF.
 * Uses Blob URLs instead of document.write() to prevent XSS vectors.
 */
export const openSafePreviewWindow = (htmlContent) => {
  const sanitized = DOMPurify.sanitize(htmlContent, {
    WHOLE_DOCUMENT: true,
    ADD_TAGS: ['style', 'link', 'meta'],
    ADD_ATTR: ['target'],
  });
  const blob = new Blob([sanitized], { type: 'text/html; charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const win = window.open(url, '_blank');
  // Revoke after a delay to allow the window to load
  if (win) {
    setTimeout(() => URL.revokeObjectURL(url), 60000);
  }
  return win;
};

/**
 * Safely open a PDF data URL in a new browser window using an iframe.
 */
export const openSafePdfPreview = (dataUrl) => {
  const sanitizedUrl = DOMPurify.sanitize(dataUrl);
  const html = `<!DOCTYPE html><html><head><title>PDF Preview</title></head><body style="margin:0;"><iframe src="${sanitizedUrl}" style="width:100%;height:100vh;border:none;"></iframe></body></html>`;
  const blob = new Blob([html], { type: 'text/html; charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const win = window.open(url, '_blank');
  if (win) {
    setTimeout(() => URL.revokeObjectURL(url), 60000);
  }
  return win;
};
