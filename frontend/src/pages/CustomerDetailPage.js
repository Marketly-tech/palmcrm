import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Checkbox } from "../components/ui/checkbox";
import { Textarea } from "../components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../components/ui/dialog";
import { toast } from "sonner";
import {
  ArrowLeft,
  User,
  Building2,
  CreditCard,
  FileText,
  MessageSquare,
  CheckCircle,
  Plus,
  Loader2,
  Mail,
  Phone,
  Send,
  Download,
  Edit,
  Save,
  Eye,
  Upload,
  Trash2,
  Calculator,
  RefreshCw,
} from "lucide-react";
import { Separator } from "../components/ui/separator";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CustomerDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [customer, setCustomer] = useState(null);
  const [paymentSchedule, setPaymentSchedule] = useState({ items: [] });
  const [checklist, setChecklist] = useState({ items: {} });
  const [documents, setDocuments] = useState([]);
  const [uploadedDocs, setUploadedDocs] = useState([]);
  const [communications, setCommunications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editData, setEditData] = useState({});
  const [saving, setSaving] = useState(false);

  // Payment Dialog
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false);
  const [newPayment, setNewPayment] = useState({
    installment_name: "",
    milestone: "",
    amount: "",
    due_date: "",
  });

  // Communication Dialog
  const [commDialogOpen, setCommDialogOpen] = useState(false);
  const [commType, setCommType] = useState("email");
  const [commMessage, setCommMessage] = useState("");
  const [commSubject, setCommSubject] = useState("");

  // Document Generation
  const [docDialogOpen, setDocDialogOpen] = useState(false);
  const [docType, setDocType] = useState("");
  
  // Document Preview
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);
  const [previewContent, setPreviewContent] = useState(null);
  
  // Welcome Email
  const [sendingWelcome, setSendingWelcome] = useState(false);
  
  // File Upload
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploadDocType, setUploadDocType] = useState("");
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchCustomerData();
  }, [id]);

  const fetchCustomerData = async () => {
    try {
      const [customerRes, scheduleRes, checklistRes, docsRes, commsRes, uploadedDocsRes] = await Promise.all([
        axios.get(`${API}/customers/${id}`),
        axios.get(`${API}/payments/schedule/${id}`),
        axios.get(`${API}/checklist/${id}`),
        axios.get(`${API}/documents/${id}`),
        axios.get(`${API}/communication/${id}`),
        axios.get(`${API}/customers/${id}/documents-list`).catch(() => ({ data: [] })),
      ]);
      setCustomer(customerRes.data);
      setEditData(customerRes.data);
      setPaymentSchedule(scheduleRes.data);
      setChecklist(checklistRes.data);
      setDocuments(docsRes.data);
      setUploadedDocs(uploadedDocsRes.data);
      setCommunications(commsRes.data);
    } catch (error) {
      toast.error("Failed to fetch customer data");
      navigate("/customers");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveCustomer = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/customers/${id}`, editData);
      setCustomer(editData);
      setEditing(false);
      toast.success("Customer updated successfully");
    } catch (error) {
      toast.error("Failed to update customer");
    } finally {
      setSaving(false);
    }
  };

  const handleAddPayment = async () => {
    if (!newPayment.installment_name || !newPayment.amount || !newPayment.due_date) {
      toast.error("Please fill all required fields");
      return;
    }

    const items = [
      ...paymentSchedule.items,
      {
        ...newPayment,
        id: Date.now().toString(),
        amount: parseFloat(newPayment.amount),
        payment_status: "pending",
      },
    ];

    try {
      await axios.post(`${API}/payments/schedule`, { customer_id: id, items });
      setPaymentSchedule({ ...paymentSchedule, items });
      setPaymentDialogOpen(false);
      setNewPayment({ installment_name: "", milestone: "", amount: "", due_date: "" });
      toast.success("Payment schedule updated");
    } catch (error) {
      toast.error("Failed to add payment");
    }
  };

  const handleGeneratePaymentSchedule = async () => {
    try {
      await axios.post(`${API}/calculator/generate-schedule/${id}`);
      fetchCustomerData();
      toast.success("Payment schedule generated from template");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to generate schedule");
    }
  };

  const handleUpdatePaymentStatus = async (itemId, status) => {
    try {
      await axios.put(`${API}/payments/item/${id}/${itemId}`, {
        payment_status: status,
        payment_date: status === "paid" ? new Date().toISOString().split("T")[0] : null,
      });
      fetchCustomerData();
      toast.success("Payment status updated");
    } catch (error) {
      toast.error("Failed to update payment");
    }
  };

  const handleUpdateChecklist = async (key, value) => {
    const newItems = { ...checklist.items, [key]: value };
    try {
      await axios.put(`${API}/checklist/${id}`, newItems);
      setChecklist({ ...checklist, items: newItems });
    } catch (error) {
      toast.error("Failed to update checklist");
    }
  };

  const handleGenerateDocument = async () => {
    if (!docType) {
      toast.error("Please select a document type");
      return;
    }

    try {
      const response = await axios.post(`${API}/documents/generate`, {
        customer_id: id,
        doc_type: docType,
      });
      setDocuments([...documents, response.data.document]);
      setDocDialogOpen(false);
      setDocType("");
      toast.success("Document generated successfully");
    } catch (error) {
      toast.error("Failed to generate document");
    }
  };

  const handlePreviewDocument = async (doc) => {
    try {
      const response = await axios.get(`${API}/documents/html/${doc.id}`);
      setPreviewContent(response.data.content);
      setPreviewDialogOpen(true);
    } catch (error) {
      toast.error("Failed to load document preview");
    }
  };

  const handleDownloadDocument = async (doc) => {
    try {
      const response = await axios.get(`${API}/documents/html/${doc.id}`);
      // Open in new window for printing/saving as PDF
      const printWindow = window.open("", "_blank");
      if (printWindow) {
        printWindow.document.write(response.data.content);
        printWindow.document.close();
      }
    } catch (error) {
      toast.error("Failed to download document");
    }
  };

  const handleSendWelcomeEmail = async () => {
    setSendingWelcome(true);
    try {
      const response = await axios.post(`${API}/communication/send-welcome-email/${id}`);
      toast.success(`Welcome email sent to ${customer.email} (MOCKED)`);
      
      // Open welcome email preview in new window
      if (response.data.welcome_html) {
        const previewWindow = window.open("", "_blank");
        if (previewWindow) {
          previewWindow.document.write(response.data.welcome_html);
          previewWindow.document.close();
        }
      }
      
      fetchCustomerData();
    } catch (error) {
      toast.error("Failed to send welcome email");
    } finally {
      setSendingWelcome(false);
    }
  };

  const handleGeneratePriceBreakup = async () => {
    try {
      const response = await axios.post(`${API}/documents/generate-pdf/${id}`);
      toast.success("Price breakup generated");
      
      // Open in new window
      if (response.data.html_content) {
        const printWindow = window.open("", "_blank");
        if (printWindow) {
          printWindow.document.write(response.data.html_content);
          printWindow.document.close();
        }
      }
      
      fetchCustomerData();
    } catch (error) {
      toast.error("Failed to generate price breakup");
    }
  };

  const handleSendCommunication = async () => {
    if (!commMessage) {
      toast.error("Please enter a message");
      return;
    }

    try {
      if (commType === "email") {
        await axios.post(`${API}/communication/email?customer_id=${id}&subject=${encodeURIComponent(commSubject)}&message=${encodeURIComponent(commMessage)}`);
      } else {
        await axios.post(`${API}/communication/whatsapp?customer_id=${id}&message=${encodeURIComponent(commMessage)}`);
      }
      fetchCustomerData();
      setCommDialogOpen(false);
      setCommMessage("");
      setCommSubject("");
      toast.success(`${commType === "email" ? "Email" : "WhatsApp"} sent (MOCKED)`);
    } catch (error) {
      toast.error("Failed to send message");
    }
  };

  const handleFileUpload = async () => {
    if (!uploadFile || !uploadDocType) {
      toast.error("Please select a file and document type");
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", uploadFile);
      formData.append("doc_type", uploadDocType);

      await axios.post(`${API}/customers/${id}/upload-document`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      toast.success("Document uploaded successfully");
      setUploadDialogOpen(false);
      setUploadFile(null);
      setUploadDocType("");
      fetchCustomerData();
    } catch (error) {
      toast.error("Failed to upload document");
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadUploadedDoc = async (doc) => {
    try {
      const response = await axios.get(`${API}/documents/download/${doc.id}`, {
        responseType: "blob",
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", doc.filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      toast.error("Failed to download document");
    }
  };

  const handlePreviewUploadedDoc = async (doc) => {
    try {
      const response = await axios.get(`${API}/documents/preview/${doc.id}`);
      const { content_base64, content_type, filename } = response.data;
      
      // Create data URL and open in new window
      const dataUrl = `data:${content_type};base64,${content_base64}`;
      
      if (content_type.startsWith("image/")) {
        // For images, show in dialog
        setPreviewContent(`<img src="${dataUrl}" style="max-width: 100%; height: auto;" alt="${filename}" />`);
        setPreviewDialogOpen(true);
      } else if (content_type === "application/pdf") {
        // For PDFs, open in new tab
        const pdfWindow = window.open("", "_blank");
        if (pdfWindow) {
          pdfWindow.document.write(`<iframe src="${dataUrl}" style="width:100%;height:100%;border:none;"></iframe>`);
        }
      } else {
        // For other types, trigger download
        handleDownloadUploadedDoc(doc);
      }
    } catch (error) {
      toast.error("Failed to preview document");
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount || 0);
  };

  const getStatusBadge = (status) => {
    const styles = {
      pending: "bg-yellow-100 text-yellow-700",
      paid: "bg-green-100 text-green-700",
      overdue: "bg-red-100 text-red-700",
      partial: "bg-blue-100 text-blue-700",
      draft: "bg-slate-100 text-slate-700",
      sent: "bg-blue-100 text-blue-700",
      signed: "bg-green-100 text-green-700",
      completed: "bg-purple-100 text-purple-700",
      pending_approval: "bg-yellow-100 text-yellow-700",
      qualified: "bg-green-100 text-green-700",
    };
    return styles[status] || "bg-slate-100 text-slate-700";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!customer) return null;

  return (
    <div className="space-y-6" data-testid="customer-detail-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate("/customers")} data-testid="back-btn">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="font-heading text-2xl font-bold text-slate-900">{customer.name}</h1>
            <p className="text-slate-500 font-mono">{customer.customer_id}</p>
          </div>
        </div>
        <div className="flex gap-2 flex-wrap">
          <Button
            variant="outline"
            onClick={handleSendWelcomeEmail}
            disabled={sendingWelcome}
            data-testid="send-welcome-btn"
          >
            {sendingWelcome ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Mail className="w-4 h-4 mr-2" />
            )}
            Send Welcome Email
          </Button>
          <Button
            variant="outline"
            onClick={handleGeneratePriceBreakup}
            data-testid="generate-price-breakup-btn"
          >
            <FileText className="w-4 h-4 mr-2" />
            Price Breakup PDF
          </Button>
          {editing ? (
            <>
              <Button variant="outline" onClick={() => setEditing(false)}>
                Cancel
              </Button>
              <Button onClick={handleSaveCustomer} disabled={saving} data-testid="save-customer-btn">
                {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Save
              </Button>
            </>
          ) : (
            <Button variant="outline" onClick={() => setEditing(true)} data-testid="edit-customer-btn">
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </Button>
          )}
        </div>
      </div>

      {/* Quick Info */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-slate-500">Project</p>
            <p className="font-semibold">{customer.project}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-slate-500">Unit</p>
            <p className="font-semibold font-mono">{customer.tower}-{customer.unit_number}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-slate-500">Total Value</p>
            <p className="font-semibold text-primary">{formatCurrency(customer.total_price)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-slate-500">Stage</p>
            <Badge className={getStatusBadge(customer.stage)}>{customer.stage?.replace("_", " ")}</Badge>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-slate-500">Received</p>
            <p className="font-semibold text-green-600">{customer.payment_received_percentage?.toFixed(1) || 0}%</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="details" className="space-y-4">
        <TabsList className="flex flex-wrap">
          <TabsTrigger value="details" data-testid="tab-details">
            <User className="w-4 h-4 mr-2" />
            Details
          </TabsTrigger>
          <TabsTrigger value="calculator" data-testid="tab-calculator">
            <Calculator className="w-4 h-4 mr-2" />
            Calculator
          </TabsTrigger>
          <TabsTrigger value="payments" data-testid="tab-payments">
            <CreditCard className="w-4 h-4 mr-2" />
            Payments
          </TabsTrigger>
          <TabsTrigger value="documents" data-testid="tab-documents">
            <FileText className="w-4 h-4 mr-2" />
            Documents
          </TabsTrigger>
          <TabsTrigger value="uploads" data-testid="tab-uploads">
            <Upload className="w-4 h-4 mr-2" />
            Uploads
          </TabsTrigger>
          <TabsTrigger value="communication" data-testid="tab-communication">
            <MessageSquare className="w-4 h-4 mr-2" />
            Communication
          </TabsTrigger>
          <TabsTrigger value="checklist" data-testid="tab-checklist">
            <CheckCircle className="w-4 h-4 mr-2" />
            Checklist
          </TabsTrigger>
        </TabsList>

        {/* Details Tab */}
        <TabsContent value="details">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Personal Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Full Name</Label>
                      {editing ? (
                        <Input
                          value={editData.name}
                          onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                        />
                      ) : (
                        <p className="text-slate-700 mt-1">{customer.name}</p>
                      )}
                    </div>
                    <div>
                      <Label>Phone</Label>
                      {editing ? (
                        <Input
                          value={editData.phone}
                          onChange={(e) => setEditData({ ...editData, phone: e.target.value })}
                        />
                      ) : (
                        <p className="text-slate-700 mt-1">{customer.phone}</p>
                      )}
                    </div>
                    <div>
                      <Label>Email</Label>
                      {editing ? (
                        <Input
                          value={editData.email}
                          onChange={(e) => setEditData({ ...editData, email: e.target.value })}
                        />
                      ) : (
                        <p className="text-slate-700 mt-1">{customer.email}</p>
                      )}
                    </div>
                    <div>
                      <Label>Father's Name</Label>
                      {editing ? (
                        <Input
                          value={editData.father_name || ""}
                          onChange={(e) => setEditData({ ...editData, father_name: e.target.value })}
                        />
                      ) : (
                        <p className="text-slate-700 mt-1">{customer.father_name || "-"}</p>
                      )}
                    </div>
                    <div>
                      <Label>PAN Number</Label>
                      <p className="text-slate-700 mt-1">{customer.pan_number || "-"}</p>
                    </div>
                    <div>
                      <Label>Aadhaar</Label>
                      <p className="text-slate-700 mt-1">{customer.aadhar_number || "-"}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Property & Pricing</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>BHK Type</Label>
                      {editing ? (
                        <Select
                          value={editData.bhk_type || ""}
                          onValueChange={(value) => setEditData({ ...editData, bhk_type: value })}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select BHK" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="2BHK">2 BHK</SelectItem>
                            <SelectItem value="2.5BHK">2.5 BHK</SelectItem>
                            <SelectItem value="3BHK">3 BHK</SelectItem>
                            <SelectItem value="3.5BHK">3.5 BHK</SelectItem>
                            <SelectItem value="4BHK">4 BHK</SelectItem>
                          </SelectContent>
                        </Select>
                      ) : (
                        <p className="text-slate-700 mt-1">{customer.bhk_type || "-"}</p>
                      )}
                    </div>
                    <div>
                      <Label>Floor</Label>
                      {editing ? (
                        <Input
                          type="number"
                          value={editData.floor || ""}
                          onChange={(e) => setEditData({ ...editData, floor: parseInt(e.target.value) || 0 })}
                          placeholder="Floor number"
                        />
                      ) : (
                        <p className="text-slate-700 mt-1">{customer.floor || "0"}</p>
                      )}
                    </div>
                    <div>
                      <Label>Carpet Area (sq.ft)</Label>
                      {editing ? (
                        <Input
                          type="number"
                          value={editData.carpet_area || ""}
                          onChange={(e) => setEditData({ ...editData, carpet_area: parseFloat(e.target.value) || 0 })}
                        />
                      ) : (
                        <p className="text-slate-700 mt-1">{customer.carpet_area || 0} sq.ft</p>
                      )}
                    </div>
                    <div>
                      <Label>Saleable Area (sq.ft)</Label>
                      {editing ? (
                        <Input
                          type="number"
                          value={editData.saleable_area || ""}
                          onChange={(e) => setEditData({ ...editData, saleable_area: parseFloat(e.target.value) || 0 })}
                        />
                      ) : (
                        <p className="text-slate-700 mt-1">{customer.saleable_area || 0} sq.ft</p>
                      )}
                    </div>
                    <div>
                      <Label>Rate/Sq.ft (₹)</Label>
                      {editing ? (
                        <>
                          <Input
                            type="number"
                            value={editData.rate_per_sqft || ""}
                            onChange={(e) => setEditData({ ...editData, rate_per_sqft: parseFloat(e.target.value) || 0 })}
                          />
                          <p className="text-xs text-slate-500 mt-1">Floor rise: ₹50/sqft per floor</p>
                        </>
                      ) : (
                        <p className="text-slate-700 mt-1">₹{customer.rate_per_sqft?.toLocaleString() || 0}</p>
                      )}
                    </div>
                    <div>
                      <Label>Additional Parking</Label>
                      {editing ? (
                        <Input
                          type="number"
                          min="0"
                          value={editData.additional_parking || "0"}
                          onChange={(e) => setEditData({ ...editData, additional_parking: parseInt(e.target.value) || 0 })}
                        />
                      ) : (
                        <p className="text-slate-700 mt-1">{customer.additional_parking || 0}</p>
                      )}
                    </div>
                    <div>
                      <Label>Base Price</Label>
                      <p className="text-slate-700 mt-1">{formatCurrency(customer.base_price)}</p>
                    </div>
                    <div>
                      <Label>Club House</Label>
                      <p className="text-slate-700 mt-1">{formatCurrency(customer.club_house_charges)}</p>
                    </div>
                    <div>
                      <Label>Labour Cess (0.70%)</Label>
                      <p className="text-slate-700 mt-1">{formatCurrency(customer.labour_cess)}</p>
                    </div>
                    <div>
                      <Label>GST (5%)</Label>
                      <p className="text-slate-700 mt-1">{formatCurrency(customer.gst_amount)}</p>
                    </div>
                    <div>
                      <Label>Total Price</Label>
                      <p className="text-primary font-bold mt-1">{formatCurrency(customer.total_price)}</p>
                    </div>
                    <div>
                      <Label>UDS</Label>
                      <p className="text-slate-700 mt-1">{customer.uds || "-"}</p>
                    </div>
                  </div>
                  {editing && (
                    <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                      <p className="text-sm text-amber-700">
                        <strong>Note:</strong> After saving, use the "Recalculate Price" button to update the total based on new values.
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Finance Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Finance Type</Label>
                    <p className="text-slate-700 mt-1 capitalize">{customer.finance_type || "Self"}</p>
                  </div>
                  <div>
                    <Label>Bank</Label>
                    <p className="text-slate-700 mt-1">{customer.finance_bank || "-"}</p>
                  </div>
                  <div>
                    <Label>Booking Amount</Label>
                    <p className="text-slate-700 mt-1">{formatCurrency(customer.booking_amount)}</p>
                  </div>
                  <div>
                    <Label>Total Received</Label>
                    <p className="text-green-600 font-semibold mt-1">{formatCurrency(customer.total_received)}</p>
                  </div>
                  <div>
                    <Label>Balance</Label>
                    <p className="text-red-600 font-semibold mt-1">{formatCurrency(customer.balance_amount)}</p>
                  </div>
                  <div>
                    <Label>Booking Date</Label>
                    <p className="text-slate-700 mt-1">{customer.booking_date || "-"}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {customer.co_applicant_name && (
              <Card>
                <CardHeader>
                  <CardTitle>Co-Applicant Details</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Name</Label>
                      <p className="text-slate-700 mt-1">{customer.co_applicant_name}</p>
                    </div>
                    <div>
                      <Label>Phone</Label>
                      <p className="text-slate-700 mt-1">{customer.co_applicant_phone || "-"}</p>
                    </div>
                    <div>
                      <Label>PAN</Label>
                      <p className="text-slate-700 mt-1">{customer.co_applicant_pan || "-"}</p>
                    </div>
                    <div>
                      <Label>Aadhaar</Label>
                      <p className="text-slate-700 mt-1">{customer.co_applicant_aadhar || "-"}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Calculator Tab */}
        <TabsContent value="calculator">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Price Calculator */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calculator className="w-5 h-5 text-primary" />
                  Price Breakup Calculator
                </CardTitle>
                <CardDescription>
                  Recalculate price based on updated values
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Saleable Area (sq.ft)</Label>
                    <Input
                      type="number"
                      value={customer.saleable_area || 0}
                      readOnly
                      className="bg-slate-50"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Rate/Sq.ft (₹)</Label>
                    <Input
                      type="number"
                      value={customer.rate_per_sqft || 0}
                      readOnly
                      className="bg-slate-50"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Floor Number</Label>
                    <Input
                      type="number"
                      value={customer.floor || 0}
                      readOnly
                      className="bg-slate-50"
                    />
                    <p className="text-xs text-slate-500">Floor rise: ₹{(customer.floor || 0) * 50}/sqft</p>
                  </div>
                  <div className="space-y-2">
                    <Label>Additional Parking</Label>
                    <Input
                      type="number"
                      value={customer.additional_parking || 0}
                      readOnly
                      className="bg-slate-50"
                    />
                  </div>
                </div>

                <Separator />

                <div className="space-y-3 p-4 bg-slate-50 rounded-lg">
                  <div className="flex justify-between">
                    <span className="text-slate-600">Base Price ({customer.saleable_area || 0} × ₹{((customer.rate_per_sqft || 0) + ((customer.floor || 0) * 50))})</span>
                    <span className="font-semibold">{formatCurrency(customer.base_price)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Club House & Infrastructure</span>
                    <span className="font-semibold">{formatCurrency(customer.club_house_charges || 200000)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Additional Parking ({customer.additional_parking || 0} × ₹3L)</span>
                    <span className="font-semibold">{formatCurrency(customer.additional_parking_charges || 0)}</span>
                  </div>
                  <Separator />
                  <div className="flex justify-between">
                    <span className="text-slate-600">Labour Cess (0.70%)</span>
                    <span className="font-semibold">{formatCurrency(customer.labour_cess)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">GST (5%)</span>
                    <span className="font-semibold">{formatCurrency(customer.gst_amount)}</span>
                  </div>
                  <Separator />
                  <div className="flex justify-between text-lg">
                    <span className="font-semibold text-primary">Total Flat Value</span>
                    <span className="font-bold text-primary">{formatCurrency(customer.total_price)}</span>
                  </div>
                </div>

                <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                  <span className="text-slate-600">UDS (Undivided Share)</span>
                  <span className="font-semibold">{customer.uds || (customer.saleable_area * 0.495046).toFixed(2)}</span>
                </div>

                <Button 
                  className="w-full" 
                  onClick={async () => {
                    try {
                      // Recalculate and update
                      const floor = customer.floor || 0;
                      const floorRise = floor * 50;
                      const effectiveRate = (customer.rate_per_sqft || 0) + floorRise;
                      const basePrice = effectiveRate * (customer.saleable_area || 0);
                      const clubHouse = 200000;
                      const parkingCharges = (customer.additional_parking || 0) * 300000;
                      const subtotal = basePrice + clubHouse + parkingCharges;
                      const labourCess = subtotal * 0.007;
                      const gst = subtotal * 0.05;
                      const total = subtotal + labourCess + gst;
                      const uds = (customer.saleable_area || 0) * 0.495046;
                      
                      const updates = {
                        base_price: Math.round(basePrice),
                        club_house_charges: clubHouse,
                        additional_parking_charges: parkingCharges,
                        labour_cess: Math.round(labourCess),
                        gst_amount: Math.round(gst),
                        total_price: Math.round(total),
                        uds: Math.round(uds * 100) / 100,
                        balance_amount: Math.round(total - (customer.total_received || 0)),
                        payment_received_percentage: total > 0 ? Math.round(((customer.total_received || 0) / total) * 10000) / 100 : 0,
                        payment_pending_percentage: total > 0 ? Math.round((1 - (customer.total_received || 0) / total) * 10000) / 100 : 100,
                      };
                      
                      await axios.put(`${API}/customers/${id}`, updates);
                      fetchCustomerData();
                      toast.success("Price recalculated and saved!");
                    } catch (error) {
                      toast.error("Failed to recalculate price");
                    }
                  }}
                  data-testid="recalculate-price-btn"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Recalculate & Save Price
                </Button>
              </CardContent>
            </Card>

            {/* Payment Tracking */}
            <Card>
              <CardHeader>
                <CardTitle>Payment Tracking</CardTitle>
                <CardDescription>Track received vs pending payments</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <p className="text-sm text-slate-600">Received</p>
                    <p className="text-2xl font-bold text-green-600">{formatCurrency(customer.total_received)}</p>
                    <p className="text-lg font-semibold text-green-600">{(customer.payment_received_percentage || 0).toFixed(1)}%</p>
                  </div>
                  <div className="text-center p-4 bg-red-50 rounded-lg">
                    <p className="text-sm text-slate-600">Pending</p>
                    <p className="text-2xl font-bold text-red-600">{formatCurrency(customer.balance_amount)}</p>
                    <p className="text-lg font-semibold text-red-600">{(customer.payment_pending_percentage || 100).toFixed(1)}%</p>
                  </div>
                </div>
                
                {/* Progress Bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Payment Progress</span>
                    <span>{(customer.payment_received_percentage || 0).toFixed(1)}%</span>
                  </div>
                  <div className="h-4 bg-slate-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-green-500 transition-all duration-500"
                      style={{ width: `${customer.payment_received_percentage || 0}%` }}
                    />
                  </div>
                </div>

                <Separator />

                {/* Disbursement Calculator */}
                <div className="space-y-3">
                  <h4 className="font-semibold">Quick Disbursement Calculator</h4>
                  <div className="grid grid-cols-3 gap-2 text-sm">
                    <Button variant="outline" size="sm" onClick={() => toast.info(`30% Disbursement: ${formatCurrency(customer.total_price * 0.3)}`)}>
                      30% = {formatCurrency(customer.total_price * 0.3)}
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => toast.info(`50% Disbursement: ${formatCurrency(customer.total_price * 0.5)}`)}>
                      50% = {formatCurrency(customer.total_price * 0.5)}
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => toast.info(`70% Disbursement: ${formatCurrency(customer.total_price * 0.7)}`)}>
                      70% = {formatCurrency(customer.total_price * 0.7)}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Payments Tab */}
        <TabsContent value="payments">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Payment Schedule</CardTitle>
                <CardDescription>Track all payment milestones</CardDescription>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" onClick={handleGeneratePaymentSchedule} data-testid="generate-schedule-btn">
                  Auto-Generate
                </Button>
                <Dialog open={paymentDialogOpen} onOpenChange={setPaymentDialogOpen}>
                  <DialogTrigger asChild>
                    <Button data-testid="add-payment-btn">
                      <Plus className="w-4 h-4 mr-2" />
                      Add Payment
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Add Payment Milestone</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label>Installment Name *</Label>
                        <Input
                          value={newPayment.installment_name}
                          onChange={(e) => setNewPayment({ ...newPayment, installment_name: e.target.value })}
                          placeholder="e.g., Booking Amount"
                        />
                      </div>
                      <div>
                        <Label>Milestone</Label>
                        <Select
                          value={newPayment.milestone}
                          onValueChange={(value) => setNewPayment({ ...newPayment, milestone: value })}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select milestone" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="booking">Booking</SelectItem>
                            <SelectItem value="agreement">Agreement</SelectItem>
                            <SelectItem value="foundation">Foundation</SelectItem>
                            <SelectItem value="slab">Slab Completion</SelectItem>
                            <SelectItem value="handover">Handover</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label>Amount (₹) *</Label>
                        <Input
                          type="number"
                          value={newPayment.amount}
                          onChange={(e) => setNewPayment({ ...newPayment, amount: e.target.value })}
                        />
                      </div>
                      <div>
                        <Label>Due Date *</Label>
                        <Input
                          type="date"
                          value={newPayment.due_date}
                          onChange={(e) => setNewPayment({ ...newPayment, due_date: e.target.value })}
                        />
                      </div>
                      <Button onClick={handleAddPayment} className="w-full">
                        Add Payment
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              {paymentSchedule.items.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Installment</TableHead>
                      <TableHead>Milestone</TableHead>
                      <TableHead>Amount</TableHead>
                      <TableHead>Due Date</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {paymentSchedule.items.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell className="font-medium">{item.installment_name}</TableCell>
                        <TableCell className="capitalize">{item.milestone || "-"}</TableCell>
                        <TableCell>{formatCurrency(item.amount)}</TableCell>
                        <TableCell>{item.due_date}</TableCell>
                        <TableCell>
                          <Badge className={getStatusBadge(item.payment_status)}>{item.payment_status}</Badge>
                        </TableCell>
                        <TableCell>
                          <Select
                            value={item.payment_status}
                            onValueChange={(value) => handleUpdatePaymentStatus(item.id, value)}
                          >
                            <SelectTrigger className="w-28">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="pending">Pending</SelectItem>
                              <SelectItem value="paid">Paid</SelectItem>
                              <SelectItem value="partial">Partial</SelectItem>
                              <SelectItem value="overdue">Overdue</SelectItem>
                            </SelectContent>
                          </Select>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <CreditCard className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                  <p>No payment schedule yet</p>
                  <p className="text-sm mt-1">Click "Auto-Generate" to create from template</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Generated Documents Tab */}
        <TabsContent value="documents">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Generated Documents</CardTitle>
                <CardDescription>Agreements, letters, and PDFs</CardDescription>
              </div>
              <Dialog open={docDialogOpen} onOpenChange={setDocDialogOpen}>
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
                          <SelectItem value="disbursement_letter">Disbursement Letter</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <Button onClick={handleGenerateDocument} className="w-full">
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
                          onClick={() => handlePreviewDocument(doc)}
                          data-testid={`preview-doc-${doc.id}`}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDownloadDocument(doc)}
                          data-testid={`download-doc-${doc.id}`}
                        >
                          <Download className="w-4 h-4" />
                        </Button>
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
        </TabsContent>

        {/* Uploaded Documents Tab */}
        <TabsContent value="uploads">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Uploaded Documents</CardTitle>
                <CardDescription>Customer KYC and other uploaded files</CardDescription>
              </div>
              <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
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
                      <Select value={uploadDocType} onValueChange={setUploadDocType}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="pan_card">PAN Card</SelectItem>
                          <SelectItem value="aadhaar">Aadhaar Card</SelectItem>
                          <SelectItem value="passport">Passport</SelectItem>
                          <SelectItem value="cheque">Cancelled Cheque</SelectItem>
                          <SelectItem value="photo">Passport Photo</SelectItem>
                          <SelectItem value="other">Other</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>File</Label>
                      <Input
                        type="file"
                        onChange={(e) => setUploadFile(e.target.files[0])}
                        accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                      />
                    </div>
                    <Button onClick={handleFileUpload} className="w-full" disabled={uploading}>
                      {uploading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Uploading...
                        </>
                      ) : (
                        "Upload"
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
                        <FileText className="w-8 h-8 text-blue-500" />
                        <div>
                          <p className="font-medium capitalize">{doc.doc_type.replace(/_/g, " ")}</p>
                          <p className="text-sm text-slate-500">{doc.filename}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handlePreviewUploadedDoc(doc)}
                          data-testid={`preview-upload-${doc.id}`}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDownloadUploadedDoc(doc)}
                          data-testid={`download-upload-${doc.id}`}
                        >
                          <Download className="w-4 h-4" />
                        </Button>
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
        </TabsContent>

        {/* Communication Tab */}
        <TabsContent value="communication">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Communication History</CardTitle>
                <CardDescription>Emails and messages</CardDescription>
              </div>
              <Dialog open={commDialogOpen} onOpenChange={setCommDialogOpen}>
                <DialogTrigger asChild>
                  <Button data-testid="send-message-btn">
                    <Send className="w-4 h-4 mr-2" />
                    Send Message
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Send Communication</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div className="flex gap-2">
                      <Button
                        variant={commType === "email" ? "default" : "outline"}
                        onClick={() => setCommType("email")}
                        className="flex-1"
                      >
                        <Mail className="w-4 h-4 mr-2" />
                        Email
                      </Button>
                      <Button
                        variant={commType === "whatsapp" ? "default" : "outline"}
                        onClick={() => setCommType("whatsapp")}
                        className="flex-1"
                      >
                        <Phone className="w-4 h-4 mr-2" />
                        WhatsApp
                      </Button>
                    </div>
                    {commType === "email" && (
                      <div>
                        <Label>Subject</Label>
                        <Input
                          value={commSubject}
                          onChange={(e) => setCommSubject(e.target.value)}
                          placeholder="Email subject"
                        />
                      </div>
                    )}
                    <div>
                      <Label>Message</Label>
                      <Textarea
                        value={commMessage}
                        onChange={(e) => setCommMessage(e.target.value)}
                        placeholder="Type your message..."
                        rows={4}
                      />
                    </div>
                    <p className="text-xs text-amber-600 bg-amber-50 p-2 rounded">
                      Note: Messages are MOCKED. Configure SendGrid for production.
                    </p>
                    <Button onClick={handleSendCommunication} className="w-full">
                      Send
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </CardHeader>
            <CardContent>
              {communications.length > 0 ? (
                <div className="space-y-4">
                  {communications.map((comm) => (
                    <div key={comm.id} className="p-4 border rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        {comm.channel === "email" ? (
                          <Mail className="w-4 h-4 text-blue-500" />
                        ) : (
                          <Phone className="w-4 h-4 text-green-500" />
                        )}
                        <span className="font-medium capitalize">{comm.channel}</span>
                        <span className="text-sm text-slate-500">- {comm.message_type}</span>
                        <Badge variant="outline" className="ml-auto">{comm.status}</Badge>
                      </div>
                      <p className="text-sm text-slate-600 whitespace-pre-wrap line-clamp-3">{comm.content}</p>
                      <p className="text-xs text-slate-400 mt-2">
                        {new Date(comm.sent_at).toLocaleString()}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <MessageSquare className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                  <p>No communication history yet</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Checklist Tab */}
        <TabsContent value="checklist">
          <Card>
            <CardHeader>
              <CardTitle>Document Checklist</CardTitle>
              <CardDescription>Track received documents</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(checklist.items || {}).map(([key, value]) => (
                  <div key={key} className="flex items-center gap-3 p-3 border rounded-lg">
                    <Checkbox
                      id={key}
                      checked={value}
                      onCheckedChange={(checked) => handleUpdateChecklist(key, checked)}
                    />
                    <Label htmlFor={key} className="flex-1 capitalize cursor-pointer">
                      {key.replace(/_/g, " ")}
                    </Label>
                    {value && <CheckCircle className="w-5 h-5 text-green-500" />}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Document Preview Dialog */}
      <Dialog open={previewDialogOpen} onOpenChange={setPreviewDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Document Preview</DialogTitle>
          </DialogHeader>
          <div
            className="mt-4"
            dangerouslySetInnerHTML={{ __html: previewContent || "" }}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CustomerDetailPage;
