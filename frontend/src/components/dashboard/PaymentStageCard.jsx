import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Label } from "../ui/label";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "../ui/select";
import { Settings, Loader2 } from "lucide-react";

const PaymentStageCard = ({
  paymentStages, currentStage, stageOverdue,
  updatingStage, onStageChange, onNavigate, formatCurrency,
}) => (
  <Card data-testid="payment-stage-card">
    <CardHeader>
      <CardTitle className="font-heading flex items-center gap-2">
        <Settings className="h-5 w-5 text-primary" />
        Disbursement Payment Stage
      </CardTitle>
      <CardDescription>Set the current construction milestone to calculate overdue payments</CardDescription>
    </CardHeader>
    <CardContent>
      <div className="flex flex-col sm:flex-row items-start sm:items-end gap-4">
        <div className="flex-1 w-full sm:max-w-md">
          <Label htmlFor="payment-stage-select" className="text-sm text-muted-foreground mb-2 block">Current Stage</Label>
          <Select value={currentStage?.current_stage || ""} onValueChange={onStageChange} disabled={updatingStage}>
            <SelectTrigger id="payment-stage-select" data-testid="payment-stage-select" className="w-full">
              <SelectValue placeholder="Select construction stage" />
            </SelectTrigger>
            <SelectContent>
              {paymentStages.map((stage) => (
                <SelectItem key={stage.key} value={stage.key}>{stage.name} ({stage.cumulative}%)</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        {updatingStage && <Loader2 className="h-5 w-5 animate-spin text-primary" />}
        {currentStage?.updated_by && <p className="text-xs text-muted-foreground">Last updated by {currentStage.updated_by}</p>}
      </div>
      {stageOverdue && stageOverdue.length > 0 && (
        <div className="mt-4">
          <p className="text-sm font-medium text-slate-700 mb-2">Overdue Customers ({stageOverdue.length})</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
            {stageOverdue.slice(0, 6).map((item) => (
              <div key={item.customer_id} className="p-3 bg-red-50 rounded-lg border border-red-200 cursor-pointer hover:shadow-sm transition-shadow" onClick={() => onNavigate(`/customers/${item.customer_id}`)} data-testid={`overdue-customer-${item.customer_id}`}>
                <p className="font-medium text-sm text-slate-900">{item.customer_name}</p>
                <p className="text-xs text-slate-500">{item.unit_number}</p>
                <p className="text-sm font-semibold text-red-600 mt-1">{formatCurrency(item.overdue_amount)} overdue</p>
              </div>
            ))}
          </div>
          {stageOverdue.length > 6 && <p className="text-xs text-muted-foreground mt-2">+{stageOverdue.length - 6} more overdue customers</p>}
        </div>
      )}
    </CardContent>
  </Card>
);

export default PaymentStageCard;
