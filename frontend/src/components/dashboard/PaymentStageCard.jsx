import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Label } from "../ui/label";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "../ui/select";
import { Settings, Loader2, TrendingUp, Wallet, AlertTriangle } from "lucide-react";

const StatTile = ({ icon: Icon, label, value, tone, testId, percent, percentLabel }) => {
  const tones = {
    blue: { card: "bg-blue-50 border-blue-200 text-blue-700", bar: "bg-blue-500", track: "bg-blue-200/60" },
    emerald: { card: "bg-emerald-50 border-emerald-200 text-emerald-700", bar: "bg-emerald-500", track: "bg-emerald-200/60" },
    red: { card: "bg-red-50 border-red-200 text-red-700", bar: "bg-red-500", track: "bg-red-200/60" },
  };
  const t = tones[tone];
  return (
    <div className={`p-3 rounded-lg border ${t.card}`} data-testid={testId}>
      <div className="flex items-center gap-2">
        <Icon className="w-4 h-4 opacity-80" />
        <p className="text-[11px] uppercase tracking-wide opacity-80">{label}</p>
      </div>
      <p className="text-2xl font-bold mt-1">{value}</p>
      {percent !== undefined && percent !== null && (
        <div className="mt-2" data-testid={`${testId}-progress`}>
          <div className="flex items-center justify-between text-[11px] opacity-90">
            <span>{percentLabel}</span>
            <span className="font-semibold">{percent.toFixed(1)}%</span>
          </div>
          <div className={`mt-1 h-1.5 w-full rounded-full overflow-hidden ${t.track}`}>
            <div
              className={`h-full ${t.bar} transition-all`}
              style={{ width: `${Math.min(100, Math.max(0, percent))}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

const PaymentStageCard = ({
  paymentStages, currentStage, stageOverdue,
  updatingStage, onStageChange, onNavigate, formatCurrency,
}) => {
  const overdueCustomers = stageOverdue?.overdue_customers || [];
  const overdueCount = stageOverdue?.overdue_count ?? overdueCustomers.length;
  const totalOverdue = stageOverdue?.total_overdue_amount ?? 0;
  const totalExpected = stageOverdue?.total_expected_at_slab ?? 0;
  const totalCollected = stageOverdue?.total_collected_cumulative ?? 0;
  const slabPct = stageOverdue?.cumulative_percentage ?? 0;
  const stageName = stageOverdue?.current_stage_name || currentStage?.current_stage_name;
  const hasStageSet = Boolean(stageOverdue?.current_stage);

  return (
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

        {hasStageSet && (
          <div className="mt-5">
            <p className="text-sm font-medium text-slate-700 mb-3">
              {stageName} <span className="text-slate-500 font-normal">— {slabPct}% slab</span>
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
              <StatTile
                icon={TrendingUp}
                label="Total Revenue (Expected)"
                value={formatCurrency(totalExpected)}
                tone="blue"
                testId="slab-total-expected"
              />
              <StatTile
                icon={Wallet}
                label="Total Collected (Cumulative)"
                value={formatCurrency(totalCollected)}
                tone="emerald"
                testId="slab-total-collected"
                percent={totalExpected > 0 ? (totalCollected / totalExpected) * 100 : 0}
                percentLabel="of expected"
              />
              <StatTile
                icon={AlertTriangle}
                label="Total Overdue at Slab"
                value={formatCurrency(totalOverdue)}
                tone="red"
                testId="slab-total-overdue"
                percent={totalExpected > 0 ? (totalOverdue / totalExpected) * 100 : 0}
                percentLabel="of expected"
              />
            </div>

            {overdueCount > 0 && (
              <>
                <div className="grid grid-cols-2 gap-3 mb-3">
                  <div className="p-3 rounded-lg bg-red-50 border border-red-200" data-testid="overdue-customers-summary">
                    <p className="text-xs text-red-700/80 uppercase tracking-wide">Overdue Customers</p>
                    <p className="text-2xl font-bold text-red-700" data-testid="overdue-customers-count">{overdueCount}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-red-50 border border-red-200" data-testid="overdue-total-summary">
                    <p className="text-xs text-red-700/80 uppercase tracking-wide">Total Overdue Amount</p>
                    <p className="text-2xl font-bold text-red-700" data-testid="overdue-total-amount">
                      {formatCurrency(totalOverdue)}
                    </p>
                  </div>
                </div>
                <p className="text-sm font-medium text-slate-700 mb-2">Overdue Customers ({overdueCount})</p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {overdueCustomers.slice(0, 6).map((item) => (
                    <div
                      key={item.customer_id}
                      className="p-3 bg-red-50 rounded-lg border border-red-200 cursor-pointer hover:shadow-sm transition-shadow"
                      onClick={() => onNavigate(`/customers/${item.customer_id}`)}
                      data-testid={`overdue-customer-${item.customer_id}`}
                    >
                      <p className="font-medium text-sm text-slate-900">{item.customer_name}</p>
                      <p className="text-xs text-slate-500">{item.unit_number}</p>
                      <p className="text-sm font-semibold text-red-600 mt-1">{formatCurrency(item.overdue_amount)} overdue</p>
                    </div>
                  ))}
                </div>
                {overdueCount > 6 && <p className="text-xs text-muted-foreground mt-2">+{overdueCount - 6} more overdue customers</p>}
              </>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PaymentStageCard;
