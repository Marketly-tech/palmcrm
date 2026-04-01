/**
 * TransactionsCard - Transaction records management component
 * Displays and manages payment transactions by stage
 */
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Badge } from "../ui/badge";
import { Textarea } from "../ui/textarea";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Plus, Edit, Trash2, CreditCard } from "lucide-react";
import { formatCurrency } from "./utils";

const TRANSACTION_STAGES = [
  { value: "booking", label: "Booking" },
  { value: "agreement", label: "Agreement" },
  { value: "scheduled_disbursement", label: "Scheduled Disbursement" },
];

const TransactionsCard = ({
  transactions,
  onAddTransaction,
  onEditTransaction,
  onDeleteTransaction,
  isAccountsRole = false,
}) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingTxn, setEditingTxn] = useState(null);
  const [formData, setFormData] = useState({
    transaction_stage: "",
    transaction_date: "",
    bank_name: "",
    transaction_number: "",
    amount: "",
    notes: "",
  });

  const resetForm = () => {
    setFormData({
      transaction_stage: "",
      transaction_date: "",
      bank_name: "",
      transaction_number: "",
      amount: "",
      notes: "",
    });
    setEditingTxn(null);
  };

  const handleOpenEdit = (txn) => {
    setEditingTxn(txn);
    setFormData({
      transaction_stage: txn.transaction_stage || "",
      transaction_date: txn.transaction_date || "",
      bank_name: txn.bank_name || "",
      transaction_number: txn.transaction_number || "",
      amount: txn.amount?.toString() || "",
      notes: txn.notes || "",
    });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    if (editingTxn) {
      await onEditTransaction(editingTxn.id, formData);
    } else {
      await onAddTransaction(formData);
    }
    setDialogOpen(false);
    resetForm();
  };

  const getStageBadgeClass = (stage) => {
    switch (stage) {
      case 'booking': return 'bg-blue-100 text-blue-700';
      case 'agreement': return 'bg-green-100 text-green-700';
      default: return 'bg-purple-100 text-purple-700';
    }
  };

  const getStageLabel = (stage) => {
    if (stage === 'scheduled_disbursement') return 'Scheduled Disbursement';
    return stage ? stage.charAt(0).toUpperCase() + stage.slice(1) : 'Payment';
  };

  return (
    <Card className="mt-6">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Transaction Records</CardTitle>
          <CardDescription>Track all payment transactions by stage</CardDescription>
        </div>
        <Dialog open={dialogOpen} onOpenChange={(open) => {
          setDialogOpen(open);
          if (!open) resetForm();
        }}>
          <DialogTrigger asChild>
            <Button data-testid="add-transaction-btn">
              <Plus className="w-4 h-4 mr-2" />
              Add Transaction
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editingTxn ? "Edit Transaction" : "Add New Transaction"}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Transaction Stage *</Label>
                <Select
                  value={formData.transaction_stage}
                  onValueChange={(value) => setFormData({ ...formData, transaction_stage: value })}
                >
                  <SelectTrigger data-testid="transaction-stage-select">
                    <SelectValue placeholder="Select stage" />
                  </SelectTrigger>
                  <SelectContent>
                    {TRANSACTION_STAGES.map((stage) => (
                      <SelectItem key={stage.value} value={stage.value}>
                        {stage.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Transaction Date *</Label>
                <Input
                  type="date"
                  value={formData.transaction_date}
                  onChange={(e) => setFormData({ ...formData, transaction_date: e.target.value })}
                  data-testid="transaction-date-input"
                />
              </div>
              <div>
                <Label>Bank Name *</Label>
                <Input
                  value={formData.bank_name}
                  onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
                  placeholder="e.g., HDFC Bank"
                  data-testid="transaction-bank-input"
                />
              </div>
              <div>
                <Label>Transaction Number *</Label>
                <Input
                  value={formData.transaction_number}
                  onChange={(e) => setFormData({ ...formData, transaction_number: e.target.value })}
                  placeholder="e.g., TXN123456789"
                  data-testid="transaction-number-input"
                />
              </div>
              <div>
                <Label>Amount (₹)</Label>
                <Input
                  type="number"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  placeholder="Enter amount"
                  data-testid="transaction-amount-input"
                />
              </div>
              <div>
                <Label>Notes</Label>
                <Textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Optional notes"
                  rows={2}
                  data-testid="transaction-notes-input"
                />
              </div>
              <Button 
                onClick={handleSave} 
                className="w-full"
                disabled={!formData.transaction_stage || !formData.transaction_date || !formData.bank_name || !formData.transaction_number}
                data-testid="save-transaction-btn"
              >
                {editingTxn ? "Update Transaction" : "Add Transaction"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
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
                    <Badge className={getStageBadgeClass(txn.transaction_stage)}>
                      {getStageLabel(txn.transaction_stage)}
                    </Badge>
                  </TableCell>
                  <TableCell>{txn.transaction_date}</TableCell>
                  <TableCell>{txn.bank_name}</TableCell>
                  <TableCell className="font-mono text-sm">{txn.transaction_number}</TableCell>
                  <TableCell className="text-right font-medium">
                    {txn.amount ? formatCurrency(txn.amount) : '-'}
                  </TableCell>
                  <TableCell className="max-w-xs truncate" title={txn.notes}>
                    {txn.notes || '-'}
                  </TableCell>
                  <TableCell className="text-center">
                    <div className="flex justify-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleOpenEdit(txn)}
                        data-testid={`edit-transaction-${txn.id}`}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      {!isAccountsRole && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-red-500 hover:text-red-700"
                          onClick={() => onDeleteTransaction(txn.id)}
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
  );
};

export default TransactionsCard;
