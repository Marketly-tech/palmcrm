import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import DOMPurify from "dompurify";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { openSafePreviewWindow } from "../utils/safePreview";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export function useCustomerPage(id) {
  const navigate = useNavigate();
  const { user } = useAuth();
  const isAccountsRole = user?.role === "accounts";

  // Core data
  const [customer, setCustomer] = useState(null);
  const [paymentSchedule, setPaymentSchedule] = useState({ items: [] });
  const [checklist, setChecklist] = useState({ items: {} });
  const [documents, setDocuments] = useState([]);
  const [uploadedDocs, setUploadedDocs] = useState([]);
  const [communications, setCommunications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [overdueInfo, setOverdueInfo] = useState(null);
  const [notes, setNotes] = useState([]);

  // Customer edit
  const [editing, setEditing] = useState(false);
  const [editData, setEditData] = useState({});
  const [saving, setSaving] = useState(false);
  const [liveCalc, setLiveCalc] = useState(null);

  // Disbursement
  const [disbursementPercentage, setDisbursementPercentage] = useState(30);

  // Booking edit
  const [editingBooking, setEditingBooking] = useState(false);
  const [savingBooking, setSavingBooking] = useState(false);
  const [bookingForm, setBookingForm] = useState({
    finance_type: "",
    finance_bank: "",
    booking_amount: "",
    booking_date: "",
  });

  // Due date
  const [editingDueDate, setEditingDueDate] = useState(false);
  const [paymentDueDate, setPaymentDueDate] = useState("");

  // Bank details
  const [bankDetailsEditing, setBankDetailsEditing] = useState(false);
  const [bankDetails, setBankDetails] = useState({
    bank_name: "",
    bank_name_other: "",
    bank_account_number: "",
    bank_ifsc_code: "",
    bank_branch: "",
    bank_account_holder: "",
  });

  // Document delete
  const [docDeleteDialogOpen, setDocDeleteDialogOpen] = useState(false);
  const [docToDelete, setDocToDelete] = useState(null);
  const [docDeleteType, setDocDeleteType] = useState(null);
  const [docDeleting, setDocDeleting] = useState(false);

  // Calculator
  const [calcEditing, setCalcEditing] = useState(false);
  const [calcData, setCalcData] = useState({});
  const [calcLivePrice, setCalcLivePrice] = useState(null);
  const [calcSaving, setCalcSaving] = useState(false);

  // Document preview
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);
  const [previewContent, setPreviewContent] = useState(null);
  const [previewDoc, setPreviewDoc] = useState(null);

  // Email composer
  const [sendingWelcome, setSendingWelcome] = useState(false);
  const [emailComposerOpen, setEmailComposerOpen] = useState(false);
  const [emailComposerData, setEmailComposerData] = useState(null);
  const [editedEmailSubject, setEditedEmailSubject] = useState("");
  const [editedEmailBody, setEditedEmailBody] = useState("");
  const [editedEmailTo, setEditedEmailTo] = useState("");
  const [editedEmailCc, setEditedEmailCc] = useState("");
  const [sendingEmail, setSendingEmail] = useState(false);

  // NOC
  const [generatingNoc, setGeneratingNoc] = useState(null);

  // Transactions
  const [transactions, setTransactions] = useState([]);
  const [transactionDialogOpen, setTransactionDialogOpen] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState(null);
  const [newTransaction, setNewTransaction] = useState({
    transaction_stage: "",
    transaction_date: "",
    bank_name: "",
    transaction_number: "",
    amount: "",
    notes: "",
  });

  // ─── Data Fetching ───────────────────────────────────────────
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const fetchCustomerData = useCallback(async () => {
    try {
      const [
        customerRes, scheduleRes, checklistRes, docsRes,
        commsRes, uploadedDocsRes, transactionsRes, overdueRes, notesRes,
      ] = await Promise.all([
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
      const c = customerRes.data;
      setCustomer(c);
      setEditData({ ...c, floor_rise_cost: c.custom_fields?.floor_rise_cost || 0 });
      setBookingForm({
        finance_type: c.finance_type || "self",
        finance_bank: c.finance_bank || "",
        booking_amount: c.booking_amount || "",
        booking_date: c.booking_date || "",
      });
      setPaymentSchedule(scheduleRes.data);
      setChecklist(checklistRes.data);
      setDocuments(docsRes.data);
      setUploadedDocs(uploadedDocsRes.data);
      setCommunications(commsRes.data);
      setTransactions(transactionsRes.data || []);
      setOverdueInfo(overdueRes.data);
      setNotes(notesRes.data || []);
      setPaymentDueDate(c.payment_due_date || "");
      setBankDetails({
        bank_name: c.bank_name || "",
        bank_name_other: c.bank_name_other || "",
        bank_account_number: c.bank_account_number || "",
        bank_ifsc_code: c.bank_ifsc_code || "",
        bank_branch: c.bank_branch || "",
        bank_account_holder: c.bank_account_holder || "",
      });
    } catch {
      toast.error("Failed to fetch customer data");
      navigate("/customers");
    } finally {
      setLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => { fetchCustomerData(); }, [id, fetchCustomerData]);

  // ─── Price Calculator ────────────────────────────────────────
  const calculateLivePrice = (data) => {
    const saleableArea = parseFloat(data.saleable_area) || 0;
    const ratePerSqft = parseFloat(data.rate_per_sqft) || 0;
    const floorRiseCost = parseFloat(data.floor_rise_cost) || 0;
    const basePrice = saleableArea * ratePerSqft;
    const floorRiseTotal = saleableArea * floorRiseCost;
    const clubHouse = parseFloat(data.club_house_charges) || 300000;
    const additionalCharges = parseFloat(data.additional_charges) || 0;
    // Car parking is now a fixed editable amount on the customer (default ₹2L),
    // NOT a count multiplied by ₹3L per slot.
    const parkingCharges = parseFloat(data.additional_parking_charges) || 200000;
    // BESCOM: rate per sqft × saleable area → adds to subtotal (before GST/labour cess)
    const bescomRate = parseFloat(data.bescom_rate) || 0;
    const bescomAmount = bescomRate * saleableArea;
    const subtotal = basePrice + floorRiseTotal + clubHouse + parkingCharges + additionalCharges + bescomAmount;
    const labourCess = subtotal * 0.007;
    const gst = subtotal * 0.05;
    // Interest is a manual flat add-on AFTER GST (non GST-taxable)
    const interestAmount = parseFloat(data.interest_amount) || 0;
    const total = subtotal + labourCess + gst + interestAmount;
    const uds = saleableArea * 0.495046;
    return {
      basePrice: Math.round(basePrice),
      floorRiseCost,
      floorRiseTotal: Math.round(floorRiseTotal),
      effectiveRate: ratePerSqft + floorRiseCost,
      clubHouse: Math.round(clubHouse),
      additionalCharges: Math.round(additionalCharges),
      parkingCharges: Math.round(parkingCharges),
      bescomRate,
      bescomAmount: Math.round(bescomAmount),
      subtotal: Math.round(subtotal),
      labourCess: Math.round(labourCess),
      gst: Math.round(gst),
      interestAmount: Math.round(interestAmount),
      total: Math.round(total),
      uds: Math.round(uds * 100) / 100,
    };
  };

  useEffect(() => {
    if (editing && editData) setLiveCalc(calculateLivePrice(editData));
  }, [editing, editData]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleEditChange = (field, value) => {
    setEditData((prev) => ({ ...prev, [field]: value }));
  };

  // ─── Customer Save ───────────────────────────────────────────
  const handleSaveCustomer = async () => {
    setSaving(true);
    try {
      let dataToSave = { ...editData };
      if (liveCalc) {
        dataToSave = {
          ...dataToSave,
          base_price: liveCalc.basePrice,
          club_house_charges: liveCalc.clubHouse,
          additional_charges: liveCalc.additionalCharges,
          additional_parking_charges: liveCalc.parkingCharges,
          bescom_rate: liveCalc.bescomRate,
          bescom_amount: liveCalc.bescomAmount,
          labour_cess: liveCalc.labourCess,
          gst_amount: liveCalc.gst,
          interest_amount: liveCalc.interestAmount,
          total_price: liveCalc.total,
          uds: liveCalc.uds,
          custom_fields: {
            ...(customer.custom_fields || {}),
            floor_rise_cost: editData.floor_rise_cost || 0,
            floor_rise_total: liveCalc.floorRiseTotal || 0,
          },
        };
      }
      const protectedFields = [
        "booking_amount", "booking_date", "transaction_date", "transaction_bank",
        "transaction_details", "total_received", "balance_amount",
        "payment_received_percentage", "payment_pending_percentage", "id", "created_at", "_id",
      ];
      protectedFields.forEach((f) => delete dataToSave[f]);
      await axios.put(`${API}/customers/${id}`, dataToSave);
      fetchCustomerData();
      setEditing(false);
      setLiveCalc(null);
      toast.success("Customer updated with recalculated prices");
    } catch {
      toast.error("Failed to update customer");
    } finally {
      setSaving(false);
    }
  };

  // ─── Booking Details ─────────────────────────────────────────
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
    } catch {
      toast.error("Failed to update booking details");
    } finally {
      setSavingBooking(false);
    }
  };

  // ─── Agreement Status ────────────────────────────────────────
  const handleAgreementStatusChange = async (newStatus) => {
    try {
      await axios.put(`${API}/customers/${id}`, { agreement_status: newStatus });
      setCustomer({ ...customer, agreement_status: newStatus });
      toast.success(`Agreement status updated to ${newStatus}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to update agreement status");
    }
  };

  // ─── Payment Schedule ────────────────────────────────────────
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
      setPaymentSchedule((prev) => ({
        ...prev,
        items: prev.items.map((item) =>
          item.id === itemId
            ? { ...item, payment_status: status, payment_date: status === "paid" ? new Date().toISOString().split("T")[0] : null }
            : item
        ),
      }));
      if (response.data) {
        setCustomer((prev) => ({
          ...prev,
          total_received: response.data.total_received,
          balance_amount: response.data.balance_amount,
          payment_received_percentage: response.data.payment_received_percentage,
          payment_pending_percentage: response.data.payment_pending_percentage,
        }));
      }
      toast.success(`Payment marked as ${status} - Received: ₹${response.data.total_received?.toLocaleString("en-IN")}`);
    } catch {
      toast.error("Failed to update payment");
    }
  };

  // ─── Checklist ───────────────────────────────────────────────
  const handleUpdateChecklist = async (key, value) => {
    const newItems = { ...checklist.items, [key]: value };
    try {
      await axios.put(`${API}/checklist/${id}`, newItems);
      setChecklist({ ...checklist, items: newItems });
    } catch {
      toast.error("Failed to update checklist");
    }
  };

  // ─── Due Date ────────────────────────────────────────────────
  const handleUpdateDueDate = async () => {
    try {
      await axios.put(`${API}/customers/${id}/payment-due-date`, { payment_due_date: paymentDueDate });
      setCustomer({ ...customer, payment_due_date: paymentDueDate });
      setEditingDueDate(false);
      toast.success("Payment due date updated");
    } catch {
      toast.error("Failed to update due date");
    }
  };

  // ─── Bank Details ────────────────────────────────────────────
  const handleSaveBankDetails = async () => {
    try {
      const updateData = { ...bankDetails };
      await axios.put(`${API}/customers/${id}`, updateData);
      setCustomer({ ...customer, ...updateData });
      setBankDetailsEditing(false);
      toast.success("Bank details updated successfully");
    } catch {
      toast.error("Failed to update bank details");
    }
  };

  // ─── Transactions ────────────────────────────────────────────
  const refreshTransactions = async () => {
    const [transactionsRes, overdueRes] = await Promise.all([
      axios.get(`${API}/transactions/${id}`),
      axios.get(`${API}/customers/${id}/overdue`).catch(() => ({ data: null })),
    ]);
    setTransactions(transactionsRes.data || []);
    setOverdueInfo(overdueRes.data);
  };

  const handleSaveTransaction = async () => {
    try {
      const transactionData = { ...newTransaction, amount: parseFloat(newTransaction.amount) || 0 };
      if (editingTransaction) {
        await axios.put(`${API}/transactions/${id}/${editingTransaction.id}`, transactionData);
        toast.success("Transaction updated successfully");
      } else {
        await axios.post(`${API}/transactions/${id}`, transactionData);
        toast.success("Transaction added successfully");
      }
      await refreshTransactions();
      setTransactionDialogOpen(false);
      setEditingTransaction(null);
      setNewTransaction({ transaction_stage: "", transaction_date: "", bank_name: "", transaction_number: "", amount: "", notes: "" });
    } catch {
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
      notes: txn.notes || "",
    });
    setTransactionDialogOpen(true);
  };

  const handleDeleteTransaction = async (transactionId) => {
    if (!window.confirm("Are you sure you want to delete this transaction?")) return;
    try {
      await axios.delete(`${API}/transactions/${id}/${transactionId}`);
      await refreshTransactions();
      toast.success("Transaction deleted");
    } catch {
      toast.error("Failed to delete transaction");
    }
  };

  const handleGenerateReceipt = async (txn) => {
    try {
      const res = await axios.post(`${API}/documents/payment-receipt/${id}/${txn.id}`);
      // Open the EditableDocumentDialog with the generated receipt
      setPreviewDoc({
        id: res.data.id,
        doc_type: res.data.doc_type,
      });
      setPreviewDialogOpen(true);
      // refresh transactions so receipt_number is shown on the row
      await refreshTransactions();
      toast.success(`Receipt ${res.data.receipt_number} ready — edit if needed, then download`);
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Failed to generate receipt");
    }
  };

  // ─── Documents ───────────────────────────────────────────────
  const handlePreviewDocument = async (doc) => {
    setPreviewDoc(doc);
    setPreviewDialogOpen(true);
  };

  const handleDownloadDocument = async (doc) => {
    try {
      const response = await axios.get(`${API}/documents/pdf/${doc.id}`, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }));
      const link = document.createElement("a");
      link.href = url;
      const docType = (doc.doc_type || "Document").replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase()).replace(/ /g, "_");
      link.setAttribute("download", `RRL_${docType}_${(customer?.name || "Customer").replace(/ /g, "_")}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      toast.error("Failed to download document");
    }
  };

  const handleGenerateNoc = async (nocType, bankName) => {
    setGeneratingNoc(nocType);
    try {
      const response = await axios.post(`${API}/documents/generate`, { customer_id: id, doc_type: nocType });
      setDocuments([...documents, response.data.document]);
      toast.success(`${bankName} NOC generated successfully`);
    } catch {
      toast.error(`Failed to generate ${bankName} NOC`);
    } finally {
      setGeneratingNoc(null);
    }
  };

  const handleDeleteDocClick = (doc, type) => {
    setDocToDelete(doc);
    setDocDeleteType(type);
    setDocDeleteDialogOpen(true);
  };

  const handleConfirmDeleteDoc = async () => {
    if (!docToDelete) return;
    setDocDeleting(true);
    try {
      const endpoint = docDeleteType === "generated"
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

  const handleGeneratePriceBreakup = async () => {
    try {
      const response = await axios.post(`${API}/documents/generate-pdf/${id}`);
      toast.success("Price breakup generated");
      if (response.data.html_content) openSafePreviewWindow(response.data.html_content);
      fetchCustomerData();
    } catch {
      toast.error("Failed to generate price breakup");
    }
  };

  const handleDownloadUploadedDoc = async (doc) => {
    try {
      const response = await axios.get(`${API}/documents/download/${doc.id}`, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", doc.filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      toast.error("Failed to download document");
    }
  };

  const handlePreviewUploadedDoc = async (doc) => {
    try {
      const response = await axios.get(`${API}/documents/preview/${doc.id}`);
      const { content_base64, content_type, filename } = response.data;
      const dataUrl = `data:${content_type};base64,${content_base64}`;
      if (content_type.startsWith("image/")) {
        setPreviewContent(DOMPurify.sanitize(`<img src="${dataUrl}" style="max-width: 100%; height: auto;" alt="${DOMPurify.sanitize(filename)}" />`));
        setPreviewDialogOpen(true);
      } else if (content_type === "application/pdf") {
        const pdfHtml = `<!DOCTYPE html><html><head><title>PDF Preview</title></head><body style="margin:0;"><iframe src="${DOMPurify.sanitize(dataUrl)}" style="width:100%;height:100vh;border:none;"></iframe></body></html>`;
        const blob = new Blob([pdfHtml], { type: "text/html; charset=utf-8" });
        const blobUrl = URL.createObjectURL(blob);
        const pdfWindow = window.open(blobUrl, "_blank");
        if (pdfWindow) setTimeout(() => URL.revokeObjectURL(blobUrl), 60000);
      } else {
        handleDownloadUploadedDoc(doc);
      }
    } catch {
      toast.error("Failed to preview document");
    }
  };

  // ─── Email Composer ──────────────────────────────────────────
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
    } catch {
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
    } catch {
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
    } catch {
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
        cc: editedEmailCc || null,
      });
      toast.success(response.data.message);
      setEmailComposerOpen(false);
      setEmailComposerData(null);
      fetchCustomerData();
    } catch {
      toast.error("Failed to send email");
    } finally {
      setSendingEmail(false);
    }
  };

  const handleSendWhatsAppWelcome = () => {
    let phone = customer.phone?.replace(/[\s\-\(\)]/g, "") || "";
    if (!phone.startsWith("+") && !phone.startsWith("91")) {
      phone = "91" + phone;
    } else if (phone.startsWith("+")) {
      phone = phone.substring(1);
    }
    const message = `Hi ${customer.name}, This is from RRL Builders. Congratulations on your new home purchase! We are happy to welcome you to the RRL family.\n\nProperty Details:\n- Project: ${customer.project}\n- Unit: ${customer.unit_number}\n- Tower: ${customer.tower}\n\nThank you for choosing RRL Builders and Developers Pvt. Ltd.`;
    const whatsappUrl = `https://web.whatsapp.com/send?phone=${phone}&text=${encodeURIComponent(message)}`;
    window.open(whatsappUrl, "_blank");
    axios.post(`${API}/communication/whatsapp?customer_id=${id}&message=${encodeURIComponent("Welcome message sent via WhatsApp")}`).catch(() => {});
    toast.success("Opening WhatsApp Web...");
  };

  // ─── Calculator Tab ──────────────────────────────────────────
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
    setCalcLivePrice(calculateLivePrice(newCalcData));
  };

  useEffect(() => {
    if (calcEditing && calcData.saleable_area) setCalcLivePrice(calculateLivePrice(calcData));
  }, [calcEditing, calcData]); // eslint-disable-line react-hooks/exhaustive-deps

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
        },
      };
      await axios.put(`${API}/customers/${id}`, updates);
      fetchCustomerData();
      setCalcEditing(false);
      setCalcLivePrice(null);
      toast.success("Calculator values saved and profile updated!");
    } catch {
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

  // ─── Utilities ───────────────────────────────────────────────
  const formatCurrency = (amount) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount || 0);

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

  return {
    // Router / Auth
    navigate, user, isAccountsRole,
    // Core data
    customer, loading, paymentSchedule, setPaymentSchedule,
    checklist, documents, setDocuments, uploadedDocs, setUploadedDocs,
    communications, setCommunications, overdueInfo, notes, setNotes,
    fetchCustomerData,
    // Customer edit
    editing, setEditing, editData, setEditData, saving, liveCalc,
    handleEditChange, handleSaveCustomer,
    // Booking
    editingBooking, setEditingBooking, savingBooking,
    bookingForm, setBookingForm, handleSaveBookingDetails,
    // Bank details
    bankDetailsEditing, setBankDetailsEditing,
    bankDetails, setBankDetails, handleSaveBankDetails,
    // Due date
    editingDueDate, setEditingDueDate,
    paymentDueDate, setPaymentDueDate, handleUpdateDueDate,
    // Agreement
    handleAgreementStatusChange,
    // Payment schedule
    handleGeneratePaymentSchedule, handleUpdatePaymentStatus,
    // Checklist
    handleUpdateChecklist,
    // Disbursement
    disbursementPercentage, setDisbursementPercentage,
    // Transactions
    transactions, transactionDialogOpen, setTransactionDialogOpen,
    editingTransaction, setEditingTransaction,
    newTransaction, setNewTransaction,
    handleSaveTransaction, handleEditTransaction, handleDeleteTransaction,
    handleGenerateReceipt,
    // Documents
    previewDialogOpen, setPreviewDialogOpen, previewContent, previewDoc,
    docDeleteDialogOpen, setDocDeleteDialogOpen, docToDelete,
    docDeleteType, docDeleting, generatingNoc,
    handlePreviewDocument, handleDownloadDocument,
    handleGenerateNoc, handleDeleteDocClick, handleConfirmDeleteDoc,
    handlePreviewUploadedDoc, handleDownloadUploadedDoc, handleGeneratePriceBreakup,
    // Email
    sendingWelcome, emailComposerOpen, setEmailComposerOpen,
    emailComposerData, editedEmailSubject, setEditedEmailSubject,
    editedEmailBody, setEditedEmailBody, editedEmailTo, setEditedEmailTo,
    editedEmailCc, setEditedEmailCc, sendingEmail,
    handlePreviewWelcomeEmail, handlePreviewSalesAgreement,
    handlePreviewAllotmentLetter, handleSendDocumentEmail,
    handleSendWhatsAppWelcome,
    // Calculator
    calcEditing, calcData, calcLivePrice, calcSaving,
    initCalcEdit, handleCalcChange, saveCalcChanges, cancelCalcEdit,
    // Utilities
    formatCurrency, getStatusBadge,
  };
}
