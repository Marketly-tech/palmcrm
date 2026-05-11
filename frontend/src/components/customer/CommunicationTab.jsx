/**
 * CommunicationTab - Communication history + send message dialog with attachment support
 */
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import SendMessageDialog from "./communication/SendMessageDialog";
import CommunicationHistoryList from "./communication/CommunicationHistoryList";

const CommunicationTab = ({
  customerId,
  customerPhone,
  communications,
  documents,
  uploadedDocs,
  onCommunicationSent,
}) => {
  const [dialogOpen, setDialogOpen] = useState(false);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Communication History</CardTitle>
          <CardDescription>Emails and messages</CardDescription>
        </div>
        <SendMessageDialog
          open={dialogOpen}
          onOpenChange={setDialogOpen}
          customerId={customerId}
          customerPhone={customerPhone}
          documents={documents}
          uploadedDocs={uploadedDocs}
          onCommunicationSent={onCommunicationSent}
        />
      </CardHeader>
      <CardContent>
        <CommunicationHistoryList communications={communications} />
        <p className="text-xs text-slate-400 mt-4 italic">
          Replies from customers will appear in your email inbox. This log tracks all outbound communications.
        </p>
      </CardContent>
    </Card>
  );
};

export default CommunicationTab;
