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
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CustomerDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [customer, setCustomer] = useState(null);
  const [paymentSchedule, setPaymentSchedule] = useState({ items: [] });
  const [checklist, setChecklist] = useState({ items: {} });
  const [documents, setDocuments] = useState([]);
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

  useEffect(() => {
    fetchCustomerData();
  }, [id]);

  const fetchCustomerData = async () => {
    try {
      const [customerRes, scheduleRes, checklistRes, docsRes, commsRes] = await Promise.all([
        axios.get(`${API}/customers/${id}`),
        axios.get(`${API}/payments/schedule/${id}`),
        axios.get(`${API}/checklist/${id}`),
        axios.get(`${API}/documents/${id}`),
        axios.get(`${API}/communication/${id}`),
      ]);
      setCustomer(customerRes.data);
      setEditData(customerRes.data);
      setPaymentSchedule(scheduleRes.data);
      setChecklist(checklistRes.data);
      setDocuments(docsRes.data);
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
        <div className="flex gap-2">
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
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
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
            <p className="text-sm text-slate-500">Agreement</p>
            <Badge className={getStatusBadge(customer.agreement_status)}>{customer.agreement_status}</Badge>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="details" className="space-y-4">
        <TabsList>
          <TabsTrigger value="details" data-testid="tab-details">
            <User className="w-4 h-4 mr-2" />
            Details
          </TabsTrigger>
          <TabsTrigger value="payments" data-testid="tab-payments">
            <CreditCard className="w-4 h-4 mr-2" />
            Payments
          </TabsTrigger>
          <TabsTrigger value="documents" data-testid="tab-documents">
            <FileText className="w-4 h-4 mr-2" />
            Documents
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
          <Card>
            <CardHeader>
              <CardTitle>Customer Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <Label>Full Name</Label>
                    {editing ? (
                      <Input
                        value={editData.name}
                        onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                      />
                    ) : (
                      <p className="text-slate-700">{customer.name}</p>
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
                      <p className="text-slate-700">{customer.email}</p>
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
                      <p className="text-slate-700">{customer.phone}</p>
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
                      <p className="text-slate-700">{customer.father_name || "-"}</p>
                    )}
                  </div>
                  <div>
                    <Label>PAN Number</Label>
                    {editing ? (
                      <Input
                        value={editData.pan_number || ""}
                        onChange={(e) => setEditData({ ...editData, pan_number: e.target.value })}
                      />
                    ) : (
                      <p className="text-slate-700">{customer.pan_number || "-"}</p>
                    )}
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <Label>Project</Label>
                    <p className="text-slate-700">{customer.project}</p>
                  </div>
                  <div>
                    <Label>Tower</Label>
                    <p className="text-slate-700">{customer.tower}</p>
                  </div>
                  <div>
                    <Label>Unit Number</Label>
                    <p className="text-slate-700">{customer.unit_number}</p>
                  </div>
                  <div>
                    <Label>Carpet Area</Label>
                    {editing ? (
                      <Input
                        type="number"
                        value={editData.carpet_area}
                        onChange={(e) => setEditData({ ...editData, carpet_area: parseFloat(e.target.value) })}
                      />
                    ) : (
                      <p className="text-slate-700">{customer.carpet_area} sq.ft</p>
                    )}
                  </div>
                  <div>
                    <Label>Saleable Area</Label>
                    {editing ? (
                      <Input
                        type="number"
                        value={editData.saleable_area}
                        onChange={(e) => setEditData({ ...editData, saleable_area: parseFloat(e.target.value) })}
                      />
                    ) : (
                      <p className="text-slate-700">{customer.saleable_area} sq.ft</p>
                    )}
                  </div>
                  <div>
                    <Label>Parking</Label>
                    {editing ? (
                      <Input
                        value={editData.parking || ""}
                        onChange={(e) => setEditData({ ...editData, parking: e.target.value })}
                      />
                    ) : (
                      <p className="text-slate-700">{customer.parking || "-"}</p>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Payments Tab */}
        <TabsContent value="payments">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Payment Schedule</CardTitle>
                <CardDescription>Track all payment milestones</CardDescription>
              </div>
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
                        data-testid="payment-name-input"
                      />
                    </div>
                    <div>
                      <Label>Milestone</Label>
                      <Select
                        value={newPayment.milestone}
                        onValueChange={(value) => setNewPayment({ ...newPayment, milestone: value })}
                      >
                        <SelectTrigger data-testid="payment-milestone-select">
                          <SelectValue placeholder="Select milestone" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="booking">Booking Amount</SelectItem>
                          <SelectItem value="agreement">Agreement Stage</SelectItem>
                          <SelectItem value="plinth">Plinth Completion</SelectItem>
                          <SelectItem value="slab">Slab Completion</SelectItem>
                          <SelectItem value="possession">Final Possession</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Amount (₹) *</Label>
                      <Input
                        type="number"
                        value={newPayment.amount}
                        onChange={(e) => setNewPayment({ ...newPayment, amount: e.target.value })}
                        data-testid="payment-amount-input"
                      />
                    </div>
                    <div>
                      <Label>Due Date *</Label>
                      <Input
                        type="date"
                        value={newPayment.due_date}
                        onChange={(e) => setNewPayment({ ...newPayment, due_date: e.target.value })}
                        data-testid="payment-date-input"
                      />
                    </div>
                    <Button onClick={handleAddPayment} className="w-full" data-testid="save-payment-btn">
                      Add Payment
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
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
                  <p className="text-sm">Add payment milestones to track</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Documents Tab */}
        <TabsContent value="documents">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Generated Documents</CardTitle>
                <CardDescription>Sales agreements, allotment letters, and more</CardDescription>
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
                        <SelectTrigger data-testid="doc-type-select">
                          <SelectValue placeholder="Select document type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="sales_agreement">Sales Agreement</SelectItem>
                          <SelectItem value="allotment_letter">Allotment Letter</SelectItem>
                          <SelectItem value="disbursement_letter">Disbursement Letter</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <Button onClick={handleGenerateDocument} className="w-full" data-testid="confirm-generate-btn">
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
                          <p className="font-medium capitalize">{doc.doc_type.replace("_", " ")}</p>
                          <p className="text-sm text-slate-500">
                            Generated: {new Date(doc.generated_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getStatusBadge(doc.status)}>{doc.status}</Badge>
                        <Button variant="outline" size="sm">
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

        {/* Communication Tab */}
        <TabsContent value="communication">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Communication History</CardTitle>
                <CardDescription>Emails and WhatsApp messages</CardDescription>
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
                          data-testid="email-subject-input"
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
                        data-testid="message-input"
                      />
                    </div>
                    <p className="text-xs text-amber-600 bg-amber-50 p-2 rounded">
                      Note: Messages are MOCKED. Configure SendGrid/Twilio for production.
                    </p>
                    <Button onClick={handleSendCommunication} className="w-full" data-testid="confirm-send-btn">
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
                      <p className="text-sm text-slate-600 whitespace-pre-wrap">{comm.content}</p>
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
                      data-testid={`checklist-${key}`}
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
    </div>
  );
};

export default CustomerDetailPage;
