import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Label } from "../ui/label";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Textarea } from "../ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import { Plus, Edit, Trash2, Save, CreditCard, CheckCircle, Download } from "lucide-react";
import axios from "axios";
import DOMPurify from "dompurify";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PaymentTrackingTab = ({
  customer,
  transactions,
  overdueInfo,
  formatCurrency,
  isAccountsRole,
  // Disbursement calculator
  disbursementPercentage,
  setDisbursementPercentage,
  // Due date
  editingDueDate,
  setEditingDueDate,
  paymentDueDate,
  setPaymentDueDate,
  handleUpdateDueDate,
  // Transaction CRUD
  transactionDialogOpen,
  setTransactionDialogOpen,
  editingTransaction,
  setEditingTransaction,
  newTransaction,
  setNewTransaction,
  handleSaveTransaction,
  handleEditTransaction,
  handleDeleteTransaction,
}) => {
  const totalReceived = transactions.reduce((sum, txn) => sum + (txn.amount || 0), 0);
  const totalPrice = customer.total_price || 0;
  const balanceAmount = totalPrice - totalReceived;
  const receivedPercentage = totalPrice > 0 ? (totalReceived / totalPrice) * 100 : 0;
  const pendingPercentage = totalPrice > 0 ? (balanceAmount / totalPrice) * 100 : 100;

  return (
    <>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Payment Tracking */}
        <Card>
          <CardHeader>
            <CardTitle>Payment Tracking</CardTitle>
            <CardDescription>Track received vs pending payments</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-slate-600">Received</p>
                <p className="text-2xl font-bold text-green-600">{formatCurrency(totalReceived)}</p>
                <p className="text-lg font-semibold text-green-600">{receivedPercentage.toFixed(1)}%</p>
                <p className="text-xs text-slate-500 mt-1">
                  (From {transactions.length} transaction{transactions.length !== 1 ? 's' : ''})
                </p>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <p className="text-sm text-slate-600">Pending</p>
                <p className="text-2xl font-bold text-red-600">{formatCurrency(balanceAmount)}</p>
                <p className="text-lg font-semibold text-red-600">{pendingPercentage.toFixed(1)}%</p>
              </div>
            </div>
            
            {/* Stage-based Overdue Amount */}
            {overdueInfo?.is_overdue && (
              <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="destructive">PAYMENT OVERDUE</Badge>
                  <span className="text-sm text-slate-600">as per disbursement slab: {overdueInfo.current_stage_name}</span>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-slate-600">Expected ({overdueInfo.cumulative_percentage}%)</p>
                    <p className="font-bold text-slate-900">{formatCurrency(overdueInfo.expected_amount)}</p>
                  </div>
                  <div>
                    <p className="text-slate-600">Total Received</p>
                    <p className="font-bold text-green-600">{formatCurrency(overdueInfo.total_received)}</p>
                  </div>
                  <div>
                    <p className="text-slate-600">Overdue Amount</p>
                    <p className="font-bold text-2xl text-red-600">{formatCurrency(overdueInfo.overdue_amount)}</p>
                  </div>
                </div>
              </div>
            )}
            
            {overdueInfo && !overdueInfo.is_overdue && overdueInfo.current_stage && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="text-sm text-green-700">
                  Payments up to date for current disbursement slab: {overdueInfo.current_stage_name}
                </span>
              </div>
            )}
            
            {overdueInfo && !overdueInfo.current_stage && (
              <div className="p-3 bg-slate-50 border rounded-lg text-sm text-slate-500">
                No disbursement slab set by admin. Overdue tracking unavailable.
              </div>
            )}
            
            {/* Progress Bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Payment Progress</span>
                <span>{receivedPercentage.toFixed(1)}%</span>
              </div>
              <div className="h-4 bg-slate-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-green-500 transition-all duration-500"
                  style={{ width: `${Math.min(receivedPercentage, 100)}%` }}
                />
              </div>
            </div>
            
            {/* Payment Due Date Section */}
            <div className="pt-4 border-t">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-700">Next Payment Due Date</p>
                  {editingDueDate ? (
                    <div className="flex items-center gap-2 mt-1">
                      <Input
                        type="date"
                        value={paymentDueDate}
                        onChange={(e) => setPaymentDueDate(e.target.value)}
                        className="w-40"
                        data-testid="payment-due-date-input"
                      />
                      <Button size="sm" onClick={handleUpdateDueDate}>
                        <Save className="h-3 w-3 mr-1" />
                        Save
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => setEditingDueDate(false)}>
                        Cancel
                      </Button>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <p className="text-lg font-semibold text-primary">
                        {customer.payment_due_date 
                          ? new Date(customer.payment_due_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
                          : "Not set"}
                      </p>
                      <Button size="sm" variant="ghost" onClick={() => setEditingDueDate(true)} data-testid="edit-due-date-btn">
                        <Edit className="h-3 w-3" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Disbursement Calculator */}
        <Card>
          <CardHeader>
            <CardTitle>Disbursement Calculator</CardTitle>
            <CardDescription>Calculate disbursement amounts</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="flex-1">
                <Label htmlFor="disbursement-pct" className="text-sm">Enter Percentage (%)</Label>
                <div className="flex items-center gap-2 mt-1">
                  <Input
                    id="disbursement-pct"
                    type="number"
                    min="0"
                    max="100"
                    step="0.5"
                    value={disbursementPercentage}
                    onChange={(e) => setDisbursementPercentage(parseFloat(e.target.value) || 0)}
                    className="w-24"
                    data-testid="disbursement-percentage-input"
                  />
                  <span className="text-slate-500">%</span>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-slate-600">Disbursement Amount</p>
                <p className="text-xl font-bold text-primary" data-testid="disbursement-amount">
                  {formatCurrency(customer.total_price * (disbursementPercentage / 100))}
                </p>
              </div>
            </div>
            <div className="grid grid-cols-4 gap-2 mt-3">
              {[30, 50, 70, 100].map((pct) => (
                <Button 
                  key={pct}
                  variant="outline" 
                  size="sm"
                  className={disbursementPercentage === pct ? "border-primary bg-primary/10" : ""}
                  onClick={() => setDisbursementPercentage(pct)}
                >
                  {pct}%
                </Button>
              ))}
            </div>
            <div className="p-3 bg-blue-50 rounded-lg text-sm">
              <div className="flex justify-between">
                <span>Total Property Value:</span>
                <span className="font-medium">{formatCurrency(customer.total_price)}</span>
              </div>
              <div className="flex justify-between mt-1">
                <span>{disbursementPercentage}% Disbursement:</span>
                <span className="font-bold text-blue-700">{formatCurrency(customer.total_price * (disbursementPercentage / 100))}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Transaction Records */}
      <Card className="mt-6">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Transaction Records</CardTitle>
            <CardDescription>Track all payment transactions by stage</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            {transactions.length > 0 && (
              <Button
                variant="outline"
                data-testid="export-transactions-pdf-btn"
                onClick={async () => {
                  try {
                    const custId = customer.customer_id || customer.id;
                    const response = await axios.get(`${API}/transactions/${custId}/export-html`);
                    const printWindow = window.open("", "_blank");
                    if (printWindow) {
                      const sanitized = DOMPurify.sanitize(response.data.content, { WHOLE_DOCUMENT: true, ADD_TAGS: ['style', 'link'], ADD_ATTR: ['target'] });
                      printWindow.document.open();
                      printWindow.document.write(sanitized);
                      printWindow.document.close();
                    }
                  } catch (error) {
                    toast.error("Failed to export transactions");
                  }
                }}
              >
                <Download className="w-4 h-4 mr-2" />
                Export PDF
              </Button>
            )}
            <Dialog open={transactionDialogOpen} onOpenChange={(open) => {
            setTransactionDialogOpen(open);
            if (!open) {
              setEditingTransaction(null);
              setNewTransaction({
                transaction_stage: "",
                transaction_date: "",
                bank_name: "",
                transaction_number: "",
                amount: "",
                notes: ""
              });
            }
          }}>
            <DialogTrigger asChild>
              <Button data-testid="add-transaction-btn">
                <Plus className="w-4 h-4 mr-2" />
                Add Transaction
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{editingTransaction ? "Edit Transaction" : "Add New Transaction"}</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label>Transaction Stage *</Label>
                  <Select
                    value={newTransaction.transaction_stage}
                    onValueChange={(value) => setNewTransaction({ ...newTransaction, transaction_stage: value })}
                  >
                    <SelectTrigger data-testid="transaction-stage-select">
                      <SelectValue placeholder="Select stage" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="booking">Booking</SelectItem>
                      <SelectItem value="agreement">Agreement</SelectItem>
                      <SelectItem value="scheduled_disbursement">Scheduled Disbursement</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Transaction Date *</Label>
                  <Input
                    type="date"
                    value={newTransaction.transaction_date}
                    onChange={(e) => setNewTransaction({ ...newTransaction, transaction_date: e.target.value })}
                    data-testid="transaction-date-input"
                  />
                </div>
                <div>
                  <Label>Bank Name *</Label>
                  <Input
                    value={newTransaction.bank_name}
                    onChange={(e) => setNewTransaction({ ...newTransaction, bank_name: e.target.value })}
                    placeholder="e.g., HDFC Bank"
                    data-testid="transaction-bank-input"
                  />
                </div>
                <div>
                  <Label>Transaction Number *</Label>
                  <Input
                    value={newTransaction.transaction_number}
                    onChange={(e) => setNewTransaction({ ...newTransaction, transaction_number: e.target.value })}
                    placeholder="e.g., TXN123456789"
                    data-testid="transaction-number-input"
                  />
                </div>
                <div>
                  <Label>Amount (₹)</Label>
                  <Input
                    type="number"
                    value={newTransaction.amount}
                    onChange={(e) => setNewTransaction({ ...newTransaction, amount: e.target.value })}
                    placeholder="Enter amount"
                    data-testid="transaction-amount-input"
                  />
                </div>
                <div>
                  <Label>Notes</Label>
                  <Textarea
                    value={newTransaction.notes}
                    onChange={(e) => setNewTransaction({ ...newTransaction, notes: e.target.value })}
                    placeholder="Optional notes"
                    rows={2}
                    data-testid="transaction-notes-input"
                  />
                </div>
                <Button 
                  onClick={handleSaveTransaction} 
                  className="w-full"
                  disabled={!newTransaction.transaction_stage || !newTransaction.transaction_date || !newTransaction.bank_name || !newTransaction.transaction_number}
                  data-testid="save-transaction-btn"
                >
                  {editingTransaction ? "Update Transaction" : "Add Transaction"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          {transactions.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Stage</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Bank Name</TableHead>
                  <TableHead>Transaction No.</TableHead>
                  <TableHead className="text-right">Amount</TableHead>
                  <TableHead>Notes</TableHead>
                  <TableHead className="text-center">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {transactions.map((txn) => (
                  <TableRow key={txn.id}>
                    <TableCell>
                      <Badge className={
                        txn.transaction_stage === 'booking' ? 'bg-blue-100 text-blue-700' :
                        txn.transaction_stage === 'agreement' ? 'bg-green-100 text-green-700' :
                        'bg-purple-100 text-purple-700'
                      }>
                        {txn.transaction_stage === 'scheduled_disbursement' ? 'Scheduled Disbursement' : 
                         (txn.transaction_stage ? txn.transaction_stage.charAt(0).toUpperCase() + txn.transaction_stage.slice(1) : 'Payment')}
                      </Badge>
                    </TableCell>
                    <TableCell>{txn.transaction_date}</TableCell>
                    <TableCell>{txn.bank_name}</TableCell>
                    <TableCell className="font-mono text-sm">{txn.transaction_number}</TableCell>
                    <TableCell className="text-right font-medium">{txn.amount ? formatCurrency(txn.amount) : '-'}</TableCell>
                    <TableCell className="max-w-xs truncate" title={txn.notes}>{txn.notes || '-'}</TableCell>
                    <TableCell className="text-center">
                      <div className="flex justify-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEditTransaction(txn)}
                          data-testid={`edit-transaction-${txn.id}`}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        {!isAccountsRole && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-500 hover:text-red-700"
                            onClick={() => handleDeleteTransaction(txn.id)}
                            data-testid={`delete-transaction-${txn.id}`}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8 text-slate-500">
              <CreditCard className="w-12 h-12 mx-auto mb-4 text-slate-300" />
              <p>No transactions recorded yet</p>
              <p className="text-sm mt-1">Click "Add Transaction" to record a payment</p>
            </div>
          )}
        </CardContent>
      </Card>
    </>
  );
};

export default PaymentTrackingTab;
