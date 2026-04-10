import { Button } from "../ui/button";
import {
  ArrowLeft, Mail, FileText, MessageCircle,
  Edit, Save, Loader2,
} from "lucide-react";

const CustomerHeader = ({
  customer, navigate, editing, setEditing, saving, isAccountsRole,
  sendingWelcome, sendingEmail,
  onSave, onPreviewWelcome, onPreviewSalesAgreement,
  onPreviewAllotmentLetter, onSendWhatsApp,
}) => (
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
      <Button variant="outline" onClick={onPreviewWelcome} disabled={sendingWelcome} data-testid="send-welcome-btn">
        {sendingWelcome ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Mail className="w-4 h-4 mr-2" />}
        Welcome Email
      </Button>
      <Button
        variant="outline" onClick={onPreviewSalesAgreement} disabled={sendingEmail}
        data-testid="send-sales-agreement-btn"
        className="text-amber-600 hover:text-amber-700 hover:bg-amber-50 border-amber-200"
      >
        {sendingEmail ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <FileText className="w-4 h-4 mr-2" />}
        Sales Agreement
      </Button>
      <Button
        variant="outline" onClick={onPreviewAllotmentLetter} disabled={sendingEmail}
        data-testid="send-allotment-btn"
        className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 border-blue-200"
      >
        {sendingEmail ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <FileText className="w-4 h-4 mr-2" />}
        Allotment Letter
      </Button>
      <Button
        variant="outline" onClick={onSendWhatsApp}
        className="text-green-600 hover:text-green-700 hover:bg-green-50 border-green-200"
        data-testid="send-whatsapp-btn"
      >
        <MessageCircle className="w-4 h-4 mr-2" />
        WhatsApp
      </Button>
      {editing ? (
        <>
          <Button variant="outline" onClick={() => setEditing(false)}>Cancel</Button>
          <Button onClick={onSave} disabled={saving} data-testid="save-customer-btn">
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
);

export default CustomerHeader;
