import { Card, CardContent } from "../ui/card";
import { Badge } from "../ui/badge";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "../ui/select";

const AGREEMENT_BADGE_CLASSES = {
  signed: "bg-green-100 text-green-700 border-green-300",
  registered: "bg-blue-100 text-blue-700 border-blue-300",
  sent: "bg-yellow-100 text-yellow-700 border-yellow-300",
  disbursement: "bg-purple-100 text-purple-700 border-purple-300",
};
const DEFAULT_AGREEMENT_BADGE = "bg-slate-100 text-slate-700 border-slate-300";

const CustomerQuickInfo = ({ customer, transactions, formatCurrency, getStatusBadge, onAgreementStatusChange }) => {
  const totalReceived = transactions.reduce((sum, txn) => sum + (txn.amount || 0), 0);
  const totalPrice = customer.total_price || 0;
  const receivedPercentage = totalPrice > 0 ? (totalReceived / totalPrice) * 100 : 0;
  const agreementBadgeClass = AGREEMENT_BADGE_CLASSES[customer.agreement_status] || DEFAULT_AGREEMENT_BADGE;

  return (
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
          <Select value={customer.agreement_status || "draft"} onValueChange={onAgreementStatusChange}>
            <SelectTrigger className={`w-full h-8 ${agreementBadgeClass}`}>
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
          <p className="font-semibold text-green-600">{receivedPercentage.toFixed(1)}%</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default CustomerQuickInfo;
