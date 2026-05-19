import { useState, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "../../ui/button";
import { Input } from "../../ui/input";
import { Label } from "../../ui/label";
import { Textarea } from "../../ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../../ui/dialog";
import {
  Send,
  Mail,
  Phone,
  FileText,
  Upload,
  Paperclip,
  X,
  CheckCircle,
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

const SendMessageDialog = ({
  open,
  onOpenChange,
  customerId,
  customerPhone,
  documents,
  uploadedDocs,
  onCommunicationSent,
}) => {
  const [commType, setCommType] = useState("email");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [selectedAttachments, setSelectedAttachments] = useState([]);
  const [localAttachment, setLocalAttachment] = useState(null);
  const localFileRef = useRef(null);

  const toggleAttachment = (docId) => {
    setSelectedAttachments((prev) =>
      prev.includes(docId) ? prev.filter((id) => id !== docId) : [...prev, docId]
    );
  };

  const handleLocalFileSelect = (e) => {
    if (e.target.files[0]) setLocalAttachment(e.target.files[0]);
  };

  const reset = () => {
    setSubject("");
    setMessage("");
    setSelectedAttachments([]);
    setLocalAttachment(null);
  };

  const sendEmail = async () => {
    const formData = new FormData();
    formData.append("customer_id", customerId);
    formData.append("subject", subject);
    formData.append("message", message);
    if (selectedAttachments.length > 0) {
      formData.append("attachment_ids", JSON.stringify(selectedAttachments));
    }
    if (localAttachment) formData.append("local_file", localAttachment);
    await axios.post(`${API}/communication/email`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  };

  const sendWhatsApp = async () => {
    const phone = customerPhone || "";
    const encodedMsg = encodeURIComponent(message);
    window.open(
      `https://wa.me/${phone.replace(/\D/g, "")}?text=${encodedMsg}`,
      "_blank"
    );
    await axios.post(`${API}/communication/whatsapp`, {
      customer_id: customerId,
      message,
    });
  };

  const handleSend = async () => {
    if (!message.trim()) {
      toast.error("Message is required");
      return;
    }
    try {
      if (commType === "email") {
        await sendEmail();
      } else {
        await sendWhatsApp();
      }
      toast.success(`${commType === "email" ? "Email" : "WhatsApp message"} sent`);
      reset();
      onOpenChange(false);
      if (onCommunicationSent) onCommunicationSent();
    } catch (error) {
      const detail = error.response?.data?.detail;
      const msg = typeof detail === "string" ? detail : `Failed to send ${commType}`;
      toast.error(msg);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
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
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Email subject"
              />
            </div>
          )}
          <div>
            <Label>Message</Label>
            <Textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              rows={4}
            />
          </div>

          {commType === "email" && (
            <div className="space-y-3">
              <Label className="flex items-center gap-2">
                <Paperclip className="w-4 h-4" />
                Attachments
              </Label>

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
          <Button onClick={handleSend} className="w-full">
            Send
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default SendMessageDialog;
