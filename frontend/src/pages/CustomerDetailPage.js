import { useState, useEffect, useCallback, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import DOMPurify from "dompurify";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { openSafePreviewWindow } from "../utils/safePreview";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
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
  CreditCard,
  FileText,
  MessageSquare,
  CheckCircle,
  Loader2,
  Mail,
  Edit,
  Save,
  Upload,
  Trash2,
  MessageCircle,
} from "lucide-react";

// Import refactored customer components
import {
  NotesTab,
  UploadsTab,
  CommunicationTab,
  PaymentTrackingCard,
  TransactionsCard,
  PaymentScheduleTab,
  DocumentsTab,
  ChecklistTab,
  DetailsTab,
  PaymentTrackingTab,
  EmailComposerDialog,
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

  // Booking Details Edit
  const [editingBooking, setEditingBooking] = useState(false);
  const [savingBooking, setSavingBooking] = useState(false);
  const [bookingForm, setBookingForm] = useState({
    finance_type: '', finance_bank: '', booking_amount: '', booking_date: ''
  });

  // Payment Dialog - now managed in PaymentScheduleTab component

  // Communication Dialog - now managed in CommunicationTab component
  
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

  // Document Generation - dialog state now managed in DocumentsTab
  
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
  
  // File Upload - dialog state now managed in UploadsTab

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

  // eslint-disable-next-line react-hooks/exhaustive-deps -- setState setters are stable references per React guarantees
  const fetchCustomerData = useCallback(async () => {
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
      // Initialize booking form
      setBookingForm({
        finance_type: customerData.finance_type || 'self',
        finance_bank: customerData.finance_bank || '',
        booking_amount: customerData.booking_amount || '',
        booking_date: customerData.booking_date || '',
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
  }, [id, navigate]);

  useEffect(() => {
    fetchCustomerData();
  }, [id, fetchCustomerData]);
  
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
          custom_fields: {
            ...(customer.custom_fields || {}),
            floor_rise_cost: editData.floor_rise_cost || 0,
            floor_rise_total: liveCalc.floorRiseTotal || 0,
          }
        };
      }
      
      // PROTECT: Never overwrite one-time booking details or computed payment fields
      const protectedFields = [
        'booking_amount', 'booking_date', 'transaction_date', 'transaction_bank',
        'transaction_details', 'total_received', 'balance_amount',
        'payment_received_percentage', 'payment_pending_percentage',
        'id', 'created_at', '_id'
      ];
      protectedFields.forEach(f => delete dataToSave[f]);
      
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

  const handleSaveBookingDetails = async () => {
    setSavingBooking(true);
    try {
      await axios.put(`${API}/customers/${id}/booking-details`, {
        finance_type: bookingForm.finance_type,
        finance_bank: bookingForm.finance_bank,
        booking_amount: parseFloat(bookingForm.booking_amount) || 0,
        booking_date: bookingForm.booking_date,
      });
      fetchCustomerData();
      setEditingBooking(false);
      toast.success("Booking details updated");
    } catch (error) {
      toast.error("Failed to update booking details");
    } finally {
      setSavingBooking(false);
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
      transaction_stage: txn.transaction_stage || txn.transaction_type || "",
      transaction_date: txn.transaction_date,
      bank_name: txn.bank_name || "",
      transaction_number: txn.transaction_number || "",
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
      openSafePreviewWindow(response.data.content);
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
      
      if (response.data.html_content) {
        openSafePreviewWindow(response.data.html_content);
      }
      
      fetchCustomerData();
    } catch (error) {
      toast.error("Failed to generate price breakup");
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
        setPreviewContent(DOMPurify.sanitize(`<img src="${dataUrl}" style="max-width: 100%; height: auto;" alt="${DOMPurify.sanitize(filename)}" />`));
        setPreviewDialogOpen(true);
      } else if (content_type === "application/pdf") {
        const pdfHtml = `<!DOCTYPE html><html><head><title>PDF Preview</title></head><body style="margin:0;"><iframe src="${DOMPurify.sanitize(dataUrl)}" style="width:100%;height:100vh;border:none;"></iframe></body></html>`;
        const blob = new Blob([pdfHtml], { type: 'text/html; charset=utf-8' });
        const blobUrl = URL.createObjectURL(blob);
        const pdfWindow = window.open(blobUrl, '_blank');
        if (pdfWindow) setTimeout(() => URL.revokeObjectURL(blobUrl), 60000);
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
            <p className="text-slate-500 font-mono">{customer.booking_number || customer.customer_id}</p>
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
                const totalReceived = transactions.reduce((sum, txn) => sum + (txn.amount || 0), 0);
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
          <DetailsTab
            customer={customer}
            editing={editing}
            editData={editData}
            setEditData={setEditData}
            liveCalc={liveCalc}
            formatCurrency={formatCurrency}
            handleEditChange={handleEditChange}
            editingBooking={editingBooking}
            setEditingBooking={setEditingBooking}
            savingBooking={savingBooking}
            bookingForm={bookingForm}
            setBookingForm={setBookingForm}
            handleSaveBookingDetails={handleSaveBookingDetails}
            bankDetailsEditing={bankDetailsEditing}
            setBankDetailsEditing={setBankDetailsEditing}
            bankDetails={bankDetails}
            setBankDetails={setBankDetails}
            handleSaveBankDetails={handleSaveBankDetails}
            user={user}
            isAccountsRole={isAccountsRole}
          />
        </TabsContent>

        {/* Payment Tracking Tab */}
        <TabsContent value="calculator">
          <PaymentTrackingTab
            customer={customer}
            transactions={transactions}
            overdueInfo={overdueInfo}
            formatCurrency={formatCurrency}
            isAccountsRole={isAccountsRole}
            disbursementPercentage={disbursementPercentage}
            setDisbursementPercentage={setDisbursementPercentage}
            editingDueDate={editingDueDate}
            setEditingDueDate={setEditingDueDate}
            paymentDueDate={paymentDueDate}
            setPaymentDueDate={setPaymentDueDate}
            handleUpdateDueDate={handleUpdateDueDate}
            transactionDialogOpen={transactionDialogOpen}
            setTransactionDialogOpen={setTransactionDialogOpen}
            editingTransaction={editingTransaction}
            setEditingTransaction={setEditingTransaction}
            newTransaction={newTransaction}
            setNewTransaction={setNewTransaction}
            handleSaveTransaction={handleSaveTransaction}
            handleEditTransaction={handleEditTransaction}
            handleDeleteTransaction={handleDeleteTransaction}
          />
        </TabsContent>

        {/* Payments Tab */}
        <TabsContent value="payments">
          <PaymentScheduleTab
            paymentSchedule={paymentSchedule}
            onGenerateSchedule={handleGeneratePaymentSchedule}
            onAddPayment={async (payment) => {
              try {
                const res = await axios.post(`${API}/payments/schedule`, {
                  customer_id: id,
                  items: [...paymentSchedule.items, {
                    id: Date.now().toString(),
                    ...payment,
                    amount: parseFloat(payment.amount),
                    percentage: parseFloat(payment.percentage) || 0,
                    status: "pending",
                  }],
                });
                setPaymentSchedule(res.data);
                toast.success("Payment added");
              } catch (error) {
                toast.error("Failed to add payment");
              }
            }}
          />
        </TabsContent>

        {/* Generated Documents Tab */}
        <TabsContent value="documents">
          <DocumentsTab
            documents={documents}
            isAccountsRole={isAccountsRole}
            onGenerateDocument={async (docType) => {
              try {
                const res = await axios.post(`${API}/documents/generate`, {
                  customer_id: id,
                  doc_type: docType,
                });
                setDocuments([...documents, res.data.document]);
                toast.success("Document generated");
              } catch (error) {
                toast.error("Failed to generate document");
              }
            }}
            onPreviewDocument={handlePreviewDocument}
            onDownloadDocument={handleDownloadDocument}
            onDeleteDocument={handleDeleteDocClick}
            onGenerateNoc={handleGenerateNoc}
            generatingNoc={generatingNoc}
          />
        </TabsContent>

        {/* Uploaded Documents Tab */}
        <TabsContent value="uploads">
          <UploadsTab
            uploadedDocs={uploadedDocs}
            isAccountsRole={isAccountsRole}
            onUpload={async (docType, file) => {
              const formData = new FormData();
              formData.append("file", file);
              formData.append("doc_type", docType);
              const res = await axios.post(`${API}/customers/${id}/upload-document`, formData, {
                headers: { "Content-Type": "multipart/form-data" },
              });
              setUploadedDocs([...uploadedDocs, res.data]);
              toast.success("Document uploaded");
            }}
            onPreview={handlePreviewUploadedDoc}
            onDownload={handleDownloadUploadedDoc}
            onDelete={handleDeleteDocClick}
          />
        </TabsContent>

        {/* Communication Tab */}
        <TabsContent value="communication">
          <CommunicationTab
            customerId={id}
            customerPhone={customer?.phone}
            communications={communications}
            documents={documents}
            uploadedDocs={uploadedDocs}
            onCommunicationSent={() => {
              axios.get(`${API}/communication/${id}`).then(res => setCommunications(res.data)).catch(() => {});
            }}
          />
        </TabsContent>

        {/* Checklist Tab */}
        <TabsContent value="checklist">
          <ChecklistTab
            checklist={checklist}
            onUpdateChecklist={handleUpdateChecklist}
          />
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
            dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(previewContent || "", { ADD_TAGS: ['style', 'link', 'img'], ADD_ATTR: ['target', 'src', 'alt'] }) }}
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
      <EmailComposerDialog
        open={emailComposerOpen}
        onOpenChange={setEmailComposerOpen}
        emailComposerData={emailComposerData}
        editedEmailSubject={editedEmailSubject}
        setEditedEmailSubject={setEditedEmailSubject}
        editedEmailBody={editedEmailBody}
        setEditedEmailBody={setEditedEmailBody}
        editedEmailTo={editedEmailTo}
        setEditedEmailTo={setEditedEmailTo}
        editedEmailCc={editedEmailCc}
        setEditedEmailCc={setEditedEmailCc}
        sendingEmail={sendingEmail}
        onSendEmail={handleSendDocumentEmail}
      />
    </div>
  );
};

export default CustomerDetailPage;
