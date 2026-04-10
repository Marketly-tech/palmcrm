import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { ScrollArea } from "../ui/scroll-area";
import { Clock } from "lucide-react";

const UpcomingPayments = ({ paymentsOverview, formatCurrency }) => (
  <Card>
    <CardHeader>
      <CardTitle className="font-heading flex items-center gap-2">
        <Clock className="h-5 w-5 text-amber-500" />
        Upcoming Payments (This Week)
      </CardTitle>
    </CardHeader>
    <CardContent>
      <ScrollArea className="h-64">
        {paymentsOverview?.upcoming?.length > 0 ? (
          <div className="space-y-3">
            {paymentsOverview.upcoming.slice(0, 5).map((item, index) => (
              <div key={item.customer_id ? `${item.customer_id}-${item.installment_name}` : index} className="p-3 bg-amber-50 rounded-lg">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium text-slate-900">{item.customer_name}</p>
                    <p className="text-sm text-slate-500">{item.installment_name} - {item.unit_number}</p>
                  </div>
                  <p className="font-semibold text-amber-600">{formatCurrency(item.amount)}</p>
                </div>
                <p className="text-xs text-amber-600 mt-1">Due: {item.due_date}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-center text-muted-foreground py-8">No upcoming payments this week</p>
        )}
      </ScrollArea>
    </CardContent>
  </Card>
);

export default UpcomingPayments;
