/**
 * CommunicationTab - Communication history + send message dialog with attachment support
 */
import { useState, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Badge } from "../ui/badge";
import { Textarea } from "../ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import {
  Send,
  Mail,
  Phone,
  FileText,
  Upload,
  Paperclip,
  X,
  CheckCircle,
  MessageSquare,
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

const CommunicationTab = ({
  customerId,
  customerPhone,
  communications,
  documents,
  uploadedDocs,
  onCommunicationSent,
}) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [commType, setCommType] = useState("email");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [selectedAttachments, setSelectedAttachments] = useState([]);
  const [localAttachment, setLocalAttachment] = useState(null);
  const localFileRef = useRef(null);

  const toggleAttachment = (docId) => {
    setSelectedAttachments(prev =>
      prev.includes(docId) ? prev.filter(id => id !== docId) : [...prev, docId]
    );
  };

  const handleLocalFileSelect = (e) => {
    if (e.target.files[0]) {
      setLocalAttachment(e.target.files[0]);
    }
  };

  const handleSend = async () => {
    if (!message.trim()) {
      toast.error("Message is required");
      return;
    }
    try {
      if (commType === "email") {
        const formData = new FormData();
        formData.append("customer_id", customerId);
        formData.append("subject", subject);
        formData.append("message", message);
        if (selectedAttachments.length > 0) {
          formData.append("attachment_ids", JSON.stringify(selectedAttachments));
        }
        if (localAttachment) {
          formData.append("local_file", localAttachment);
        }
        await axios.post(`${API}/communication/email`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      } else {
        const phone = customerPhone || "";
        const encodedMsg = encodeURIComponent(message);
        window.open(`https://wa.me/${phone.replace(/\D/g, "")}?text=${encodedMsg}`, "_blank");
        await axios.post(`${API}/communication/whatsapp`, {
          customer_id: customerId,
          message,
        });
      }
      toast.success(`${commType === "email" ? "Email" : "WhatsApp message"} sent`);
      // Reset
      setSubject("");
      setMessage("");
      setSelectedAttachments([]);
      setLocalAttachment(null);
      setDialogOpen(false);
      if (onCommunicationSent) onCommunicationSent();
    } catch (error) {
      toast.error(`Failed to send ${commType}`);
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Communication History</CardTitle>
          <CardDescription>Emails and messages</CardDescription>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
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
              <Button onClick={handleSend} className="w-full">
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
  );
};

export default CommunicationTab;
