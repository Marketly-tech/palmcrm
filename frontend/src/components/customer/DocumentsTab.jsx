/**
 * DocumentsTab - Generated documents management + Bank NOC (Disbursement Documents)
 */
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Button } from "../ui/button";
import { Label } from "../ui/label";
import { Badge } from "../ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Plus, FileText, Eye, Download, Trash2, Loader2, Building2, Lock } from "lucide-react";
import { getStatusBadge } from "./utils";
import axios from "axios";

const NOC_TYPES = [
  { key: "noc_hdfc", label: "HDFC Bank", color: "red" },
  { key: "noc_bob", label: "Bank of Baroda", color: "orange" },
  { key: "noc_tata", label: "TATA Capital", color: "blue" },
  { key: "noc_bajaj", label: "Bajaj Housing Finance", color: "violet" },
];

const DocumentsTab = ({
  documents,
  customer,
  isAccountsRole,
  onGenerateDocument,
  onPreviewDocument,
  onDownloadDocument,
  onDeleteDocument,
  onGenerateNoc,
  generatingNoc,
}) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [docType, setDocType] = useState("");

  const handleGenerate = async () => {
    if (!docType) return;
    await onGenerateDocument(docType);
    setDocType("");
    setDialogOpen(false);
  };

  const nocDocTypes = ["noc_hdfc", "noc_bob", "noc_tata", "noc_bajaj"];

  const nocDocuments = documents.filter(doc =>
    nocDocTypes.includes(doc.doc_type)
  );

  const regularDocuments = documents.filter(doc =>
    !nocDocTypes.includes(doc.doc_type)
  );

  const getNocLabel = (type) => {
    const labels = { noc_hdfc: "HDFC Bank NOC", noc_bob: "Bank of Baroda NOC", noc_tata: "TATA Capital NOC", noc_bajaj: "Bajaj Housing Finance NOC" };
    return labels[type] || type;
  };

  return (
    <>
      {customer?.id && (
        <Card className="border-amber-200 bg-amber-50/40" data-testid="original-booking-form-card">
          <CardHeader className="flex flex-row items-start justify-between gap-3">
            <div className="flex items-start gap-3">
              <div className="rounded-md bg-amber-100 p-2 mt-0.5">
                <Lock className="w-5 h-5 text-amber-700" />
              </div>
              <div>
                <CardTitle className="flex items-center gap-2 text-amber-900">
                  Original Booking Form
                  <Badge className="bg-amber-200 text-amber-900 hover:bg-amber-200">Locked</Badge>
                </CardTitle>
                <CardDescription className="mt-1">
                  Immutable copy of the booking form preview that was emailed to the customer on the day of booking. Cannot be edited.
                  {customer.original_booking_form_pdf_recovered_from ? (
                    <span className="block mt-1 text-emerald-700">
                      ✓ Restored from original email attachment (perfect fidelity)
                    </span>
                  ) : customer.original_booking_form_html ? (
                    <span className="block mt-1 text-slate-600">
                      Rendered from the frozen HTML snapshot
                      {customer.original_booking_form_snapshot_at &&
                        ` — locked on ${new Date(customer.original_booking_form_snapshot_at).toLocaleDateString()}`}
                    </span>
                  ) : (
                    <span className="block mt-1 text-slate-500">
                      No snapshot on file — run the admin backfill once.
                    </span>
                  )}
                </CardDescription>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <Button
                variant="outline"
                className="border-amber-400 text-amber-900 hover:bg-amber-100"
                data-testid="view-original-booking-form-btn"
                onClick={async () => {
                  try {
                    const backend = process.env.REACT_APP_BACKEND_URL || "";
                    const res = await axios.get(
                      `${backend}/api/customers/${customer.id}/original-booking-form.pdf`,
                      { responseType: "blob" }
                    );
                    const blob = new Blob([res.data], { type: "application/pdf" });
                    const objUrl = URL.createObjectURL(blob);
                    window.open(objUrl, "_blank", "noopener,noreferrer");
                  } catch (err) {
                    alert(
                      `Could not load original booking form: ${
                        err.response?.data?.detail || err.message
                      }`
                    );
                  }
                }}
              >
                <Eye className="w-4 h-4 mr-2" />
                View
              </Button>
              <Button
                variant="outline"
                className="border-amber-400 text-amber-900 hover:bg-amber-100"
                data-testid="download-original-booking-form-btn"
                onClick={async () => {
                  try {
                    const backend = process.env.REACT_APP_BACKEND_URL || "";
                    const res = await axios.get(
                      `${backend}/api/customers/${customer.id}/original-booking-form.pdf`,
                      { responseType: "blob" }
                    );
                    const blob = new Blob([res.data], { type: "application/pdf" });
                    const objUrl = URL.createObjectURL(blob);
                    const safe = (customer.name || "Customer").trim().replace(/\s+/g, "_");
                    const a = document.createElement("a");
                    a.href = objUrl;
                    a.download = `RRL_OriginalBookingForm_${safe}.pdf`;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    setTimeout(() => URL.revokeObjectURL(objUrl), 1000);
                  } catch (err) {
                    alert(
                      `Could not download original booking form: ${
                        err.response?.data?.detail || err.message
                      }`
                    );
                  }
                }}
              >
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
            </div>
          </CardHeader>
        </Card>
      )}

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Generated Documents</CardTitle>
            <CardDescription>Agreements, letters, and PDFs</CardDescription>
          </div>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button data-testid="generate-doc-btn">
                <Plus className="w-4 h-4 mr-2" />
                Generate Document
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Generate Document</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label>Document Type</Label>
                  <Select value={docType} onValueChange={setDocType}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select document type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sales_agreement">Sales Agreement</SelectItem>
                      <SelectItem value="allotment_letter">Allotment Letter</SelectItem>
                      <SelectItem value="price_breakup">Price Breakup</SelectItem>
                      <SelectItem value="cost_breakup">Cost Breakup</SelectItem>
                      <SelectItem value="demand_letter">Demand Letter</SelectItem>
                      <SelectItem value="payment_schedule">Payment Schedule</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button onClick={handleGenerate} className="w-full">
                  Generate
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </CardHeader>
        <CardContent>
          {regularDocuments.length > 0 ? (
            <div className="space-y-4">
              {regularDocuments.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-4">
                    <FileText className="w-8 h-8 text-primary" />
                    <div>
                      <p className="font-medium capitalize">{doc.doc_type.replace(/_/g, " ")}</p>
                      <p className="text-sm text-slate-500">
                        Generated: {new Date(doc.generated_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={getStatusBadge(doc.status)}>{doc.status}</Badge>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onPreviewDocument(doc)}
                      data-testid={`preview-doc-${doc.id}`}
                    >
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onDownloadDocument(doc)}
                      data-testid={`download-doc-${doc.id}`}
                    >
                      <Download className="w-4 h-4" />
                    </Button>
                    {!isAccountsRole && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={() => onDeleteDocument(doc, "generated")}
                        data-testid={`delete-doc-${doc.id}`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500">
              <FileText className="w-12 h-12 mx-auto mb-4 text-slate-300" />
              <p>No documents generated yet</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Disbursement Documents - Bank NOC Section */}
      <Card className="mt-6" data-testid="disbursement-docs-card">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Building2 className="w-5 h-5 text-primary" />
            <div>
              <CardTitle>Disbursement Documents</CardTitle>
              <CardDescription>Generate Bank NOC (No Objection Certificate) letters</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
            {NOC_TYPES.map((noc) => (
              <Button
                key={noc.key}
                variant="outline"
                className={`h-auto py-3 px-4 flex flex-col items-center gap-1 border-${noc.color}-300 hover:bg-${noc.color}-50`}
                onClick={() => onGenerateNoc(noc.key, noc.label)}
                disabled={generatingNoc === noc.key}
                data-testid={`generate-${noc.key}-btn`}
              >
                {generatingNoc === noc.key ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Building2 className="w-5 h-5" />
                )}
                <span className="font-medium text-sm">{noc.label}</span>
                <span className="text-xs text-slate-500">Generate NOC</span>
              </Button>
            ))}
          </div>

          {nocDocuments.length > 0 && (
            <div>
              <p className="text-sm font-medium text-slate-700 mb-3">Generated NOC Documents</p>
              <div className="space-y-3">
                {nocDocuments.map((doc) => (
                  <div key={doc.id} className="flex items-center justify-between p-3 border rounded-lg bg-slate-50">
                    <div className="flex items-center gap-3">
                      <FileText className="w-6 h-6 text-primary" />
                      <div>
                        <p className="font-medium text-sm">{getNocLabel(doc.doc_type)}</p>
                        <p className="text-xs text-slate-500">
                          Generated: {new Date(doc.generated_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getStatusBadge(doc.status)}>{doc.status}</Badge>
                      <Button variant="outline" size="sm" onClick={() => onPreviewDocument(doc)} data-testid={`preview-noc-${doc.id}`}>
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => onDownloadDocument(doc)} data-testid={`download-noc-${doc.id}`}>
                        <Download className="w-4 h-4" />
                      </Button>
                      {!isAccountsRole && (
                        <Button
                          variant="outline"
                          size="sm"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          onClick={() => onDeleteDocument(doc, "generated")}
                          data-testid={`delete-noc-${doc.id}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </>
  );
};

export default DocumentsTab;
