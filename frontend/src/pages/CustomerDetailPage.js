import { useParams } from "react-router-dom";
import axios from "axios";
import { useCustomerPage } from "../hooks/useCustomerPage";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from "../components/ui/alert-dialog";
import { toast } from "sonner";
import {
  User, CreditCard, FileText, MessageSquare, CheckCircle,
  Loader2, Upload, Trash2,
} from "lucide-react";
import {
  NotesTab, UploadsTab, CommunicationTab, PaymentScheduleTab,
  DocumentsTab, ChecklistTab, DetailsTab, PaymentTrackingTab,
  EmailComposerDialog, CustomerHeader, CustomerQuickInfo,
} from "../components/customer";
import EditableDocumentDialog from "../components/customer/documents/EditableDocumentDialog";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CustomerDetailPage = () => {
  const { id } = useParams();
  const h = useCustomerPage(id);

  if (h.loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!h.customer) return null;

  return (
    <div className="space-y-6" data-testid="customer-detail-page">
      <CustomerHeader
        customer={h.customer} navigate={h.navigate}
        editing={h.editing} setEditing={h.setEditing} saving={h.saving}
        isAccountsRole={h.isAccountsRole}
        sendingWelcome={h.sendingWelcome} sendingEmail={h.sendingEmail}
        onSave={h.handleSaveCustomer}
        onPreviewWelcome={h.handlePreviewWelcomeEmail}
        onPreviewSalesAgreement={h.handlePreviewSalesAgreement}
        onPreviewAllotmentLetter={h.handlePreviewAllotmentLetter}
        onSendWhatsApp={h.handleSendWhatsAppWelcome}
      />

      <CustomerQuickInfo
        customer={h.customer} transactions={h.transactions}
        formatCurrency={h.formatCurrency} getStatusBadge={h.getStatusBadge}
        onAgreementStatusChange={h.handleAgreementStatusChange}
      />

      <Tabs defaultValue="details" className="space-y-4">
        <TabsList className="flex flex-wrap">
          <TabsTrigger value="details" data-testid="tab-details"><User className="w-4 h-4 mr-2" />Details</TabsTrigger>
          <TabsTrigger value="calculator" data-testid="tab-calculator"><CreditCard className="w-4 h-4 mr-2" />Payment Tracking</TabsTrigger>
          <TabsTrigger value="payments" data-testid="tab-payments"><CreditCard className="w-4 h-4 mr-2" />Payment Schedule</TabsTrigger>
          <TabsTrigger value="documents" data-testid="tab-documents"><FileText className="w-4 h-4 mr-2" />Documents</TabsTrigger>
          <TabsTrigger value="uploads" data-testid="tab-uploads"><Upload className="w-4 h-4 mr-2" />Uploads</TabsTrigger>
          <TabsTrigger value="communication" data-testid="tab-communication"><MessageSquare className="w-4 h-4 mr-2" />Communication</TabsTrigger>
          <TabsTrigger value="checklist" data-testid="tab-checklist"><CheckCircle className="w-4 h-4 mr-2" />Checklist</TabsTrigger>
          <TabsTrigger value="notes" data-testid="tab-notes"><FileText className="w-4 h-4 mr-2" />Notes</TabsTrigger>
        </TabsList>

        <TabsContent value="details">
          <DetailsTab
            customer={h.customer} editing={h.editing} editData={h.editData}
            setEditData={h.setEditData} liveCalc={h.liveCalc}
            formatCurrency={h.formatCurrency} handleEditChange={h.handleEditChange}
            editingBooking={h.editingBooking} setEditingBooking={h.setEditingBooking}
            savingBooking={h.savingBooking} bookingForm={h.bookingForm}
            setBookingForm={h.setBookingForm} handleSaveBookingDetails={h.handleSaveBookingDetails}
            bankDetailsEditing={h.bankDetailsEditing} setBankDetailsEditing={h.setBankDetailsEditing}
            bankDetails={h.bankDetails} setBankDetails={h.setBankDetails}
            handleSaveBankDetails={h.handleSaveBankDetails}
            user={h.user} isAccountsRole={h.isAccountsRole}
          />
        </TabsContent>

        <TabsContent value="calculator">
          <PaymentTrackingTab
            customer={h.customer} transactions={h.transactions}
            overdueInfo={h.overdueInfo} formatCurrency={h.formatCurrency}
            isAccountsRole={h.isAccountsRole}
            disbursementPercentage={h.disbursementPercentage}
            setDisbursementPercentage={h.setDisbursementPercentage}
            editingDueDate={h.editingDueDate} setEditingDueDate={h.setEditingDueDate}
            paymentDueDate={h.paymentDueDate} setPaymentDueDate={h.setPaymentDueDate}
            handleUpdateDueDate={h.handleUpdateDueDate}
            transactionDialogOpen={h.transactionDialogOpen}
            setTransactionDialogOpen={h.setTransactionDialogOpen}
            editingTransaction={h.editingTransaction}
            setEditingTransaction={h.setEditingTransaction}
            newTransaction={h.newTransaction} setNewTransaction={h.setNewTransaction}
            handleSaveTransaction={h.handleSaveTransaction}
            handleEditTransaction={h.handleEditTransaction}
            handleDeleteTransaction={h.handleDeleteTransaction}
            handleGenerateReceipt={h.handleGenerateReceipt}
          />
        </TabsContent>

        <TabsContent value="payments">
          <PaymentScheduleTab
            paymentSchedule={h.paymentSchedule}
            onGenerateSchedule={h.handleGeneratePaymentSchedule}
            onAddPayment={async (payment) => {
              try {
                const res = await axios.post(`${API}/payments/schedule`, {
                  customer_id: id,
                  items: [...h.paymentSchedule.items, {
                    id: Date.now().toString(), ...payment,
                    amount: parseFloat(payment.amount),
                    percentage: parseFloat(payment.percentage) || 0,
                    status: "pending",
                  }],
                });
                h.setPaymentSchedule(res.data);
                toast.success("Payment added");
              } catch { toast.error("Failed to add payment"); }
            }}
          />
        </TabsContent>

        <TabsContent value="documents">
          <DocumentsTab
            documents={h.documents} isAccountsRole={h.isAccountsRole}
            customer={h.customer}
            onGenerateDocument={async (docType) => {
              try {
                const res = await axios.post(`${API}/documents/generate`, { customer_id: id, doc_type: docType });
                h.setDocuments([...h.documents, res.data.document]);
                toast.success("Document generated");
              } catch (error) {
                toast.error(error.response?.data?.detail || "Failed to generate document");
              }
            }}
            onPreviewDocument={h.handlePreviewDocument}
            onDownloadDocument={h.handleDownloadDocument}
            onDeleteDocument={h.handleDeleteDocClick}
            onGenerateNoc={h.handleGenerateNoc}
            generatingNoc={h.generatingNoc}
          />
        </TabsContent>

        <TabsContent value="uploads">
          <UploadsTab
            uploadedDocs={h.uploadedDocs} isAccountsRole={h.isAccountsRole}
            onUpload={async (docType, file) => {
              const formData = new FormData();
              formData.append("file", file);
              formData.append("doc_type", docType);
              const res = await axios.post(`${API}/customers/${id}/upload-document`, formData, {
                headers: { "Content-Type": "multipart/form-data" },
              });
              h.setUploadedDocs([...h.uploadedDocs, res.data]);
              toast.success("Document uploaded");
            }}
            onPreview={h.handlePreviewUploadedDoc}
            onDownload={h.handleDownloadUploadedDoc}
            onDelete={h.handleDeleteDocClick}
          />
        </TabsContent>

        <TabsContent value="communication">
          <CommunicationTab
            customerId={id} customerPhone={h.customer?.phone}
            communications={h.communications}
            documents={h.documents} uploadedDocs={h.uploadedDocs}
            onCommunicationSent={() => {
              axios.get(`${API}/communication/${id}`).then((res) => h.setCommunications(res.data)).catch(() => {});
            }}
          />
        </TabsContent>

        <TabsContent value="checklist">
          <ChecklistTab checklist={h.checklist} onUpdateChecklist={h.handleUpdateChecklist} />
        </TabsContent>

        <TabsContent value="notes">
          <NotesTab
            notes={h.notes}
            onAddNote={async (content) => {
              try {
                const res = await axios.post(`${API}/customers/${id}/notes`, { content });
                h.setNotes([res.data, ...h.notes]);
                toast.success("Note added");
              } catch (error) { toast.error("Failed to add note"); throw error; }
            }}
            onDeleteNote={async (noteId) => {
              try {
                await axios.delete(`${API}/customers/${id}/notes/${noteId}`);
                h.setNotes(h.notes.filter((n) => n.id !== noteId));
                toast.success("Note deleted");
              } catch { toast.error("Failed to delete note"); }
            }}
            isAccountsRole={h.isAccountsRole}
          />
        </TabsContent>
      </Tabs>

      {/* Document Preview + Edit Dialog */}
      <EditableDocumentDialog
        open={h.previewDialogOpen}
        onOpenChange={h.setPreviewDialogOpen}
        doc={h.previewDoc}
        customerName={h.customer?.name}
        onSaved={() => {
          // reload documents list so updated_at reflects
          axios.get(`${API}/documents/${id}`).then(r => h.setDocuments(r.data)).catch(() => {});
        }}
      />

      {/* Document Delete Confirmation */}
      <AlertDialog open={h.docDeleteDialogOpen} onOpenChange={h.setDocDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Document?</AlertDialogTitle>
            <AlertDialogDescription>
              {h.docToDelete && (
                <>Are you sure you want to delete <strong>"{h.docToDelete.doc_type?.replace(/_/g, " ") || h.docToDelete.filename}"</strong>?<br /><br /><span className="text-red-600 font-medium">This action cannot be undone.</span></>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={h.docDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={h.handleConfirmDeleteDoc} disabled={h.docDeleting} className="bg-red-600 hover:bg-red-700" data-testid="confirm-delete-doc-btn">
              {h.docDeleting ? (<><Loader2 className="w-4 h-4 mr-2 animate-spin" />Deleting...</>) : (<><Trash2 className="w-4 h-4 mr-2" />Delete</>)}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <EmailComposerDialog
        open={h.emailComposerOpen} onOpenChange={h.setEmailComposerOpen}
        emailComposerData={h.emailComposerData}
        editedEmailSubject={h.editedEmailSubject} setEditedEmailSubject={h.setEditedEmailSubject}
        editedEmailBody={h.editedEmailBody} setEditedEmailBody={h.setEditedEmailBody}
        editedEmailTo={h.editedEmailTo} setEditedEmailTo={h.setEditedEmailTo}
        editedEmailCc={h.editedEmailCc} setEditedEmailCc={h.setEditedEmailCc}
        sendingEmail={h.sendingEmail} onSendEmail={h.handleSendDocumentEmail}
      />
    </div>
  );
};

export default CustomerDetailPage;
