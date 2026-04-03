import DOMPurify from "dompurify";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Badge } from "../ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";
import { Mail, FileText, Loader2 } from "lucide-react";

const EmailComposerDialog = ({
  open,
  onOpenChange,
  emailComposerData,
  editedEmailSubject,
  setEditedEmailSubject,
  editedEmailBody,
  setEditedEmailBody,
  editedEmailTo,
  setEditedEmailTo,
  editedEmailCc,
  setEditedEmailCc,
  sendingEmail,
  onSendEmail,
}) => {
  if (!emailComposerData) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Mail className="w-5 h-5 text-primary" />
            {emailComposerData.email_type === 'welcome' && 'Send Welcome Email'}
            {emailComposerData.email_type === 'sales_agreement' && 'Send Sales Agreement'}
            {emailComposerData.email_type === 'allotment_letter' && 'Send Allotment Letter'}
          </DialogTitle>
        </DialogHeader>
        
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
                <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(emailComposerData.email_html || "") }} />
              </TabsContent>
              
              <TabsContent value="attachment1" className="max-h-[300px] overflow-auto border rounded-lg mt-2 bg-white">
                <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(emailComposerData.attachment_html || "") }} />
              </TabsContent>
              
              {emailComposerData.attachment_html_2 && (
                <TabsContent value="attachment2" className="max-h-[300px] overflow-auto border rounded-lg mt-2 bg-white">
                  <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(emailComposerData.attachment_html_2 || "") }} />
                </TabsContent>
              )}
              
              {emailComposerData.attachment_html_3 && (
                <TabsContent value="attachment3" className="max-h-[300px] overflow-auto border rounded-lg mt-2 bg-white">
                  <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(emailComposerData.attachment_html_3 || "") }} />
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
              <Button variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button 
                onClick={onSendEmail} 
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
      </DialogContent>
    </Dialog>
  );
};

export default EmailComposerDialog;
