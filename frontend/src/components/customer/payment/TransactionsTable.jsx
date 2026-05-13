import { Button } from "../../ui/button";
import { Badge } from "../../ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../../ui/table";
import { Edit, Trash2, CreditCard, Receipt } from "lucide-react";

const stageClass = (stage) => {
  switch (stage) {
    case 'booking': return 'bg-blue-100 text-blue-700';
    case 'agreement': return 'bg-green-100 text-green-700';
    case 'tds': return 'bg-amber-100 text-amber-700';
    default: return 'bg-purple-100 text-purple-700';
  }
};

const stageLabel = (stage) => {
  if (stage === 'scheduled_disbursement') return 'Scheduled Disbursement';
  if (stage === 'tds') return 'TDS';
  return stage ? stage.charAt(0).toUpperCase() + stage.slice(1) : 'Payment';
};

const TransactionsTable = ({
  transactions,
  formatCurrency,
  isAccountsRole,
  handleEditTransaction,
  handleDeleteTransaction,
  handleGenerateReceipt,
}) => {
  if (transactions.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        <CreditCard className="w-12 h-12 mx-auto mb-4 text-slate-300" />
        <p>No transactions recorded yet</p>
        <p className="text-sm mt-1">Click "Add Transaction" to record a payment</p>
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Receipt No.</TableHead>
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
            <TableCell className="font-mono text-xs text-slate-600">
              {txn.receipt_number || <span className="text-slate-300">—</span>}
            </TableCell>
            <TableCell>
              <Badge className={stageClass(txn.transaction_stage)}>
                {stageLabel(txn.transaction_stage)}
              </Badge>
            </TableCell>
            <TableCell>{txn.transaction_date}</TableCell>
            <TableCell>{txn.bank_name}</TableCell>
            <TableCell className="font-mono text-sm">{txn.transaction_number}</TableCell>
            <TableCell className="text-right font-medium">{txn.amount ? formatCurrency(txn.amount) : '-'}</TableCell>
            <TableCell className="max-w-xs truncate" title={txn.notes}>{txn.notes || '-'}</TableCell>
            <TableCell className="text-center">
              <div className="flex justify-center gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleGenerateReceipt(txn)}
                  data-testid={`receipt-transaction-${txn.id}`}
                  title="Generate Payment Receipt"
                  className="text-emerald-600 hover:text-emerald-700"
                >
                  <Receipt className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleEditTransaction(txn)}
                  data-testid={`edit-transaction-${txn.id}`}
                  title="Edit Transaction"
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
                    title="Delete Transaction"
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
  );
};

export default TransactionsTable;
