/**
 * PaymentTrackingCard - Payment tracking with overdue calculation
 * Shows received vs pending amounts and stage-based overdue tracking
 */
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Badge } from "../ui/badge";
import { CheckCircle, Edit, Save } from "lucide-react";
import { formatCurrency } from "./utils";

const PaymentTrackingCard = ({
  transactions,
  totalPrice,
  overdueInfo,
  paymentDueDate,
  onUpdateDueDate,
}) => {
  const [editingDueDate, setEditingDueDate] = useState(false);
  const [dueDateValue, setDueDateValue] = useState(paymentDueDate || "");

  // Calculate totals - total received comes from transactions only
  // booking_amount is already recorded as transaction entries, no double-counting
  const totalReceived = transactions.reduce((sum, txn) => sum + (txn.amount || 0), 0);
  const balanceAmount = (totalPrice || 0) - totalReceived;
  const receivedPercentage = totalPrice > 0 ? (totalReceived / totalPrice) * 100 : 0;
  const pendingPercentage = totalPrice > 0 ? (balanceAmount / totalPrice) * 100 : 100;

  const handleSaveDueDate = async () => {
    await onUpdateDueDate(dueDateValue);
    setEditingDueDate(false);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Payment Tracking</CardTitle>
        <CardDescription>Track received vs pending payments</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Received vs Pending */}
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
              <Badge variant="destructive">OVERDUE</Badge>
              <span className="text-sm text-slate-600">as per stage: {overdueInfo.current_stage_name}</span>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-slate-600">Expected ({overdueInfo.cumulative_percentage}%)</p>
                <p className="font-bold text-slate-900">{formatCurrency(overdueInfo.expected_amount)}</p>
              </div>
              <div>
                <p className="text-slate-600">Received</p>
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
              No overdue payments for current stage: {overdueInfo.current_stage_name}
            </span>
          </div>
        )}
        
        {overdueInfo && !overdueInfo.current_stage && (
          <div className="p-3 bg-slate-50 border rounded-lg text-sm text-slate-500">
            No payment stage set by admin. Overdue tracking unavailable.
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
                    value={dueDateValue}
                    onChange={(e) => setDueDateValue(e.target.value)}
                    className="w-40"
                    data-testid="payment-due-date-input"
                  />
                  <Button size="sm" onClick={handleSaveDueDate}>
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
                    {paymentDueDate 
                      ? new Date(paymentDueDate).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
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
  );
};

export default PaymentTrackingCard;
