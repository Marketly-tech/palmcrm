/**
 * EditableDocumentDialog
 * Renders a generated document in an iframe (preserves all CSS/formatting).
 * Toggle "Edit" → makes the iframe body contenteditable so the user can tweak
 * text in-place. "Save" persists the updated HTML to the backend, "Download"
 * fetches the PDF via WeasyPrint.
 *
 * The iframe approach keeps the document's @page rules, fonts, and layout
 * isolated from the surrounding app CSS so nothing overlaps.
 */
import { useEffect, useRef, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../../ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../../ui/alert-dialog";
import { Button } from "../../ui/button";
import { Edit, Save, Download, X, Loader2, BookmarkPlus } from "lucide-react";
import { useAuth } from "../../../context/AuthContext";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

const EditableDocumentDialog = ({
  open,
  onOpenChange,
  doc,
  customerName,
  onSaved,
}) => {
  const { user } = useAuth();
  const canSaveMaster = user?.role === "admin" || user?.role === "manager";
  const iframeRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [savingMaster, setSavingMaster] = useState(false);
  const [confirmMasterOpen, setConfirmMasterOpen] = useState(false);
  const [content, setContent] = useState("");

  // Load HTML when dialog opens
  useEffect(() => {
    if (!open || !doc?.id) return;
    let cancelled = false;
    setEditing(false);
    setLoading(true);
    axios
      .get(`${API}/documents/html/${doc.id}`)
      .then((res) => {
        if (cancelled) return;
        setContent(res.data.content || "");
      })
      .catch(() => toast.error("Failed to load document"))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [open, doc?.id]);

  // Write content into iframe whenever it changes (and the iframe is mounted)
  useEffect(() => {
    if (!iframeRef.current || !content) return;
    const iframe = iframeRef.current;
    const docu = iframe.contentDocument || iframe.contentWindow?.document;
    if (!docu) return;
    docu.open();
    docu.write(content);
    docu.close();
    // Apply contenteditable to the body when in edit mode
    if (docu.body) {
      docu.body.contentEditable = editing ? "true" : "false";
      docu.body.style.outline = editing ? "2px dashed #D4AF37" : "none";
      docu.body.style.outlineOffset = "4px";
    }
  }, [content, editing]);

  const toggleEdit = () => {
    setEditing((e) => !e);
  };

  const handleSave = async () => {
    if (!iframeRef.current) return;
    const docu = iframeRef.current.contentDocument;
    if (!docu) return;
    setSaving(true);
    try {
      const updated = "<!DOCTYPE html>\n" + docu.documentElement.outerHTML;
      await axios.put(`${API}/documents/html/${doc.id}`, { content: updated });
      setContent(updated);
      setEditing(false);
      toast.success("Changes saved");
      if (onSaved) onSaved();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Failed to save changes");
    } finally {
      setSaving(false);
    }
  };

  const handleSaveAsMaster = async () => {
    setSavingMaster(true);
    try {
      // If user is currently editing, persist the per-customer changes first
      // so the generated doc's `content` is up-to-date before we promote it.
      if (editing) {
        const docu = iframeRef.current?.contentDocument;
        if (docu) {
          const updated = "<!DOCTYPE html>\n" + docu.documentElement.outerHTML;
          await axios.put(`${API}/documents/html/${doc.id}`, { content: updated });
          setContent(updated);
          setEditing(false);
        }
      }
      const res = await axios.post(`${API}/templates/save-from-document/${doc.id}`);
      toast.success(
        res.data?.message
          ? `${res.data.message} — applies to all future ${prettyTitle.toLowerCase()}s`
          : "Saved as master template"
      );
      setConfirmMasterOpen(false);
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Failed to save master template");
    } finally {
      setSavingMaster(false);
    }
  };

  const handleDiscard = () => {
    // Reload from backend
    setEditing(false);
    setLoading(true);
    axios
      .get(`${API}/documents/html/${doc.id}`)
      .then((res) => setContent(res.data.content || ""))
      .catch(() => toast.error("Failed to reload document"))
      .finally(() => setLoading(false));
  };

  const handleDownload = async () => {
    setDownloading(true);
    try {
      // If user is currently editing, auto-save first
      if (editing) await handleSave();
      const response = await axios.get(`${API}/documents/pdf/${doc.id}`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(
        new Blob([response.data], { type: "application/pdf" })
      );
      const link = document.createElement("a");
      link.href = url;
      const docTypeLabel = (doc.doc_type || "Document")
        .replace(/_/g, " ")
        .replace(/\b\w/g, (c) => c.toUpperCase())
        .replace(/ /g, "_");
      link.setAttribute(
        "download",
        `RRL_${docTypeLabel}_${(customerName || "Customer").replace(/ /g, "_")}.pdf`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      toast.error("Failed to download PDF");
    } finally {
      setDownloading(false);
    }
  };

  const prettyTitle = (doc?.doc_type || "Document")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl max-h-[95vh] p-0 gap-0">
        <DialogHeader className="px-6 pt-5 pb-3 border-b">
          <div className="flex items-center justify-between gap-4">
            <DialogTitle data-testid="edit-doc-title">{prettyTitle}</DialogTitle>
            <div className="flex items-center gap-2">
              {editing ? (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleDiscard}
                    disabled={saving}
                    data-testid="discard-edit-btn"
                  >
                    <X className="w-4 h-4 mr-1" />
                    Discard
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleSave}
                    disabled={saving}
                    data-testid="save-edit-btn"
                  >
                    {saving ? (
                      <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                    ) : (
                      <Save className="w-4 h-4 mr-1" />
                    )}
                    Save Changes
                  </Button>
                </>
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={toggleEdit}
                  disabled={loading}
                  data-testid="enter-edit-btn"
                >
                  <Edit className="w-4 h-4 mr-1" />
                  Edit
                </Button>
              )}
              <Button
                size="sm"
                onClick={handleDownload}
                disabled={downloading || saving || loading}
                data-testid="download-pdf-btn"
              >
                {downloading ? (
                  <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                ) : (
                  <Download className="w-4 h-4 mr-1" />
                )}
                Download PDF
              </Button>
              {canSaveMaster && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setConfirmMasterOpen(true)}
                  disabled={loading || saving || savingMaster}
                  title="Save current content as the master template for all future generations"
                  data-testid="save-master-btn"
                >
                  {savingMaster ? (
                    <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                  ) : (
                    <BookmarkPlus className="w-4 h-4 mr-1" />
                  )}
                  Save as Master
                </Button>
              )}
            </div>
          </div>
          {editing && (
            <p className="text-xs text-amber-700 mt-2">
              Edit mode active — click anywhere in the document to make changes.
              Use Save Changes when done; formatting is preserved.
            </p>
          )}
        </DialogHeader>
        <div className="bg-slate-100 p-4 h-[80vh] overflow-auto">
          {loading ? (
            <div className="flex items-center justify-center h-full text-slate-500">
              <Loader2 className="w-6 h-6 animate-spin mr-2" />
              Loading document...
            </div>
          ) : (
            <iframe
              ref={iframeRef}
              title="Document preview"
              className="w-full h-full bg-white shadow-md mx-auto"
              style={{ border: "1px solid #e2e8f0", minHeight: "100%" }}
              sandbox="allow-same-origin"
            />
          )}
        </div>
      </DialogContent>
      <AlertDialog open={confirmMasterOpen} onOpenChange={setConfirmMasterOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Save as master template?</AlertDialogTitle>
            <AlertDialogDescription>
              All <strong>future</strong> <em>{prettyTitle}</em> documents will
              use this format (layout, styling, legal text). Customer-specific
              fields — name, unit number, prices, address, dates — are
              automatically refilled from each customer's profile, so any
              values currently shown in this document are{" "}
              <strong>NOT</strong> baked into the master. Existing generated
              documents are not affected.
              <br />
              <br />
              You can revert to the system default later from Settings → Document
              Templates.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={savingMaster} data-testid="confirm-master-cancel">Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleSaveAsMaster}
              disabled={savingMaster}
              data-testid="confirm-master-save"
            >
              {savingMaster ? (
                <Loader2 className="w-4 h-4 mr-1 animate-spin" />
              ) : (
                <BookmarkPlus className="w-4 h-4 mr-1" />
              )}
              Save as Master
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Dialog>
  );
};

export default EditableDocumentDialog;
