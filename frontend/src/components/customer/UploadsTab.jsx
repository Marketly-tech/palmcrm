/**
 * UploadsTab - Uploaded documents management component
 * Displays and manages customer uploaded documents
 */
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
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
import { Plus, Upload, FileText, Download, Trash2, Loader2 } from "lucide-react";
import { formatDate } from "./utils";

const DOCUMENT_TYPES = [
  { value: "aadhar", label: "Aadhaar Card" },
  { value: "pan", label: "PAN Card" },
  { value: "photo", label: "Photo" },
  { value: "bank_statement", label: "Bank Statement" },
  { value: "income_proof", label: "Income Proof" },
  { value: "address_proof", label: "Address Proof" },
  { value: "other", label: "Other Document" },
];

const UploadsTab = ({
  uploadedDocs,
  onUpload,
  onDownload,
  onDelete,
  isAccountsRole = false,
}) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [docType, setDocType] = useState("");
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async () => {
    if (!docType || !file) return;
    setUploading(true);
    try {
      await onUpload(docType, file);
      setDocType("");
      setFile(null);
      setDialogOpen(false);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Uploaded Documents</CardTitle>
          <CardDescription>Customer submitted documents</CardDescription>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid="upload-doc-btn">
              <Upload className="w-4 h-4 mr-2" />
              Upload Document
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Upload Document</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Document Type</Label>
                <Select value={docType} onValueChange={setDocType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select document type" />
                  </SelectTrigger>
                  <SelectContent>
                    {DOCUMENT_TYPES.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Select File</Label>
                <Input
                  type="file"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                />
              </div>
              <Button 
                onClick={handleUpload} 
                className="w-full" 
                disabled={!docType || !file || uploading}
              >
                {uploading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    Upload
                  </>
                )}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </CardHeader>
      <CardContent>
        {uploadedDocs.length > 0 ? (
          <div className="space-y-4">
            {uploadedDocs.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-4">
                  <FileText className="w-8 h-8 text-blue-600" />
                  <div>
                    <p className="font-medium capitalize">{doc.doc_type?.replace(/_/g, " ") || doc.filename}</p>
                    <p className="text-sm text-slate-500">
                      {doc.filename} • {formatDate(doc.uploaded_at)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onDownload(doc)}
                    data-testid={`download-upload-${doc.id}`}
                  >
                    <Download className="w-4 h-4" />
                  </Button>
                  {!isAccountsRole && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      onClick={() => onDelete(doc, 'uploaded')}
                      data-testid={`delete-upload-${doc.id}`}
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
            <Upload className="w-12 h-12 mx-auto mb-4 text-slate-300" />
            <p>No documents uploaded yet</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default UploadsTab;
