/**
 * DocumentTemplatesTab — Admin-only editor for document templates.
 *
 * Per doc type, the admin can:
 *   - "Customize" (snapshot the current built-in template into the DB; from
 *     then on, the editor's HTML is used for ALL future generations of that
 *     doc type).
 *   - Edit the HTML in a textarea with a live preview iframe.
 *   - "Revert to Default" which deletes the override and restores the
 *     built-in generator.
 *
 * Placeholders (e.g. {customer_name}, {total_price_formatted}) are substituted
 * at generation time. Only generic placeholders are supported in custom
 * templates — for document-type-specific fields (transaction tables, computed
 * amounts, etc.) the built-in generator should be used.
 */
import { useEffect, useRef, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Button } from "../ui/button";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Badge } from "../ui/badge";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../ui/alert-dialog";
import { FileText, Save, Trash2, RefreshCw, Loader2, Eye, Code } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

const DOC_TYPES = [
  { value: "sales_agreement", label: "Sales Agreement" },
  { value: "allotment_letter", label: "Allotment Letter" },
  { value: "price_breakup", label: "Price Breakup" },
  { value: "cost_breakup", label: "Cost Breakup" },
  { value: "demand_letter", label: "Demand Letter" },
  { value: "payment_schedule", label: "Payment Schedule" },
  { value: "noc_hdfc", label: "HDFC Bank NOC" },
  { value: "noc_bob", label: "Bank of Baroda NOC" },
  { value: "noc_tata", label: "TATA Capital NOC" },
  { value: "noc_bajaj", label: "Bajaj Housing Finance NOC" },
];

const PLACEHOLDERS = [
  "{customer_name}", "{customer_id}", "{unit_number}", "{tower}",
  "{project}", "{total_price}", "{total_price_formatted}",
  "{saleable_area}", "{uds}", "{booking_amount}", "{booking_date}",
  "{date}", "{father_name}", "{pan_number}", "{phone}", "{email}",
  "{address}", "{bhk_type}", "{floor}", "{rate_per_sqft}",
  "{base_price}", "{gst_amount}", "{labour_cess}", "{club_house_charges}",
];

const DocumentTemplatesTab = () => {
  const [templates, setTemplates] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [selectedDocType, setSelectedDocType] = useState("");
  const [sampleCustomerId, setSampleCustomerId] = useState("");
  const [content, setContent] = useState("");
  const [currentTemplate, setCurrentTemplate] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [snapshotting, setSnapshotting] = useState(false);
  const [showCode, setShowCode] = useState(false);
  const [revertConfirmOpen, setRevertConfirmOpen] = useState(false);
  const iframeRef = useRef(null);

  // Load templates + customers
  useEffect(() => {
    const load = async () => {
      try {
        const [tmplRes, custRes] = await Promise.all([
          axios.get(`${API}/templates`),
          axios.get(`${API}/customers`),
        ]);
        setTemplates(tmplRes.data || []);
        const custList = Array.isArray(custRes.data)
          ? custRes.data
          : custRes.data?.customers || [];
        setCustomers(custList);
        if (custList.length > 0) {
          setSampleCustomerId(custList[0].id);
        }
      } catch {
        toast.error("Failed to load templates");
      }
    };
    load();
  }, []);

  // When doc type changes → load that template's content (or clear)
  useEffect(() => {
    if (!selectedDocType) {
      setContent("");
      setCurrentTemplate(null);
      return;
    }
    const tmpl = templates.find((t) => t.doc_type === selectedDocType && t.is_active);
    if (tmpl) {
      setCurrentTemplate(tmpl);
      setContent(tmpl.content || "");
    } else {
      setCurrentTemplate(null);
      setContent("");
    }
  }, [selectedDocType, templates]);

  // Render content to iframe
  useEffect(() => {
    if (!iframeRef.current) return;
    const docu = iframeRef.current.contentDocument;
    if (!docu) return;
    docu.open();
    docu.write(content || "<p style='padding:20px;color:#94a3b8'>Select a document type and click Customize to start editing.</p>");
    docu.close();
  }, [content]);

  const refreshTemplates = async () => {
    const res = await axios.get(`${API}/templates`);
    setTemplates(res.data || []);
    return res.data || [];
  };

  const handleSnapshot = async () => {
    if (!selectedDocType) {
      toast.error("Choose a document type first");
      return;
    }
    if (!sampleCustomerId) {
      toast.error("Choose a sample customer to render the default");
      return;
    }
    setSnapshotting(true);
    try {
      const res = await axios.post(
        `${API}/templates/snapshot/${selectedDocType}`,
        { customer_id: sampleCustomerId }
      );
      setCurrentTemplate(res.data);
      setContent(res.data.content || "");
      await refreshTemplates();
      toast.success("Editable template created from the current default");
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Failed to create template");
    } finally {
      setSnapshotting(false);
    }
  };

  const handleSave = async () => {
    if (!currentTemplate?.id) return;
    setSaving(true);
    try {
      await axios.put(`${API}/templates/${currentTemplate.id}`, {
        content,
        is_active: true,
      });
      await refreshTemplates();
      toast.success("Template saved — future generations will use it");
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Failed to save template");
    } finally {
      setSaving(false);
    }
  };

  const handleRevert = async () => {
    if (!currentTemplate?.id) return;
    setLoading(true);
    try {
      await axios.delete(`${API}/templates/${currentTemplate.id}`);
      setCurrentTemplate(null);
      setContent("");
      await refreshTemplates();
      toast.success("Reverted to built-in default");
    } catch {
      toast.error("Failed to revert template");
    } finally {
      setLoading(false);
      setRevertConfirmOpen(false);
    }
  };

  const insertPlaceholder = (ph) => {
    setContent((c) => c + " " + ph);
  };

  const activeForType = (type) =>
    templates.some((t) => t.doc_type === type && t.is_active);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-primary" /> Document Template Editor
        </CardTitle>
        <CardDescription>
          Customize the HTML used to generate documents. When a template is
          saved, all future documents of that type are rendered from it
          (placeholders are auto-filled per customer).
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label>Document Type</Label>
            <Select value={selectedDocType} onValueChange={setSelectedDocType}>
              <SelectTrigger data-testid="template-doctype-select">
                <SelectValue placeholder="Choose a document" />
              </SelectTrigger>
              <SelectContent>
                {DOC_TYPES.map((d) => (
                  <SelectItem key={d.value} value={d.value}>
                    {d.label}{" "}
                    {activeForType(d.value) ? " • Customized" : ""}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Sample Customer (for rendering the default)</Label>
            <Select value={sampleCustomerId} onValueChange={setSampleCustomerId}>
              <SelectTrigger data-testid="template-sample-customer-select">
                <SelectValue placeholder="Pick a customer" />
              </SelectTrigger>
              <SelectContent>
                {customers.slice(0, 200).map((c) => (
                  <SelectItem key={c.id} value={c.id}>
                    {c.name} ({c.customer_id || c.unit_number})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-end gap-2">
            {!currentTemplate && selectedDocType && (
              <Button
                onClick={handleSnapshot}
                disabled={snapshotting || !sampleCustomerId}
                data-testid="snapshot-template-btn"
              >
                {snapshotting ? (
                  <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                ) : (
                  <Code className="w-4 h-4 mr-1" />
                )}
                Customize
              </Button>
            )}
            {currentTemplate && (
              <>
                <Button
                  onClick={handleSave}
                  disabled={saving}
                  data-testid="save-template-btn"
                >
                  {saving ? (
                    <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                  ) : (
                    <Save className="w-4 h-4 mr-1" />
                  )}
                  Save
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setRevertConfirmOpen(true)}
                  disabled={loading}
                  data-testid="revert-template-btn"
                >
                  <Trash2 className="w-4 h-4 mr-1" />
                  Revert
                </Button>
              </>
            )}
          </div>
        </div>

        {currentTemplate && (
          <div className="flex items-center gap-2 text-xs text-slate-600 flex-wrap">
            <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-300">
              Active Override
            </Badge>
            <span>Insert placeholder:</span>
            {PLACEHOLDERS.map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => insertPlaceholder(p)}
                className="px-2 py-0.5 bg-slate-100 hover:bg-slate-200 rounded text-xs font-mono"
              >
                {p}
              </button>
            ))}
          </div>
        )}

        {currentTemplate && (
          <div className="flex items-center gap-2">
            <Button
              variant={showCode ? "default" : "outline"}
              size="sm"
              onClick={() => setShowCode(true)}
            >
              <Code className="w-4 h-4 mr-1" /> HTML
            </Button>
            <Button
              variant={!showCode ? "default" : "outline"}
              size="sm"
              onClick={() => setShowCode(false)}
            >
              <Eye className="w-4 h-4 mr-1" /> Preview
            </Button>
          </div>
        )}

        <div className="border rounded-lg overflow-hidden bg-slate-100">
          {showCode ? (
            <Textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="font-mono text-xs h-[60vh] resize-none border-0 bg-white"
              placeholder="HTML content (placeholders like {customer_name} will be substituted at generation)"
              data-testid="template-html-textarea"
            />
          ) : (
            <iframe
              ref={iframeRef}
              title="Template preview"
              className="w-full bg-white"
              style={{ height: "60vh", border: 0 }}
              sandbox="allow-same-origin"
            />
          )}
        </div>

        {!selectedDocType && (
          <div className="text-center py-6 text-slate-500">
            <FileText className="w-10 h-10 mx-auto mb-2 text-slate-300" />
            <p className="text-sm">Pick a document type above to begin.</p>
          </div>
        )}
      </CardContent>

      <AlertDialog open={revertConfirmOpen} onOpenChange={setRevertConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Revert to Default?</AlertDialogTitle>
            <AlertDialogDescription>
              This will delete the custom template and restore the built-in
              default for this document type. Any future generations will use
              the system default. This cannot be undone, but you can re-create
              the template by clicking "Customize" again.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleRevert}
              className="bg-red-600 hover:bg-red-700"
              data-testid="confirm-revert-template-btn"
            >
              <RefreshCw className="w-4 h-4 mr-1" />
              Revert to Default
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  );
};

export default DocumentTemplatesTab;
