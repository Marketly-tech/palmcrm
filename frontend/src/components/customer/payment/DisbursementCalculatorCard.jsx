import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../../ui/card";
import { Label } from "../../ui/label";
import { Input } from "../../ui/input";
import { Button } from "../../ui/button";

const DisbursementCalculatorCard = ({
  customer,
  disbursementPercentage,
  setDisbursementPercentage,
  formatCurrency,
}) => {
  const amount = (customer.total_price || 0) * (disbursementPercentage / 100);

  return (
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
              {formatCurrency(amount)}
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
            <span className="font-bold text-blue-700">{formatCurrency(amount)}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default DisbursementCalculatorCard;
