import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
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
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../components/ui/alert-dialog";
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
  Paperclip,
  X,
  MessageCircle,
} from "lucide-react";
import { Separator } from "../components/ui/separator";

// Import refactored customer components
import {
  NotesTab,
  UploadsTab,
  CommunicationTab,
  PaymentTrackingCard,
  TransactionsCard,
  formatCurrency as formatCurrencyUtil,
} from "../components/customer";

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
  
  // Auth context for role-based access
  const { user } = useAuth();
  const isAccountsRole = user?.role === 'accounts';
  
  // Live calculated values during editing
  const [liveCalc, setLiveCalc] = useState(null);
  
  // Disbursement Calculator
  const [disbursementPercentage, setDisbursementPercentage] = useState(30);

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
  const [selectedAttachments, setSelectedAttachments] = useState([]);
  const [localAttachment, setLocalAttachment] = useState(null);
  const localFileRef = useRef(null);
  
  // Customer Overdue Info
  const [overdueInfo, setOverdueInfo] = useState(null);
  
  // Customer Notes
  const [notes, setNotes] = useState([]);
  
  // Payment Due Date
  const [editingDueDate, setEditingDueDate] = useState(false);
  const [paymentDueDate, setPaymentDueDate] = useState("");
  
  // Bank Details
  const [bankDetailsEditing, setBankDetailsEditing] = useState(false);
  const [bankDetails, setBankDetails] = useState({
    bank_name: "",
    bank_name_other: "",
    bank_account_number: "",
    bank_ifsc_code: "",
    bank_branch: "",
    bank_account_holder: "",
  });
  
  // Document Delete
  const [docDeleteDialogOpen, setDocDeleteDialogOpen] = useState(false);
  const [docToDelete, setDocToDelete] = useState(null);
  const [docDeleteType, setDocDeleteType] = useState(null); // 'generated' or 'uploaded'
  const [docDeleting, setDocDeleting] = useState(false);

  // Calculator Tab Editing
  const [calcEditing, setCalcEditing] = useState(false);
  const [calcData, setCalcData] = useState({});
  const [calcLivePrice, setCalcLivePrice] = useState(null);
  const [calcSaving, setCalcSaving] = useState(false);

  // Document Generation
  const [docDialogOpen, setDocDialogOpen] = useState(false);
  const [docType, setDocType] = useState("");
  
  // Document Preview
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);
  const [previewContent, setPreviewContent] = useState(null);
  
  // Welcome Email
  const [sendingWelcome, setSendingWelcome] = useState(false);
  const [welcomePreviewOpen, setWelcomePreviewOpen] = useState(false);
  const [welcomePreviewData, setWelcomePreviewData] = useState(null);
  
  // Unified Email Composer
  const [emailComposerOpen, setEmailComposerOpen] = useState(false);
  const [emailComposerData, setEmailComposerData] = useState(null);
  const [editedEmailSubject, setEditedEmailSubject] = useState("");
  const [editedEmailBody, setEditedEmailBody] = useState("");
  const [editedEmailTo, setEditedEmailTo] = useState("");
  const [editedEmailCc, setEditedEmailCc] = useState("");
  const [sendingEmail, setSendingEmail] = useState(false);
  
  // File Upload
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploadDocType, setUploadDocType] = useState("");
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  // Bank NOC Generation
  const [generatingNoc, setGeneratingNoc] = useState(null);

  // Payment Transactions
  const [transactions, setTransactions] = useState([]);
  const [transactionDialogOpen, setTransactionDialogOpen] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState(null);
  const [newTransaction, setNewTransaction] = useState({
    transaction_stage: "",
    transaction_date: "",
    bank_name: "",
    transaction_number: "",
    amount: "",
    notes: ""
  });

  useEffect(() => {
    fetchCustomerData();
  }, [id]);

  const fetchCustomerData = async () => {
    try {
      const [customerRes, scheduleRes, checklistRes, docsRes, commsRes, uploadedDocsRes, transactionsRes, overdueRes, notesRes] = await Promise.all([
        axios.get(`${API}/customers/${id}`),
        axios.get(`${API}/payments/schedule/${id}`),
        axios.get(`${API}/checklist/${id}`),
        axios.get(`${API}/documents/${id}`),
        axios.get(`${API}/communication/${id}`),
        axios.get(`${API}/customers/${id}/documents-list`).catch(() => ({ data: [] })),
        axios.get(`${API}/transactions/${id}`).catch(() => ({ data: [] })),
        axios.get(`${API}/customers/${id}/overdue`).catch(() => ({ data: null })),
        axios.get(`${API}/customers/${id}/notes`).catch(() => ({ data: [] })),
      ]);
      setCustomer(customerRes.data);
      // Initialize editData with floor_rise_cost from custom_fields
      const customerData = customerRes.data;
      setEditData({
        ...customerData,
        floor_rise_cost: customerData.custom_fields?.floor_rise_cost || 0,
      });
      setPaymentSchedule(scheduleRes.data);
      setChecklist(checklistRes.data);
      setDocuments(docsRes.data);
      setUploadedDocs(uploadedDocsRes.data);
      setCommunications(commsRes.data);
      setTransactions(transactionsRes.data || []);
      setOverdueInfo(overdueRes.data);
      setNotes(notesRes.data || []);
      setPaymentDueDate(customerData.payment_due_date || "");
      // Initialize bank details
      setBankDetails({
        bank_name: customerData.bank_name || "",
        bank_name_other: customerData.bank_name_other || "",
        bank_account_number: customerData.bank_account_number || "",
        bank_ifsc_code: customerData.bank_ifsc_code || "",
        bank_branch: customerData.bank_branch || "",
        bank_account_holder: customerData.bank_account_holder || "",
      });
    } catch (error) {
      toast.error("Failed to fetch customer data");
      navigate("/customers");
    } finally {
      setLoading(false);
    }
  };
  
  // Update payment due date
  const handleUpdateDueDate = async () => {
    try {
      await axios.put(`${API}/customers/${id}/payment-due-date`, { payment_due_date: paymentDueDate });
      setCustomer({ ...customer, payment_due_date: paymentDueDate });
      setEditingDueDate(false);
      toast.success("Payment due date updated");
    } catch (error) {
      toast.error("Failed to update due date");
    }
  };
  
  // Save bank details
  const handleSaveBankDetails = async () => {
    try {
      const updateData = {
        bank_name: bankDetails.bank_name,
        bank_name_other: bankDetails.bank_name_other,
        bank_account_number: bankDetails.bank_account_number,
        bank_ifsc_code: bankDetails.bank_ifsc_code,
        bank_branch: bankDetails.bank_branch,
        bank_account_holder: bankDetails.bank_account_holder,
      };
      
      await axios.put(`${API}/customers/${id}`, updateData);
      setCustomer({ ...customer, ...updateData });
      setBankDetailsEditing(false);
      toast.success("Bank details updated successfully");
    } catch (error) {
      toast.error("Failed to update bank details");
    }
  };

  const handleSaveCustomer = async () => {
    setSaving(true);
    try {
      // Include live calculated prices if available
      let dataToSave = { ...editData };
      
      if (liveCalc) {
        dataToSave = {
          ...dataToSave,
          base_price: liveCalc.basePrice,
          club_house_charges: liveCalc.clubHouse,
          additional_charges: liveCalc.additionalCharges,
          additional_parking_charges: liveCalc.parkingCharges,
          labour_cess: liveCalc.labourCess,
          gst_amount: liveCalc.gst,
          total_price: liveCalc.total,
          uds: liveCalc.uds,
          balance_amount: Math.round(liveCalc.total - (customer.total_received || 0)),
          payment_received_percentage: liveCalc.total > 0 ? Math.round(((customer.total_received || 0) / liveCalc.total) * 10000) / 100 : 0,
          payment_pending_percentage: liveCalc.total > 0 ? Math.round((1 - (customer.total_received || 0) / liveCalc.total) * 10000) / 100 : 100,
          custom_fields: {
            ...(customer.custom_fields || {}),
            floor_rise_cost: editData.floor_rise_cost || 0,
            floor_rise_total: liveCalc.floorRiseTotal || 0,
          }
        };
      }
      
      await axios.put(`${API}/customers/${id}`, dataToSave);
      fetchCustomerData(); // Refresh to get updated data
      setEditing(false);
      setLiveCalc(null);
      toast.success("Customer updated with recalculated prices");
    } catch (error) {
      toast.error("Failed to update customer");
    } finally {
      setSaving(false);
    }
  };

  const handleAgreementStatusChange = async (newStatus) => {
    try {
      await axios.put(`${API}/customers/${id}`, {
        agreement_status: newStatus
      });
      setCustomer({ ...customer, agreement_status: newStatus });
      toast.success(`Agreement status updated to ${newStatus}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to update agreement status");
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
      const response = await axios.put(`${API}/payments/item/${id}/${itemId}`, {
        payment_status: status,
        payment_date: status === "paid" ? new Date().toISOString().split("T")[0] : null,
      });
      
      // Update local payment schedule immediately
      setPaymentSchedule(prev => ({
        ...prev,
        items: prev.items.map(item => 
          item.id === itemId 
            ? { ...item, payment_status: status, payment_date: status === "paid" ? new Date().toISOString().split("T")[0] : null }
            : item
        )
      }));
      
      // Update customer's payment tracking fields from API response
      if (response.data) {
        setCustomer(prev => ({
          ...prev,
          total_received: response.data.total_received,
          balance_amount: response.data.balance_amount,
          payment_received_percentage: response.data.payment_received_percentage,
          payment_pending_percentage: response.data.payment_pending_percentage
        }));
      }
      
      toast.success(`Payment marked as ${status} - Received: ₹${response.data.total_received?.toLocaleString('en-IN')}`);
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

  // Transaction Handlers
  const handleSaveTransaction = async () => {
    try {
      const transactionData = {
        ...newTransaction,
        amount: parseFloat(newTransaction.amount) || 0
      };

      if (editingTransaction) {
        await axios.put(`${API}/transactions/${id}/${editingTransaction.id}`, transactionData);
        toast.success("Transaction updated successfully");
      } else {
        await axios.post(`${API}/transactions/${id}`, transactionData);
        toast.success("Transaction added successfully");
      }

      // Refresh transactions and overdue info
      const [transactionsRes, overdueRes] = await Promise.all([
        axios.get(`${API}/transactions/${id}`),
        axios.get(`${API}/customers/${id}/overdue`).catch(() => ({ data: null }))
      ]);
      setTransactions(transactionsRes.data || []);
      setOverdueInfo(overdueRes.data);

      // Reset form
      setTransactionDialogOpen(false);
      setEditingTransaction(null);
      setNewTransaction({
        transaction_stage: "",
        transaction_date: "",
        bank_name: "",
        transaction_number: "",
        amount: "",
        notes: ""
      });
    } catch (error) {
      toast.error("Failed to save transaction");
    }
  };

  const handleEditTransaction = (txn) => {
    setEditingTransaction(txn);
    setNewTransaction({
      transaction_stage: txn.transaction_stage,
      transaction_date: txn.transaction_date,
      bank_name: txn.bank_name,
      transaction_number: txn.transaction_number,
      amount: txn.amount?.toString() || "",
      notes: txn.notes || ""
    });
    setTransactionDialogOpen(true);
  };

  const handleDeleteTransaction = async (transactionId) => {
    if (!window.confirm("Are you sure you want to delete this transaction?")) {
      return;
    }
    
    try {
      await axios.delete(`${API}/transactions/${id}/${transactionId}`);
      
      // Refresh transactions and overdue info
      const [transactionsRes, overdueRes] = await Promise.all([
        axios.get(`${API}/transactions/${id}`),
        axios.get(`${API}/customers/${id}/overdue`).catch(() => ({ data: null }))
      ]);
      setTransactions(transactionsRes.data || []);
      setOverdueInfo(overdueRes.data);
      
      toast.success("Transaction deleted");
    } catch (error) {
      toast.error("Failed to delete transaction");
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

  // Bank NOC Generation Handler
  const handleGenerateNoc = async (nocType, bankName) => {
    setGeneratingNoc(nocType);
    try {
      const response = await axios.post(`${API}/documents/generate`, {
        customer_id: id,
        doc_type: nocType,
      });
      setDocuments([...documents, response.data.document]);
      toast.success(`${bankName} NOC generated successfully`);
    } catch (error) {
      toast.error(`Failed to generate ${bankName} NOC`);
    } finally {
      setGeneratingNoc(null);
    }
  };

  const handlePreviewWelcomeEmail = async () => {
    setSendingWelcome(true);
    try {
      const response = await axios.get(`${API}/communication/preview-welcome-email/${id}`);
      setEmailComposerData(response.data);
      setEditedEmailSubject(response.data.subject);
      setEditedEmailBody(response.data.body);
      setEditedEmailTo(response.data.recipient_email || customer.email);
      setEditedEmailCc("");
      setEmailComposerOpen(true);
    } catch (error) {
      toast.error("Failed to generate welcome email preview");
    } finally {
      setSendingWelcome(false);
    }
  };

  const handlePreviewSalesAgreement = async () => {
    setSendingEmail(true);
    try {
      const response = await axios.get(`${API}/communication/preview-sales-agreement/${id}`);
      setEmailComposerData(response.data);
      setEditedEmailSubject(response.data.subject);
      setEditedEmailBody(response.data.body);
      setEditedEmailTo(response.data.recipient_email || customer.email);
      setEditedEmailCc("");
      setEmailComposerOpen(true);
    } catch (error) {
      toast.error("Failed to generate sales agreement preview");
    } finally {
      setSendingEmail(false);
    }
  };

  const handlePreviewAllotmentLetter = async () => {
    setSendingEmail(true);
    try {
      const response = await axios.get(`${API}/communication/preview-allotment-letter/${id}`);
      setEmailComposerData(response.data);
      setEditedEmailSubject(response.data.subject);
      setEditedEmailBody(response.data.body);
      setEditedEmailTo(response.data.recipient_email || customer.email);
      setEditedEmailCc("");
      setEmailComposerOpen(true);
    } catch (error) {
      toast.error("Failed to generate allotment letter preview");
    } finally {
      setSendingEmail(false);
    }
  };

  const handleSendDocumentEmail = async () => {
    if (!emailComposerData) return;
    
    setSendingEmail(true);
    try {
      const response = await axios.post(`${API}/communication/send-document-email/${id}`, {
        email_type: emailComposerData.email_type,
        subject: editedEmailSubject,
        body: editedEmailBody,
        recipient_email: editedEmailTo,
        cc: editedEmailCc || null
      });
      toast.success(response.data.message);
      setEmailComposerOpen(false);
      setEmailComposerData(null);
      fetchCustomerData();
    } catch (error) {
      toast.error("Failed to send email");
    } finally {
      setSendingEmail(false);
    }
  };

  const handleSendWelcomeEmail = async () => {
    setSendingWelcome(true);
    try {
      const response = await axios.post(`${API}/communication/send-welcome-email/${id}`);
      toast.success(`Welcome email sent to ${customer.email}`);
      setWelcomePreviewOpen(false);
      setWelcomePreviewData(null);
      fetchCustomerData();
    } catch (error) {
      toast.error("Failed to send welcome email");
    } finally {
      setSendingWelcome(false);
    }
  };

  const handleSendWhatsAppWelcome = () => {
    // Format phone number - remove spaces, dashes, and ensure it starts with country code
    let phone = customer.phone?.replace(/[\s\-\(\)]/g, '') || '';
    
    // If phone doesn't start with country code, assume India (+91)
    if (!phone.startsWith('+') && !phone.startsWith('91')) {
      phone = '91' + phone;
    } else if (phone.startsWith('+')) {
      phone = phone.substring(1); // Remove + for WhatsApp URL
    }
    
    // Welcome message
    const message = `Hi ${customer.name}, This is from RRL Builders. Congratulations on your new home purchase! We are happy to welcome you to the RRL family.

Property Details:
- Project: ${customer.project}
- Unit: ${customer.unit_number}
- Tower: ${customer.tower}

Thank you for choosing RRL Builders and Developers Pvt. Ltd.`;
    
    // Encode message for URL
    const encodedMessage = encodeURIComponent(message);
    
    // Open WhatsApp Web
    const whatsappUrl = `https://web.whatsapp.com/send?phone=${phone}&text=${encodedMessage}`;
    window.open(whatsappUrl, '_blank');
    
    // Log the communication
    axios.post(`${API}/communication/whatsapp?customer_id=${id}&message=${encodeURIComponent('Welcome message sent via WhatsApp')}`).catch(() => {});
    
    toast.success("Opening WhatsApp Web...");
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
        // Build attachment info
        const attachmentIds = selectedAttachments.join(",");
        let url = `${API}/communication/email?customer_id=${id}&subject=${encodeURIComponent(commSubject)}&message=${encodeURIComponent(commMessage)}`;
        
        if (attachmentIds) {
          url += `&attachment_ids=${attachmentIds}`;
        }
        
        // If there's a local file, upload it first then send email with attachment
        if (localAttachment) {
          const formData = new FormData();
          formData.append("file", localAttachment);
          formData.append("doc_type", "email_attachment");
          
          const uploadRes = await axios.post(`${API}/customers/${id}/upload-document`, formData, {
            headers: { "Content-Type": "multipart/form-data" },
          });
          
          if (uploadRes.data.doc_id) {
            url += attachmentIds ? `,${uploadRes.data.doc_id}` : `&attachment_ids=${uploadRes.data.doc_id}`;
          }
        }
        
        await axios.post(url);
        toast.success("Email sent successfully!");
      } else {
        await axios.post(`${API}/communication/whatsapp?customer_id=${id}&message=${encodeURIComponent(commMessage)}`);
        toast.success("WhatsApp message sent (MOCKED)");
      }
      fetchCustomerData();
      setCommDialogOpen(false);
      setCommMessage("");
      setCommSubject("");
      setSelectedAttachments([]);
      setLocalAttachment(null);
    } catch (error) {
      toast.error("Failed to send message");
    }
  };

  const toggleAttachment = (docId) => {
    setSelectedAttachments(prev => 
      prev.includes(docId) 
        ? prev.filter(id => id !== docId)
        : [...prev, docId]
    );
  };

  const handleLocalFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        toast.error("File size should be less than 10MB");
        return;
      }
      setLocalAttachment(file);
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

  // Delete document functions
  const handleDeleteDocClick = (doc, type) => {
    setDocToDelete(doc);
    setDocDeleteType(type);
    setDocDeleteDialogOpen(true);
  };

  const handleConfirmDeleteDoc = async () => {
    if (!docToDelete) return;
    
    setDocDeleting(true);
    try {
      const endpoint = docDeleteType === 'generated' 
        ? `${API}/documents/${docToDelete.id}`
        : `${API}/customers/${id}/documents/${docToDelete.id}`;
      
      await axios.delete(endpoint);
      toast.success("Document deleted successfully");
      setDocDeleteDialogOpen(false);
      setDocToDelete(null);
      setDocDeleteType(null);
      fetchCustomerData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to delete document");
    } finally {
      setDocDeleting(false);
    }
  };

  // Live price calculation function
  const calculateLivePrice = (data) => {
    const saleableArea = parseFloat(data.saleable_area) || 0;
    const ratePerSqft = parseFloat(data.rate_per_sqft) || 0;
    const floorRiseCost = parseFloat(data.floor_rise_cost) || 0;
    const additionalParking = parseInt(data.additional_parking) || 0;
    
    // Base price = Total Saleable Area × Rate/sqft
    const basePrice = saleableArea * ratePerSqft;
    
    // Floor Rise is manual cost per sqft × saleable area
    const floorRiseTotal = saleableArea * floorRiseCost;
    
    // Club House - editable, default ₹2,00,000
    const clubHouse = parseFloat(editData?.club_house_charges) || 200000;
    
    // Additional Charges - editable manual entry
    const additionalCharges = parseFloat(editData?.additional_charges) || 0;
    
    const parkingCharges = additionalParking * 300000; // ₹3,00,000 per additional
    const subtotal = basePrice + floorRiseTotal + clubHouse + parkingCharges + additionalCharges;
    const labourCess = subtotal * 0.007; // 0.70%
    const gst = subtotal * 0.05; // 5%
    const total = subtotal + labourCess + gst;
    const uds = saleableArea * 0.495046;
    
    return {
      basePrice: Math.round(basePrice),
      floorRiseCost,
      floorRiseTotal: Math.round(floorRiseTotal),
      effectiveRate: ratePerSqft + floorRiseCost,
      clubHouse: Math.round(clubHouse),
      additionalCharges: Math.round(additionalCharges),
      parkingCharges: Math.round(parkingCharges),
      subtotal: Math.round(subtotal),
      labourCess: Math.round(labourCess),
      gst: Math.round(gst),
      total: Math.round(total),
      uds: Math.round(uds * 100) / 100
    };
  };

  // Update live calculation when editData changes
  useEffect(() => {
    if (editing && editData) {
      const calc = calculateLivePrice(editData);
      setLiveCalc(calc);
    }
  }, [editing, editData]);

  // Handle edit data change with live calculation
  const handleEditChange = (field, value) => {
    const newEditData = { ...editData, [field]: value };
    setEditData(newEditData);
  };

  // Calculator Tab Editing Functions
  const initCalcEdit = () => {
    setCalcData({
      saleable_area: customer.saleable_area || 0,
      rate_per_sqft: customer.rate_per_sqft || 0,
      floor: customer.floor || 0,
      floor_rise_cost: customer.custom_fields?.floor_rise_cost || 0,
      additional_parking: customer.additional_parking || 0,
    });
    setCalcEditing(true);
  };

  const handleCalcChange = (field, value) => {
    const newCalcData = { ...calcData, [field]: value };
    setCalcData(newCalcData);
    
    // Live calculate
    const calc = calculateLivePrice(newCalcData);
    setCalcLivePrice(calc);
  };

  // Update calc live price when calcData changes
  useEffect(() => {
    if (calcEditing && calcData.saleable_area) {
      const calc = calculateLivePrice(calcData);
      setCalcLivePrice(calc);
    }
  }, [calcEditing, calcData]);

  const saveCalcChanges = async () => {
    if (!calcLivePrice) return;
    
    setCalcSaving(true);
    try {
      const updates = {
        saleable_area: calcData.saleable_area,
        rate_per_sqft: calcData.rate_per_sqft,
        floor: calcData.floor,
        additional_parking: calcData.additional_parking,
        base_price: calcLivePrice.basePrice,
        club_house_charges: calcLivePrice.clubHouse,
        additional_parking_charges: calcLivePrice.parkingCharges,
        labour_cess: calcLivePrice.labourCess,
        gst_amount: calcLivePrice.gst,
        total_price: calcLivePrice.total,
        uds: calcLivePrice.uds,
        balance_amount: Math.round(calcLivePrice.total - (customer.total_received || 0)),
        payment_received_percentage: calcLivePrice.total > 0 ? Math.round(((customer.total_received || 0) / calcLivePrice.total) * 10000) / 100 : 0,
        payment_pending_percentage: calcLivePrice.total > 0 ? Math.round((1 - (customer.total_received || 0) / calcLivePrice.total) * 10000) / 100 : 100,
        custom_fields: {
          ...(customer.custom_fields || {}),
          floor_rise_cost: calcData.floor_rise_cost || 0,
          floor_rise_total: calcLivePrice.floorRiseTotal || 0,
        }
      };
      
      await axios.put(`${API}/customers/${id}`, updates);
      fetchCustomerData();
      setCalcEditing(false);
      setCalcLivePrice(null);
      toast.success("Calculator values saved and profile updated!");
    } catch (error) {
      toast.error("Failed to save changes");
    } finally {
      setCalcSaving(false);
    }
  };

  const cancelCalcEdit = () => {
    setCalcEditing(false);
    setCalcData({});
    setCalcLivePrice(null);
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
            onClick={handlePreviewWelcomeEmail}
            disabled={sendingWelcome}
            data-testid="send-welcome-btn"
          >
            {sendingWelcome ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Mail className="w-4 h-4 mr-2" />
            )}
            Welcome Email
          </Button>
          <Button
            variant="outline"
            onClick={handlePreviewSalesAgreement}
            disabled={sendingEmail}
            data-testid="send-sales-agreement-btn"
            className="text-amber-600 hover:text-amber-700 hover:bg-amber-50 border-amber-200"
          >
            {sendingEmail ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <FileText className="w-4 h-4 mr-2" />
            )}
            Sales Agreement
          </Button>
          <Button
            variant="outline"
            onClick={handlePreviewAllotmentLetter}
            disabled={sendingEmail}
            data-testid="send-allotment-btn"
            className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 border-blue-200"
          >
            {sendingEmail ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <FileText className="w-4 h-4 mr-2" />
            )}
            Allotment Letter
          </Button>
          <Button
            variant="outline"
            onClick={handleSendWhatsAppWelcome}
            className="text-green-600 hover:text-green-700 hover:bg-green-50 border-green-200"
            data-testid="send-whatsapp-btn"
          >
            <MessageCircle className="w-4 h-4 mr-2" />
            WhatsApp
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
            !isAccountsRole && (
              <Button variant="outline" onClick={() => setEditing(true)} data-testid="edit-customer-btn">
                <Edit className="w-4 h-4 mr-2" />
                Edit
              </Button>
            )
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
            <p className="text-sm text-slate-500 mb-2">Agreement Status</p>
            <Select
              value={customer.agreement_status || 'draft'}
              onValueChange={handleAgreementStatusChange}
            >
              <SelectTrigger className={`w-full h-8 ${
                customer.agreement_status === 'signed' ? 'bg-green-100 text-green-700 border-green-300' :
                customer.agreement_status === 'registered' ? 'bg-blue-100 text-blue-700 border-blue-300' :
                customer.agreement_status === 'sent' ? 'bg-yellow-100 text-yellow-700 border-yellow-300' :
                customer.agreement_status === 'disbursement' ? 'bg-purple-100 text-purple-700 border-purple-300' :
                'bg-slate-100 text-slate-700 border-slate-300'
              }`}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="sent">Sent</SelectItem>
                <SelectItem value="signed">Signed</SelectItem>
                <SelectItem value="registered">Registered</SelectItem>
                <SelectItem value="disbursement">Disbursement</SelectItem>
              </SelectContent>
            </Select>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-slate-500">Received</p>
            <p className="font-semibold text-green-600">
              {(() => {
                const transactionTotal = transactions.reduce((sum, txn) => sum + (txn.amount || 0), 0);
                const bookingAmount = customer.booking_amount || 0;
                const totalReceived = transactionTotal + bookingAmount;
                const totalPrice = customer.total_price || 0;
                const receivedPercentage = totalPrice > 0 ? (totalReceived / totalPrice) * 100 : 0;
                return `${receivedPercentage.toFixed(1)}%`;
              })()}
            </p>
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
            <CreditCard className="w-4 h-4 mr-2" />
            Payment Tracking
          </TabsTrigger>
          <TabsTrigger value="payments" data-testid="tab-payments">
            <CreditCard className="w-4 h-4 mr-2" />
            Payment Schedule
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
          <TabsTrigger value="notes" data-testid="tab-notes">
            <FileText className="w-4 h-4 mr-2" />
            Notes
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
                      <Label>Father's/Spouse Name</Label>
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
                      <Label>Date of Birth</Label>
                      {editing ? (
                        <Input
                          type="date"
                          value={editData.date_of_birth || ""}
                          onChange={(e) => setEditData({ ...editData, date_of_birth: e.target.value })}
                        />
                      ) : (
                        <p className="text-slate-700 mt-1">{customer.date_of_birth || "-"}</p>
                      )}
                    </div>
                    <div>
                      <Label>Gender</Label>
                      {editing ? (
                        <Select
                          value={editData.gender || "male"}
                          onValueChange={(value) => setEditData({ ...editData, gender: value })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="male">Male (S/o)</SelectItem>
                            <SelectItem value="female">Female (D/o)</SelectItem>
                            <SelectItem value="spouse">Spouse (W/o)</SelectItem>
                          </SelectContent>
                        </Select>
                      ) : (
                        <p className="text-slate-700 mt-1">
                          {customer.gender === 'female' ? 'Female (D/o)' : 
                           customer.gender === 'spouse' ? 'Spouse (W/o)' : 'Male (S/o)'}
                        </p>
                      )}
                    </div>
                    <div>
                      <Label>Nationality</Label>
                      <p className="text-slate-700 mt-1">{customer.nationality || "Indian"}</p>
                    </div>
                    <div>
                      <Label>PAN Number</Label>
                      <p className="text-slate-700 mt-1">{customer.pan_number || "-"}</p>
                    </div>
                    <div>
                      <Label>Aadhaar Number</Label>
                      <p className="text-slate-700 mt-1">{customer.aadhar_number || "-"}</p>
                    </div>
                    <div>
                      <Label>Profession</Label>
                      <p className="text-slate-700 mt-1">{customer.custom_fields?.profession || "-"}</p>
                    </div>
                    <div>
                      <Label>Company</Label>
                      <p className="text-slate-700 mt-1">{customer.company || "-"}</p>
                    </div>
                    <div>
                      <Label>Designation</Label>
                      <p className="text-slate-700 mt-1">{customer.designation || "-"}</p>
                    </div>
                  </div>
                  <div>
                    <Label>Address</Label>
                    <p className="text-slate-700 mt-1">{customer.address || "-"}</p>
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
                          onChange={(e) => handleEditChange('floor', parseInt(e.target.value) || 0)}
                          placeholder="Floor number"
                        />
                      ) : (
                        <p className="text-slate-700 mt-1">{customer.floor || "0"}</p>
                      )}
                    </div>
                    <div>
                      <Label>Saleable Area (sq.ft)</Label>
                      {editing ? (
                        <Input
                          type="number"
                          value={editData.saleable_area || ""}
                          onChange={(e) => handleEditChange('saleable_area', parseFloat(e.target.value) || 0)}
                        />
                      ) : (
                        <p className="text-slate-700 mt-1">{customer.saleable_area || 0} sq.ft</p>
                      )}
                    </div>
                    <div>
                      <Label>Rate/Sq.ft (₹)</Label>
                      {editing ? (
                        <Input
                          type="number"
                          value={editData.rate_per_sqft || ""}
                          onChange={(e) => handleEditChange('rate_per_sqft', parseFloat(e.target.value) || 0)}
                        />
                      ) : (
                        <p className="text-slate-700 mt-1">₹{customer.rate_per_sqft?.toLocaleString() || 0}</p>
                      )}
                    </div>
                    <div>
                      <Label>Floor Rise (₹/sq.ft)</Label>
                      {editing ? (
                        <>
                          <Input
                            type="number"
                            value={editData.floor_rise_cost || ""}
                            onChange={(e) => handleEditChange('floor_rise_cost', parseFloat(e.target.value) || 0)}
                            placeholder="e.g., 50"
                          />
                          <p className="text-xs text-slate-500 mt-1">Manual floor rise cost per sq.ft</p>
                        </>
                      ) : (
                        <p className="text-slate-700 mt-1">₹{customer.custom_fields?.floor_rise_cost || 0}/sq.ft</p>
                      )}
                    </div>
                    <div>
                      <Label>Additional Parking</Label>
                      {editing ? (
                        <Input
                          type="number"
                          min="0"
                          value={editData.additional_parking || "0"}
                          onChange={(e) => handleEditChange('additional_parking', parseInt(e.target.value) || 0)}
                        />
                      ) : (
                        <p className="text-slate-700 mt-1">{customer.additional_parking || 0}</p>
                      )}
                    </div>
                    <div>
                      <Label>Base Price</Label>
                      <p className="text-slate-700 mt-1">
                        {editing && liveCalc ? formatCurrency(liveCalc.basePrice) : formatCurrency(customer.base_price)}
                      </p>
                    </div>
                    <div>
                      <Label>Floor Rise Total</Label>
                      <p className="text-slate-700 mt-1">
                        {editing && liveCalc ? formatCurrency(liveCalc.floorRiseTotal) : formatCurrency(customer.custom_fields?.floor_rise_total || 0)}
                      </p>
                    </div>
                    <div>
                      <Label>Club House</Label>
                      {editing ? (
                        <Input
                          type="number"
                          value={editData.club_house_charges || 200000}
                          onChange={(e) => setEditData({...editData, club_house_charges: parseFloat(e.target.value) || 0})}
                          className="mt-1"
                        />
                      ) : (
                        <p className="text-slate-700 mt-1">
                          {formatCurrency(customer.club_house_charges)}
                        </p>
                      )}
                    </div>
                    <div>
                      <Label>Additional Charges</Label>
                      {editing ? (
                        <Input
                          type="number"
                          value={editData.additional_charges || 0}
                          onChange={(e) => setEditData({...editData, additional_charges: parseFloat(e.target.value) || 0})}
                          className="mt-1"
                          placeholder="Enter additional charges"
                        />
                      ) : (
                        <p className="text-slate-700 mt-1">
                          {formatCurrency(customer.additional_charges || 0)}
                        </p>
                      )}
                    </div>
                    <div>
                      <Label>Labour Cess (0.70%)</Label>
                      <p className="text-slate-700 mt-1">
                        {editing && liveCalc ? formatCurrency(liveCalc.labourCess) : formatCurrency(customer.labour_cess)}
                      </p>
                    </div>
                    <div>
                      <Label>GST (5%)</Label>
                      <p className="text-slate-700 mt-1">
                        {editing && liveCalc ? formatCurrency(liveCalc.gst) : formatCurrency(customer.gst_amount)}
                      </p>
                    </div>
                    <div>
                      <Label>Total Price</Label>
                      <p className={`font-bold mt-1 ${editing && liveCalc ? 'text-green-600' : 'text-primary'}`}>
                        {editing && liveCalc ? formatCurrency(liveCalc.total) : formatCurrency(customer.total_price)}
                        {editing && liveCalc && liveCalc.total !== customer.total_price && (
                          <span className="text-xs font-normal text-slate-500 ml-2">(live preview)</span>
                        )}
                      </p>
                    </div>
                    <div>
                      <Label>UDS</Label>
                      <p className="text-slate-700 mt-1">
                        {editing && liveCalc ? liveCalc.uds : (customer.uds || "-")}
                      </p>
                    </div>
                  </div>
                  {editing && liveCalc && (
                    <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                      <p className="text-sm text-green-700 font-medium mb-2">
                        Live Price Preview
                      </p>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <span>Base Price ({editData.saleable_area || 0} × ₹{editData.rate_per_sqft || 0}):</span>
                        <span className="font-medium text-right">{formatCurrency(liveCalc.basePrice)}</span>
                        {liveCalc.floorRiseTotal > 0 && (
                          <>
                            <span>Floor Rise ({editData.saleable_area || 0} × ₹{editData.floor_rise_cost || 0}):</span>
                            <span className="font-medium text-right">{formatCurrency(liveCalc.floorRiseTotal)}</span>
                          </>
                        )}
                        <span>Club House & Infrastructure:</span>
                        <span className="font-medium text-right">{formatCurrency(liveCalc.clubHouse)}</span>
                        {liveCalc.additionalCharges > 0 && (
                          <>
                            <span>Additional Charges:</span>
                            <span className="font-medium text-right">{formatCurrency(liveCalc.additionalCharges)}</span>
                          </>
                        )}
                        <span>Additional Parking:</span>
                        <span className="font-medium text-right">{formatCurrency(liveCalc.parkingCharges)}</span>
                        <span className="font-semibold pt-2 border-t">New Total:</span>
                        <span className="font-bold text-right text-green-700 pt-2 border-t">{formatCurrency(liveCalc.total)}</span>
                      </div>
                      <p className="text-xs text-green-600 mt-2">
                        Price updates automatically as you edit. Click "Save Changes" to persist.
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Booking Details</CardTitle>
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
                {(customer.transaction_details || customer.transaction_date || customer.transaction_bank) && (
                  <div className="mt-4 pt-4 border-t">
                    <p className="font-medium text-slate-700 mb-3">Transaction Details</p>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label>Transaction Date</Label>
                        <p className="text-slate-700 mt-1">{customer.transaction_date || "-"}</p>
                      </div>
                      <div>
                        <Label>Transaction Bank</Label>
                        <p className="text-slate-700 mt-1">{customer.transaction_bank || "-"}</p>
                      </div>
                    </div>
                    {customer.transaction_details && (
                      <div className="mt-2">
                        <Label>Transaction Reference</Label>
                        <p className="text-slate-700 mt-1">{customer.transaction_details}</p>
                      </div>
                    )}
                  </div>
                )}
                {customer.remarks && (
                  <div className="mt-4 pt-4 border-t">
                    <Label>Remarks</Label>
                    <p className="text-slate-700 mt-1">{customer.remarks}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Bank Opted for Loan */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Bank Opted for Loan</CardTitle>
                {!isAccountsRole && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setBankDetailsEditing(!bankDetailsEditing)}
                    data-testid="edit-bank-details-btn"
                  >
                    {bankDetailsEditing ? (
                      <>Cancel</>
                    ) : (
                      <>
                        <Edit className="w-4 h-4 mr-1" />
                        Edit
                      </>
                    )}
                  </Button>
                )}
              </CardHeader>
              <CardContent>
                {bankDetailsEditing ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label>Bank Name *</Label>
                        <Select
                          value={bankDetails.bank_name || ""}
                          onValueChange={(value) => setBankDetails({ ...bankDetails, bank_name: value, bank_name_other: value !== "Others" ? "" : bankDetails.bank_name_other })}
                        >
                          <SelectTrigger data-testid="bank-name-select">
                            <SelectValue placeholder="Select bank" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="HDFC">HDFC Bank</SelectItem>
                            <SelectItem value="BOB">Bank of Baroda</SelectItem>
                            <SelectItem value="TATA">Tata Capital</SelectItem>
                            <SelectItem value="SBI">State Bank of India</SelectItem>
                            <SelectItem value="ICICI">ICICI Bank</SelectItem>
                            <SelectItem value="AXIS">Axis Bank</SelectItem>
                            <SelectItem value="PNB">Punjab National Bank</SelectItem>
                            <SelectItem value="KOTAK">Kotak Mahindra Bank</SelectItem>
                            <SelectItem value="Others">Others</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      {bankDetails.bank_name === "Others" && (
                        <div>
                          <Label>Other Bank Name *</Label>
                          <Input
                            value={bankDetails.bank_name_other || ""}
                            onChange={(e) => setBankDetails({ ...bankDetails, bank_name_other: e.target.value })}
                            placeholder="Enter bank name"
                            data-testid="bank-name-other-input"
                          />
                        </div>
                      )}
                      <div>
                        <Label>Account Holder Name</Label>
                        <Input
                          value={bankDetails.bank_account_holder || ""}
                          onChange={(e) => setBankDetails({ ...bankDetails, bank_account_holder: e.target.value })}
                          placeholder="Enter account holder name"
                          data-testid="bank-account-holder-input"
                        />
                      </div>
                      <div>
                        <Label>Account Number</Label>
                        <Input
                          value={bankDetails.bank_account_number || ""}
                          onChange={(e) => setBankDetails({ ...bankDetails, bank_account_number: e.target.value })}
                          placeholder="Enter account number"
                          data-testid="bank-account-number-input"
                        />
                      </div>
                      <div>
                        <Label>IFSC Code</Label>
                        <Input
                          value={bankDetails.bank_ifsc_code || ""}
                          onChange={(e) => setBankDetails({ ...bankDetails, bank_ifsc_code: e.target.value.toUpperCase() })}
                          placeholder="Enter IFSC code"
                          data-testid="bank-ifsc-input"
                        />
                      </div>
                      <div>
                        <Label>Branch</Label>
                        <Input
                          value={bankDetails.bank_branch || ""}
                          onChange={(e) => setBankDetails({ ...bankDetails, bank_branch: e.target.value })}
                          placeholder="Enter branch name"
                          data-testid="bank-branch-input"
                        />
                      </div>
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" onClick={() => {
                        setBankDetailsEditing(false);
                        setBankDetails({
                          bank_name: customer.bank_name || "",
                          bank_name_other: customer.bank_name_other || "",
                          bank_account_number: customer.bank_account_number || "",
                          bank_ifsc_code: customer.bank_ifsc_code || "",
                          bank_branch: customer.bank_branch || "",
                          bank_account_holder: customer.bank_account_holder || "",
                        });
                      }}>
                        Cancel
                      </Button>
                      <Button onClick={handleSaveBankDetails} data-testid="save-bank-details-btn">
                        <Save className="w-4 h-4 mr-1" />
                        Save Bank Details
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Bank Name</Label>
                      <p className="text-slate-700 mt-1">
                        {customer.bank_name === "Others" 
                          ? customer.bank_name_other || "-" 
                          : customer.bank_name || "-"}
                      </p>
                    </div>
                    <div>
                      <Label>Account Holder</Label>
                      <p className="text-slate-700 mt-1">{customer.bank_account_holder || "-"}</p>
                    </div>
                    <div>
                      <Label>Account Number</Label>
                      <p className="text-slate-700 mt-1 font-mono">{customer.bank_account_number || "-"}</p>
                    </div>
                    <div>
                      <Label>IFSC Code</Label>
                      <p className="text-slate-700 mt-1 font-mono">{customer.bank_ifsc_code || "-"}</p>
                    </div>
                    <div>
                      <Label>Branch</Label>
                      <p className="text-slate-700 mt-1">{customer.bank_branch || "-"}</p>
                    </div>
                  </div>
                )}
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
                      <Label>Father's/Spouse Name</Label>
                      <p className="text-slate-700 mt-1">{customer.co_applicant_father_name || "-"}</p>
                    </div>
                    <div>
                      <Label>Phone</Label>
                      <p className="text-slate-700 mt-1">{customer.co_applicant_phone || "-"}</p>
                    </div>
                    <div>
                      <Label>Email</Label>
                      <p className="text-slate-700 mt-1">{customer.co_applicant_email || "-"}</p>
                    </div>
                    <div>
                      <Label>PAN Number</Label>
                      <p className="text-slate-700 mt-1">{customer.co_applicant_pan || "-"}</p>
                    </div>
                    <div>
                      <Label>Aadhaar Number</Label>
                      <p className="text-slate-700 mt-1">{customer.co_applicant_aadhar || "-"}</p>
                    </div>
                    <div>
                      <Label>Profession</Label>
                      <p className="text-slate-700 mt-1">{customer.custom_fields?.co_applicant_profession || "-"}</p>
                    </div>
                    <div>
                      <Label>Nationality</Label>
                      <p className="text-slate-700 mt-1">{customer.custom_fields?.co_applicant_nationality || "Indian"}</p>
                    </div>
                  </div>
                  {customer.co_applicant_address && (
                    <div className="mt-4">
                      <Label>Address</Label>
                      <p className="text-slate-700 mt-1">{customer.co_applicant_address}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Payment Schedule Tab */}
        <TabsContent value="calculator">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Payment Tracking */}
            <Card>
              <CardHeader>
                <CardTitle>Payment Tracking</CardTitle>
                <CardDescription>Track received vs pending payments</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {(() => {
                  // Calculate received from transactions + booking amount
                  const transactionTotal = transactions.reduce((sum, txn) => sum + (txn.amount || 0), 0);
                  const bookingAmount = customer.booking_amount || 0;
                  const totalReceived = transactionTotal + bookingAmount;
                  const totalPrice = customer.total_price || 0;
                  const balanceAmount = totalPrice - totalReceived;
                  const receivedPercentage = totalPrice > 0 ? (totalReceived / totalPrice) * 100 : 0;
                  const pendingPercentage = totalPrice > 0 ? (balanceAmount / totalPrice) * 100 : 100;
                  
                  return (
                    <>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center p-4 bg-green-50 rounded-lg">
                          <p className="text-sm text-slate-600">Received</p>
                          <p className="text-2xl font-bold text-green-600">{formatCurrency(totalReceived)}</p>
                          <p className="text-lg font-semibold text-green-600">{receivedPercentage.toFixed(1)}%</p>
                          <p className="text-xs text-slate-500 mt-1">
                            (Booking: {formatCurrency(bookingAmount)} + Transactions: {formatCurrency(transactionTotal)})
                          </p>
                        </div>
                        <div className="text-center p-4 bg-red-50 rounded-lg">
                          <p className="text-sm text-slate-600">Pending</p>
                          <p className="text-2xl font-bold text-red-600">{formatCurrency(balanceAmount)}</p>
                          <p className="text-lg font-semibold text-red-600">{pendingPercentage.toFixed(1)}%</p>
                        </div>
                      </div>
                      
                      {/* Stage-based Overdue Amount */}
                      {overdueInfo?.is_overdue && (
                        <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="destructive">PAYMENT OVERDUE</Badge>
                            <span className="text-sm text-slate-600">as per disbursement slab: {overdueInfo.current_stage_name}</span>
                          </div>
                          <div className="grid grid-cols-3 gap-4 text-sm">
                            <div>
                              <p className="text-slate-600">Expected ({overdueInfo.cumulative_percentage}%)</p>
                              <p className="font-bold text-slate-900">{formatCurrency(overdueInfo.expected_amount)}</p>
                            </div>
                            <div>
                              <p className="text-slate-600">Total Received</p>
                              <p className="font-bold text-green-600">{formatCurrency(overdueInfo.total_received)}</p>
                            </div>
                            <div>
                              <p className="text-slate-600">Overdue Amount</p>
                              <p className="font-bold text-2xl text-red-600">{formatCurrency(overdueInfo.overdue_amount)}</p>
                            </div>
                          </div>
                        </div>
                      )}
                      
                      {overdueInfo && !overdueInfo.is_overdue && overdueInfo.current_stage && (
                        <div className="p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2">
                          <CheckCircle className="h-5 w-5 text-green-600" />
                          <span className="text-sm text-green-700">
                            Payments up to date for current disbursement slab: {overdueInfo.current_stage_name}
                          </span>
                        </div>
                      )}
                      
                      {overdueInfo && !overdueInfo.current_stage && (
                        <div className="p-3 bg-slate-50 border rounded-lg text-sm text-slate-500">
                          No disbursement slab set by admin. Overdue tracking unavailable.
                        </div>
                      )}
                      
                      {/* Progress Bar */}
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Payment Progress</span>
                          <span>{receivedPercentage.toFixed(1)}%</span>
                        </div>
                        <div className="h-4 bg-slate-200 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-green-500 transition-all duration-500"
                            style={{ width: `${Math.min(receivedPercentage, 100)}%` }}
                          />
                        </div>
                      </div>
                      
                      {/* Payment Due Date Section */}
                      <div className="pt-4 border-t">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-slate-700">Next Payment Due Date</p>
                            {editingDueDate ? (
                              <div className="flex items-center gap-2 mt-1">
                                <Input
                                  type="date"
                                  value={paymentDueDate}
                                  onChange={(e) => setPaymentDueDate(e.target.value)}
                                  className="w-40"
                                  data-testid="payment-due-date-input"
                                />
                                <Button size="sm" onClick={handleUpdateDueDate}>
                                  <Save className="h-3 w-3 mr-1" />
                                  Save
                                </Button>
                                <Button size="sm" variant="outline" onClick={() => setEditingDueDate(false)}>
                                  Cancel
                                </Button>
                              </div>
                            ) : (
                              <div className="flex items-center gap-2">
                                <p className="text-lg font-semibold text-primary">
                                  {customer.payment_due_date 
                                    ? new Date(customer.payment_due_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
                                    : "Not set"}
                                </p>
                                <Button size="sm" variant="ghost" onClick={() => setEditingDueDate(true)} data-testid="edit-due-date-btn">
                                  <Edit className="h-3 w-3" />
                                </Button>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </>
                  );
                })()}
              </CardContent>
            </Card>

            {/* Disbursement Calculator */}
            <Card>
              <CardHeader>
                <CardTitle>Disbursement Calculator</CardTitle>
                <CardDescription>Calculate disbursement amounts</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="flex-1">
                    <Label htmlFor="disbursement-pct" className="text-sm">Enter Percentage (%)</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <Input
                        id="disbursement-pct"
                        type="number"
                        min="0"
                        max="100"
                        step="0.5"
                        value={disbursementPercentage}
                        onChange={(e) => setDisbursementPercentage(parseFloat(e.target.value) || 0)}
                        className="w-24"
                        data-testid="disbursement-percentage-input"
                      />
                      <span className="text-slate-500">%</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-slate-600">Disbursement Amount</p>
                    <p className="text-xl font-bold text-primary" data-testid="disbursement-amount">
                      {formatCurrency(customer.total_price * (disbursementPercentage / 100))}
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-4 gap-2 mt-3">
                  <Button 
                    variant="outline" 
                    size="sm"
                    className={disbursementPercentage === 30 ? "border-primary bg-primary/10" : ""}
                    onClick={() => setDisbursementPercentage(30)}
                  >
                    30%
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    className={disbursementPercentage === 50 ? "border-primary bg-primary/10" : ""}
                    onClick={() => setDisbursementPercentage(50)}
                  >
                    50%
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    className={disbursementPercentage === 70 ? "border-primary bg-primary/10" : ""}
                    onClick={() => setDisbursementPercentage(70)}
                  >
                    70%
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    className={disbursementPercentage === 100 ? "border-primary bg-primary/10" : ""}
                    onClick={() => setDisbursementPercentage(100)}
                  >
                    100%
                  </Button>
                </div>
                <div className="p-3 bg-blue-50 rounded-lg text-sm">
                  <div className="flex justify-between">
                    <span>Total Property Value:</span>
                    <span className="font-medium">{formatCurrency(customer.total_price)}</span>
                  </div>
                  <div className="flex justify-between mt-1">
                    <span>{disbursementPercentage}% Disbursement:</span>
                    <span className="font-bold text-blue-700">{formatCurrency(customer.total_price * (disbursementPercentage / 100))}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Transaction Records */}
          <Card className="mt-6">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Transaction Records</CardTitle>
                <CardDescription>Track all payment transactions by stage</CardDescription>
              </div>
              <Dialog open={transactionDialogOpen} onOpenChange={(open) => {
                setTransactionDialogOpen(open);
                if (!open) {
                  setEditingTransaction(null);
                  setNewTransaction({
                    transaction_stage: "",
                    transaction_date: "",
                    bank_name: "",
                    transaction_number: "",
                    amount: "",
                    notes: ""
                  });
                }
              }}>
                <DialogTrigger asChild>
                  <Button data-testid="add-transaction-btn">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Transaction
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>{editingTransaction ? "Edit Transaction" : "Add New Transaction"}</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label>Transaction Stage *</Label>
                      <Select
                        value={newTransaction.transaction_stage}
                        onValueChange={(value) => setNewTransaction({ ...newTransaction, transaction_stage: value })}
                      >
                        <SelectTrigger data-testid="transaction-stage-select">
                          <SelectValue placeholder="Select stage" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="booking">Booking</SelectItem>
                          <SelectItem value="agreement">Agreement</SelectItem>
                          <SelectItem value="scheduled_disbursement">Scheduled Disbursement</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Transaction Date *</Label>
                      <Input
                        type="date"
                        value={newTransaction.transaction_date}
                        onChange={(e) => setNewTransaction({ ...newTransaction, transaction_date: e.target.value })}
                        data-testid="transaction-date-input"
                      />
                    </div>
                    <div>
                      <Label>Bank Name *</Label>
                      <Input
                        value={newTransaction.bank_name}
                        onChange={(e) => setNewTransaction({ ...newTransaction, bank_name: e.target.value })}
                        placeholder="e.g., HDFC Bank"
                        data-testid="transaction-bank-input"
                      />
                    </div>
                    <div>
                      <Label>Transaction Number *</Label>
                      <Input
                        value={newTransaction.transaction_number}
                        onChange={(e) => setNewTransaction({ ...newTransaction, transaction_number: e.target.value })}
                        placeholder="e.g., TXN123456789"
                        data-testid="transaction-number-input"
                      />
                    </div>
                    <div>
                      <Label>Amount (₹)</Label>
                      <Input
                        type="number"
                        value={newTransaction.amount}
                        onChange={(e) => setNewTransaction({ ...newTransaction, amount: e.target.value })}
                        placeholder="Enter amount"
                        data-testid="transaction-amount-input"
                      />
                    </div>
                    <div>
                      <Label>Notes</Label>
                      <Textarea
                        value={newTransaction.notes}
                        onChange={(e) => setNewTransaction({ ...newTransaction, notes: e.target.value })}
                        placeholder="Optional notes"
                        rows={2}
                        data-testid="transaction-notes-input"
                      />
                    </div>
                    <Button 
                      onClick={handleSaveTransaction} 
                      className="w-full"
                      disabled={!newTransaction.transaction_stage || !newTransaction.transaction_date || !newTransaction.bank_name || !newTransaction.transaction_number}
                      data-testid="save-transaction-btn"
                    >
                      {editingTransaction ? "Update Transaction" : "Add Transaction"}
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </CardHeader>
            <CardContent>
              {transactions.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Stage</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Bank Name</TableHead>
                      <TableHead>Transaction No.</TableHead>
                      <TableHead className="text-right">Amount</TableHead>
                      <TableHead>Notes</TableHead>
                      <TableHead className="text-center">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {transactions.map((txn) => (
                      <TableRow key={txn.id}>
                        <TableCell>
                          <Badge className={
                            txn.transaction_stage === 'booking' ? 'bg-blue-100 text-blue-700' :
                            txn.transaction_stage === 'agreement' ? 'bg-green-100 text-green-700' :
                            'bg-purple-100 text-purple-700'
                          }>
                            {txn.transaction_stage === 'scheduled_disbursement' ? 'Scheduled Disbursement' : 
                             (txn.transaction_stage ? txn.transaction_stage.charAt(0).toUpperCase() + txn.transaction_stage.slice(1) : 'Payment')}
                          </Badge>
                        </TableCell>
                        <TableCell>{txn.transaction_date}</TableCell>
                        <TableCell>{txn.bank_name}</TableCell>
                        <TableCell className="font-mono text-sm">{txn.transaction_number}</TableCell>
                        <TableCell className="text-right font-medium">{txn.amount ? formatCurrency(txn.amount) : '-'}</TableCell>
                        <TableCell className="max-w-xs truncate" title={txn.notes}>{txn.notes || '-'}</TableCell>
                        <TableCell className="text-center">
                          <div className="flex justify-center gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEditTransaction(txn)}
                              data-testid={`edit-transaction-${txn.id}`}
                            >
                              <Edit className="w-4 h-4" />
                            </Button>
                            {!isAccountsRole && (
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-red-500 hover:text-red-700"
                                onClick={() => handleDeleteTransaction(txn.id)}
                                data-testid={`delete-transaction-${txn.id}`}
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <CreditCard className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                  <p>No transactions recorded yet</p>
                  <p className="text-sm mt-1">Click "Add Transaction" to record a payment</p>
                </div>
              )}
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
                <>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">#</TableHead>
                      <TableHead>Particulars</TableHead>
                      <TableHead className="text-center">%</TableHead>
                      <TableHead className="text-center">Cumulative %</TableHead>
                      <TableHead className="text-right">Amount</TableHead>
                      <TableHead className="text-right">Cumulative Amt</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {paymentSchedule.items.map((item, index) => {
                      // Calculate cumulative percentage
                      const cumulativePct = paymentSchedule.items
                        .slice(0, index + 1)
                        .reduce((sum, i) => sum + (i.percentage || 0), 0);
                      return (
                        <TableRow key={item.id}>
                          <TableCell className="font-mono text-slate-500">{index + 1}</TableCell>
                          <TableCell className="font-medium max-w-xs">
                            <div className="truncate" title={item.installment_name}>
                              {item.installment_name}
                            </div>
                            {item.description && (
                              <div className="text-xs text-slate-500">{item.description}</div>
                            )}
                          </TableCell>
                          <TableCell className="text-center font-semibold">{item.percentage}%</TableCell>
                          <TableCell className="text-center font-semibold text-primary">{cumulativePct}%</TableCell>
                          <TableCell className="text-right font-mono">{formatCurrency(item.amount)}</TableCell>
                          <TableCell className="text-right font-mono text-primary font-semibold">{formatCurrency(item.cumulative)}</TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
                </>
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
                          <SelectItem value="price_breakup">Price Breakup</SelectItem>
                          <SelectItem value="cost_breakup">Cost Breakup</SelectItem>
                          <SelectItem value="disbursement_letter">Disbursement Letter</SelectItem>
                          <SelectItem value="payment_schedule">Payment Schedule</SelectItem>
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
                        {!isAccountsRole && (
                          <Button
                            variant="outline"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteDocClick(doc, 'generated')}
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

          {/* Disbursement - Bank NOC Documents Subsection */}
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
                {/* HDFC Bank NOC */}
                <div className="p-4 border rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors">
                  <div className="flex flex-col items-center text-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                      <Building2 className="w-6 h-6 text-red-600" />
                    </div>
                    <div>
                      <p className="font-semibold text-slate-800">HDFC Bank</p>
                      <p className="text-xs text-slate-500">No Objection Certificate</p>
                    </div>
                    <Button
                      onClick={() => handleGenerateNoc("noc_hdfc", "HDFC Bank")}
                      disabled={generatingNoc === "noc_hdfc"}
                      className="w-full bg-red-600 hover:bg-red-700"
                      size="sm"
                      data-testid="generate-noc-hdfc"
                    >
                      {generatingNoc === "noc_hdfc" ? (
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

                {/* Bank of Baroda NOC */}
                <div className="p-4 border rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors">
                  <div className="flex flex-col items-center text-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center">
                      <Building2 className="w-6 h-6 text-orange-600" />
                    </div>
                    <div>
                      <p className="font-semibold text-slate-800">Bank of Baroda</p>
                      <p className="text-xs text-slate-500">No Objection Certificate</p>
                    </div>
                    <Button
                      onClick={() => handleGenerateNoc("noc_bob", "Bank of Baroda")}
                      disabled={generatingNoc === "noc_bob"}
                      className="w-full bg-orange-600 hover:bg-orange-700"
                      size="sm"
                      data-testid="generate-noc-bob"
                    >
                      {generatingNoc === "noc_bob" ? (
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

                {/* TATA Capital NOC */}
                <div className="p-4 border rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors">
                  <div className="flex flex-col items-center text-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                      <Building2 className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <p className="font-semibold text-slate-800">TATA Capital</p>
                      <p className="text-xs text-slate-500">No Objection Certificate</p>
                    </div>
                    <Button
                      onClick={() => handleGenerateNoc("noc_tata", "TATA Capital")}
                      disabled={generatingNoc === "noc_tata"}
                      className="w-full bg-blue-600 hover:bg-blue-700"
                      size="sm"
                      data-testid="generate-noc-tata"
                    >
                      {generatingNoc === "noc_tata" ? (
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
              </div>

              {/* List any generated NOC documents */}
              {documents.filter(doc => ['noc_hdfc', 'noc_bob', 'noc_tata'].includes(doc.doc_type)).length > 0 && (
                <div className="mt-6 pt-6 border-t">
                  <h4 className="text-sm font-medium text-slate-700 mb-3">Generated NOC Documents</h4>
                  <div className="space-y-3">
                    {documents.filter(doc => ['noc_hdfc', 'noc_bob', 'noc_tata'].includes(doc.doc_type)).map((doc) => (
                      <div key={doc.id} className="flex items-center justify-between p-3 border rounded-lg bg-white">
                        <div className="flex items-center gap-3">
                          <FileText className="w-6 h-6 text-primary" />
                          <div>
                            <p className="font-medium text-sm capitalize">
                              {doc.doc_type === 'noc_hdfc' && 'HDFC Bank NOC'}
                              {doc.doc_type === 'noc_bob' && 'Bank of Baroda NOC'}
                              {doc.doc_type === 'noc_tata' && 'TATA Capital NOC'}
                            </p>
                            <p className="text-xs text-slate-500">
                              Generated: {new Date(doc.generated_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handlePreviewDocument(doc)}
                            data-testid={`preview-noc-${doc.id}`}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDownloadDocument(doc)}
                            data-testid={`download-noc-${doc.id}`}
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                          {!isAccountsRole && (
                            <Button
                              variant="outline"
                              size="sm"
                              className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              onClick={() => handleDeleteDocClick(doc, 'generated')}
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
                        {!isAccountsRole && (
                          <Button
                            variant="outline"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteDocClick(doc, 'uploaded')}
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
                    
                    {/* Attachment Section */}
                    {commType === "email" && (
                      <div className="space-y-3">
                        <Label className="flex items-center gap-2">
                          <Paperclip className="w-4 h-4" />
                          Attachments
                        </Label>
                        
                        {/* Available Documents */}
                        {(documents.length > 0 || uploadedDocs.length > 0) && (
                          <div className="p-3 bg-slate-50 rounded-lg space-y-2">
                            <p className="text-sm font-medium text-slate-600">Select from available documents:</p>
                            <div className="flex flex-wrap gap-2">
                              {documents.map((doc) => (
                                <Button
                                  key={doc.id}
                                  type="button"
                                  variant={selectedAttachments.includes(doc.id) ? "default" : "outline"}
                                  size="sm"
                                  onClick={() => toggleAttachment(doc.id)}
                                  className="text-xs"
                                >
                                  <FileText className="w-3 h-3 mr-1" />
                                  {doc.doc_type.replace(/_/g, " ")}
                                  {selectedAttachments.includes(doc.id) && (
                                    <CheckCircle className="w-3 h-3 ml-1" />
                                  )}
                                </Button>
                              ))}
                              {uploadedDocs.map((doc) => (
                                <Button
                                  key={doc.id}
                                  type="button"
                                  variant={selectedAttachments.includes(doc.id) ? "default" : "outline"}
                                  size="sm"
                                  onClick={() => toggleAttachment(doc.id)}
                                  className="text-xs"
                                >
                                  <FileText className="w-3 h-3 mr-1" />
                                  {doc.filename || doc.doc_type}
                                  {selectedAttachments.includes(doc.id) && (
                                    <CheckCircle className="w-3 h-3 ml-1" />
                                  )}
                                </Button>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Upload from local disk */}
                        <div className="space-y-2">
                          <input
                            type="file"
                            ref={localFileRef}
                            className="hidden"
                            onChange={handleLocalFileSelect}
                            accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                          />
                          {localAttachment ? (
                            <div className="flex items-center gap-2 p-2 bg-green-50 border border-green-200 rounded">
                              <FileText className="w-4 h-4 text-green-600" />
                              <span className="text-sm truncate flex-1">{localAttachment.name}</span>
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={() => setLocalAttachment(null)}
                              >
                                <X className="w-4 h-4" />
                              </Button>
                            </div>
                          ) : (
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => localFileRef.current?.click()}
                              className="w-full"
                            >
                              <Upload className="w-4 h-4 mr-2" />
                              Upload from Computer
                            </Button>
                          )}
                        </div>
                        
                        {selectedAttachments.length > 0 && (
                          <p className="text-xs text-green-600">
                            {selectedAttachments.length} document(s) selected for attachment
                          </p>
                        )}
                      </div>
                    )}
                    
                    <p className="text-xs text-green-600 bg-green-50 p-2 rounded">
                      Emails are sent via SendGrid. WhatsApp is MOCKED.
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
        
        {/* Notes Tab */}
        <TabsContent value="notes">
          <NotesTab
            notes={notes}
            onAddNote={async (content) => {
              try {
                const res = await axios.post(`${API}/customers/${id}/notes`, { content });
                setNotes([res.data, ...notes]);
                toast.success("Note added");
              } catch (error) {
                toast.error("Failed to add note");
                throw error;
              }
            }}
            onDeleteNote={async (noteId) => {
              try {
                await axios.delete(`${API}/customers/${id}/notes/${noteId}`);
                setNotes(notes.filter(n => n.id !== noteId));
                toast.success("Note deleted");
              } catch (error) {
                toast.error("Failed to delete note");
              }
            }}
            isAccountsRole={isAccountsRole}
          />
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

      {/* Document Delete Confirmation Dialog */}
      <AlertDialog open={docDeleteDialogOpen} onOpenChange={setDocDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Document?</AlertDialogTitle>
            <AlertDialogDescription>
              {docToDelete && (
                <>
                  Are you sure you want to delete <strong>"{docToDelete.doc_type?.replace(/_/g, " ") || docToDelete.filename}"</strong>?
                  <br /><br />
                  <span className="text-red-600 font-medium">This action cannot be undone.</span>
                </>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={docDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDeleteDoc}
              disabled={docDeleting}
              className="bg-red-600 hover:bg-red-700"
              data-testid="confirm-delete-doc-btn"
            >
              {docDeleting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Deleting...
                </>
              ) : (
                <>
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete
                </>
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Unified Email Composer Dialog */}
      <Dialog open={emailComposerOpen} onOpenChange={setEmailComposerOpen}>
        <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Mail className="w-5 h-5 text-primary" />
              {emailComposerData?.email_type === 'welcome' && 'Send Welcome Email'}
              {emailComposerData?.email_type === 'sales_agreement' && 'Send Sales Agreement'}
              {emailComposerData?.email_type === 'allotment_letter' && 'Send Allotment Letter'}
            </DialogTitle>
          </DialogHeader>
          
          {emailComposerData && (
            <div className="space-y-4">
              {/* Editable Email Fields */}
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-xs text-slate-500">To (Editable)</Label>
                    <Input 
                      value={editedEmailTo} 
                      onChange={(e) => setEditedEmailTo(e.target.value)}
                      placeholder="recipient@email.com"
                      className="border-primary/50"
                    />
                  </div>
                  <div>
                    <Label className="text-xs text-slate-500">CC (Optional)</Label>
                    <Input 
                      value={editedEmailCc} 
                      onChange={(e) => setEditedEmailCc(e.target.value)}
                      placeholder="cc@email.com"
                      className="border-primary/50"
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-xs text-slate-500">Customer</Label>
                    <Input 
                      value={emailComposerData.customer_name} 
                      readOnly 
                      className="bg-slate-50"
                    />
                  </div>
                </div>
                
                <div>
                  <Label className="text-xs text-slate-500">Subject (Editable)</Label>
                  <Input 
                    value={editedEmailSubject} 
                    onChange={(e) => setEditedEmailSubject(e.target.value)}
                    className="border-primary/50"
                  />
                </div>
                
                <div>
                  <Label className="text-xs text-slate-500">Email Body (Editable)</Label>
                  <textarea 
                    value={editedEmailBody}
                    onChange={(e) => setEditedEmailBody(e.target.value)}
                    rows={5}
                    className="w-full border border-primary/50 rounded-md p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary/20"
                  />
                </div>
                
                {/* Attachments Info */}
                <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                  <FileText className="w-5 h-5 text-red-500" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Attachments (Auto-generated)</p>
                    <div className="flex flex-wrap gap-2 mt-1">
                      <Badge variant="outline" className="text-xs">
                        {emailComposerData.attachment_filename}
                      </Badge>
                      {emailComposerData.attachment_filename_2 && (
                        <Badge variant="outline" className="text-xs">
                          {emailComposerData.attachment_filename_2}
                        </Badge>
                      )}
                      {emailComposerData.attachment_filename_3 && (
                        <Badge variant="outline" className="text-xs">
                          {emailComposerData.attachment_filename_3}
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Preview Tabs */}
              <div>
                <Tabs defaultValue="preview">
                  <TabsList className={`grid w-full max-w-2xl ${emailComposerData.email_type === 'welcome' ? 'grid-cols-4' : 'grid-cols-3'}`}>
                    <TabsTrigger value="preview">Email Preview</TabsTrigger>
                    <TabsTrigger value="attachment1">
                      {emailComposerData.email_type === 'welcome' ? 'Form Preview' : 
                       emailComposerData.email_type === 'sales_agreement' ? 'Sales Agreement' : 
                       'Allotment Letter'}
                    </TabsTrigger>
                    {emailComposerData.attachment_html_2 && (
                      <TabsTrigger value="attachment2">
                        {emailComposerData.email_type === 'welcome' ? 'Terms & Conditions' : 'Price Breakup'}
                      </TabsTrigger>
                    )}
                    {emailComposerData.attachment_html_3 && (
                      <TabsTrigger value="attachment3">Price Breakup</TabsTrigger>
                    )}
                  </TabsList>
                  
                  <TabsContent value="preview" className="max-h-[300px] overflow-auto border rounded-lg mt-2 bg-white">
                    <div dangerouslySetInnerHTML={{ __html: emailComposerData.email_html || "" }} />
                  </TabsContent>
                  
                  <TabsContent value="attachment1" className="max-h-[300px] overflow-auto border rounded-lg mt-2 bg-white">
                    <div dangerouslySetInnerHTML={{ __html: emailComposerData.attachment_html || "" }} />
                  </TabsContent>
                  
                  {emailComposerData.attachment_html_2 && (
                    <TabsContent value="attachment2" className="max-h-[300px] overflow-auto border rounded-lg mt-2 bg-white">
                      <div dangerouslySetInnerHTML={{ __html: emailComposerData.attachment_html_2 || "" }} />
                    </TabsContent>
                  )}
                  
                  {emailComposerData.attachment_html_3 && (
                    <TabsContent value="attachment3" className="max-h-[300px] overflow-auto border rounded-lg mt-2 bg-white">
                      <div dangerouslySetInnerHTML={{ __html: emailComposerData.attachment_html_3 || "" }} />
                    </TabsContent>
                  )}
                </Tabs>
              </div>
              
              {/* Action Buttons */}
              <div className="flex justify-between items-center pt-4 border-t">
                <div className="text-sm text-slate-500">
                  {emailComposerData.has_sendgrid ? (
                    <span className="text-green-600">✓ SendGrid configured</span>
                  ) : (
                    <span className="text-amber-600">⚠ Email will be simulated</span>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" onClick={() => setEmailComposerOpen(false)}>
                    Cancel
                  </Button>
                  <Button 
                    onClick={handleSendDocumentEmail} 
                    disabled={sendingEmail}
                    className="bg-green-600 hover:bg-green-700"
                    data-testid="confirm-send-email-btn"
                  >
                    {sendingEmail ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Sending...
                      </>
                    ) : (
                      <>
                        <Mail className="w-4 h-4 mr-2" />
                        Send Email
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CustomerDetailPage;
