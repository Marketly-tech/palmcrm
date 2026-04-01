/**
 * CommunicationTab - Communication history and messaging component
 * Displays communication history and allows sending emails/WhatsApp messages
 */
import { useState, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import { Badge } from "../ui/badge";
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
  MessageSquare, 
  Paperclip, 
  FileText, 
  CheckCircle, 
  Upload,
  X 
} from "lucide-react";

const CommunicationTab = ({
  communications,
  documents,
  uploadedDocs,
  customerPhone,
  onSendCommunication,
}) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [commType, setCommType] = useState("email");
  const [commSubject, setCommSubject] = useState("");
  const [commMessage, setCommMessage] = useState("");
  const [selectedAttachments, setSelectedAttachments] = useState([]);
  const [localAttachment, setLocalAttachment] = useState(null);
  const localFileRef = useRef(null);

  const toggleAttachment = (docId) => {
    setSelectedAttachments(prev =>
      prev.includes(docId)
        ? prev.filter(id => id !== docId)
        : [...prev, docId]
    );
  };

  const handleLocalFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setLocalAttachment(file);
    }
  };

  const handleSend = async () => {
    if (commType === "whatsapp") {
      const message = encodeURIComponent(commMessage);
      const phone = customerPhone?.replace(/\D/g, "");
      window.open(`https://wa.me/${phone}?text=${message}`, "_blank");
      setDialogOpen(false);
      setCommMessage("");
      return;
    }

    await onSendCommunication({
      type: commType,
      subject: commSubject,
      message: commMessage,
      attachments: selectedAttachments,
      localAttachment,
    });
    
    setDialogOpen(false);
    setCommSubject("");
    setCommMessage("");
    setSelectedAttachments([]);
    setLocalAttachment(null);
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
