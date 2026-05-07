import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Card, CardContent } from "../ui/card";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "../ui/table";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "../ui/select";
import { Eye, Users, Loader2, Trash2 } from "lucide-react";

const INR = (amount) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount || 0);

const getStatusBadge = (status) => {
  const styles = { draft: "bg-slate-100 text-slate-700", sent: "bg-yellow-100 text-yellow-700", signed: "bg-green-100 text-green-700", registered: "bg-blue-100 text-blue-700", disbursement: "bg-purple-100 text-purple-700", completed: "bg-purple-100 text-purple-700" };
  return styles[status] || styles.draft;
};

const CustomerTable = ({
  customers, loading, isAccountsRole, agreementFilter, bankFilter,
  onNavigate, onDeleteClick, onAgreementStatusChange,
}) => {
  const showOverdue = !!bankFilter || agreementFilter === "overdue";
  const totalOverdue = showOverdue
    ? customers.reduce((sum, c) => sum + (c._overdue_amount || 0), 0)
    : 0;

  return (
    <Card>
      <CardContent className="p-0">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : customers.length > 0 ? (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Booking ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Project</TableHead>
                <TableHead>Flat No.</TableHead>
                <TableHead>Unit</TableHead>
                <TableHead>Phone</TableHead>
                {showOverdue && <TableHead className="text-right text-red-600" data-testid="overdue-column-header">Overdue Amount</TableHead>}
                <TableHead>Agreement</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {customers.map((customer) => (
                <TableRow key={customer.id} className="cursor-pointer hover:bg-slate-50" onClick={() => onNavigate(`/customers/${customer.id}`)} data-testid={`customer-row-${customer.id}`}>
                  <TableCell className="font-mono text-sm">{customer.booking_number || customer.customer_id}</TableCell>
                  <TableCell>
                    <div>
                      <p className="font-medium">{customer.name}</p>
                      <p className="text-sm text-slate-500">{customer.email}</p>
                    </div>
                  </TableCell>
                  <TableCell>{customer.project}</TableCell>
                  <TableCell><span className="font-mono font-medium text-blue-600">{customer.unit_number}</span></TableCell>
                  <TableCell><span className="font-mono">{customer.tower}-{customer.unit_number}</span></TableCell>
                  <TableCell>{customer.phone}</TableCell>
                  {showOverdue && (
                    <TableCell className="text-right font-mono font-semibold text-red-600" data-testid={`overdue-amount-${customer.id}`}>
                      {INR(customer._overdue_amount || 0)}
                    </TableCell>
                  )}
                  <TableCell onClick={(e) => e.stopPropagation()}>
                    <Select value={customer.agreement_status || "draft"} onValueChange={(value) => onAgreementStatusChange(customer.id, value)}>
                      <SelectTrigger className={`w-28 h-8 text-xs ${getStatusBadge(customer.agreement_status)}`}><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="draft">Draft</SelectItem>
                        <SelectItem value="sent">Sent</SelectItem>
                        <SelectItem value="signed">Signed</SelectItem>
                        <SelectItem value="registered">Registered</SelectItem>
                        <SelectItem value="disbursement">Disbursement</SelectItem>
                      </SelectContent>
                    </Select>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-1">
                      <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); onNavigate(`/customers/${customer.id}`); }} data-testid={`view-customer-${customer.id}`}>
                        <Eye className="w-4 h-4" />
                      </Button>
                      {!isAccountsRole && (
                        <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700 hover:bg-red-50" onClick={(e) => onDeleteClick(customer, e)} data-testid={`delete-customer-${customer.id}`}>
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              {showOverdue && bankFilter && (
                <TableRow className="bg-slate-900 hover:bg-slate-900" data-testid="overdue-total-row">
                  <TableCell colSpan={6} className="text-right font-semibold text-white text-sm">
                    Total Overdue ({bankFilter})
                  </TableCell>
                  <TableCell className="text-right font-mono font-bold text-amber-400 text-base" data-testid="overdue-total-amount">
                    {INR(totalOverdue)}
                  </TableCell>
                  <TableCell colSpan={2} />
                </TableRow>
              )}
            </TableBody>
          </Table>
        ) : (
          <div className="flex flex-col items-center justify-center h-64 text-slate-500">
            <Users className="w-12 h-12 mb-4 text-slate-300" />
            <p className="text-lg font-medium">No customers found</p>
            <p className="text-sm">Try adjusting your search or filters</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default CustomerTable;
