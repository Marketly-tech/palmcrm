import axios from "axios";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Button } from "../ui/button";
import { Download } from "lucide-react";
import { openSafePreviewWindow } from "../../utils/safePreview";
import PaymentSummaryCard from "./payment/PaymentSummaryCard";
import DisbursementCalculatorCard from "./payment/DisbursementCalculatorCard";
import TransactionFormDialog from "./payment/TransactionFormDialog";
import TransactionsTable from "./payment/TransactionsTable";

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
  handleGenerateReceipt,
}) => {
  const handleExport = async () => {
    try {
      const custId = customer.id || customer.customer_id;
      const response = await axios.get(`${API}/transactions/${custId}/export-html`);
      openSafePreviewWindow(response.data.content);
    } catch (error) {
      toast.error("Failed to export transactions");
    }
  };

  const handleDialogOpenChange = (open) => {
    setTransactionDialogOpen(open);
    if (!open) {
      setEditingTransaction(null);
      setNewTransaction({
        transaction_stage: "",
        transaction_date: "",
        bank_name: "",
        transaction_number: "",
        amount: "",
        notes: "",
      });
    }
  };

  return (
    <>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PaymentSummaryCard
          customer={customer}
          transactions={transactions}
          overdueInfo={overdueInfo}
          formatCurrency={formatCurrency}
          editingDueDate={editingDueDate}
          setEditingDueDate={setEditingDueDate}
          paymentDueDate={paymentDueDate}
          setPaymentDueDate={setPaymentDueDate}
          handleUpdateDueDate={handleUpdateDueDate}
        />
        <DisbursementCalculatorCard
          customer={customer}
          disbursementPercentage={disbursementPercentage}
          setDisbursementPercentage={setDisbursementPercentage}
          formatCurrency={formatCurrency}
        />
      </div>

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
                onClick={handleExport}
              >
                <Download className="w-4 h-4 mr-2" />
                Export PDF
              </Button>
            )}
            <TransactionFormDialog
              open={transactionDialogOpen}
              onOpenChange={handleDialogOpenChange}
              editingTransaction={editingTransaction}
              newTransaction={newTransaction}
              setNewTransaction={setNewTransaction}
              handleSaveTransaction={handleSaveTransaction}
            />
          </div>
        </CardHeader>
        <CardContent>
          <TransactionsTable
            transactions={transactions}
            formatCurrency={formatCurrency}
            isAccountsRole={isAccountsRole}
            handleEditTransaction={handleEditTransaction}
            handleDeleteTransaction={handleDeleteTransaction}
            handleGenerateReceipt={handleGenerateReceipt}
          />
        </CardContent>
      </Card>
    </>
  );
};

export default PaymentTrackingTab;
