import { Label } from "../../ui/label";
import { Input } from "../../ui/input";
import { Button } from "../../ui/button";
import { Textarea } from "../../ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../../ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../../ui/dialog";
import { Plus } from "lucide-react";

const TransactionFormDialog = ({
  open,
  onOpenChange,
  editingTransaction,
  newTransaction,
  setNewTransaction,
  handleSaveTransaction,
}) => {
  const formValid =
    newTransaction.transaction_stage &&
    newTransaction.transaction_date &&
    newTransaction.bank_name &&
    newTransaction.transaction_number;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
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
                <SelectItem value="tds">TDS</SelectItem>
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
            disabled={!formValid}
            data-testid="save-transaction-btn"
          >
            {editingTransaction ? "Update Transaction" : "Add Transaction"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default TransactionFormDialog;
