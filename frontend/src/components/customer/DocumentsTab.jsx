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
                      <SelectItem value="demand_letter">Demand Letter</SelectItem>
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

    </>
  );
};

export default DocumentsTab;
