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
import { Plus, FileText, Eye, Download, Trash2, Loader2, Building2 } from "lucide-react";
import { getStatusBadge } from "./utils";

const NOC_TYPES = [
  { key: "noc_hdfc", label: "HDFC Bank", color: "red" },
  { key: "noc_bob", label: "Bank of Baroda", color: "orange" },
  { key: "noc_tata", label: "TATA Capital", color: "blue" },
];

const DocumentsTab = ({
  documents,
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

  const nocDocuments = documents.filter(doc =>
    ["noc_hdfc", "noc_bob", "noc_tata"].includes(doc.doc_type)
  );

  const getNocLabel = (type) => {
    const labels = { noc_hdfc: "HDFC Bank NOC", noc_bob: "Bank of Baroda NOC", noc_tata: "TATA Capital NOC" };
    return labels[type] || type;
  };

  return (
    <>
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
                      <SelectItem value="disbursement_letter">Disbursement Letter</SelectItem>
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
          {documents.length > 0 ? (
            <div className="space-y-4">
              {documents.map((doc) => (
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

      {/* Disbursement - Bank NOC Documents */}
      <Card className="mt-6">
        <CardHeader>
          <div>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="w-5 h-5 text-amber-600" />
              Disbursement Documents
            </CardTitle>
            <CardDescription>Generate Bank NOC (No Objection Certificate) for loan disbursement</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {NOC_TYPES.map(({ key, label, color }) => (
              <div key={key} className="p-4 border rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors">
                <div className="flex flex-col items-center text-center gap-3">
                  <div className={`w-12 h-12 rounded-full bg-${color}-100 flex items-center justify-center`}>
                    <Building2 className={`w-6 h-6 text-${color}-600`} />
                  </div>
                  <div>
                    <p className="font-semibold text-slate-800">{label}</p>
                    <p className="text-xs text-slate-500">No Objection Certificate</p>
                  </div>
                  <Button
                    onClick={() => onGenerateNoc(key, label)}
                    disabled={generatingNoc === key}
                    className={`w-full bg-${color}-600 hover:bg-${color}-700`}
                    size="sm"
                    data-testid={`generate-${key.replace("_", "-")}`}
                  >
                    {generatingNoc === key ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <FileText className="w-4 h-4 mr-2" />
                        Generate NOC
                      </>
                    )}
                  </Button>
                </div>
              </div>
            ))}
          </div>

          {nocDocuments.length > 0 && (
            <div className="mt-6 pt-6 border-t">
              <h4 className="text-sm font-medium text-slate-700 mb-3">Generated NOC Documents</h4>
              <div className="space-y-3">
                {nocDocuments.map((doc) => (
                  <div key={doc.id} className="flex items-center justify-between p-3 border rounded-lg bg-white">
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
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onPreviewDocument(doc)}
                        data-testid={`preview-noc-${doc.id}`}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onDownloadDocument(doc)}
                        data-testid={`download-noc-${doc.id}`}
                      >
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
