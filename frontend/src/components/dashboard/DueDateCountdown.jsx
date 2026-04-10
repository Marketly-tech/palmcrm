import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Badge } from "../ui/badge";
import { Bell, Calendar, ChevronRight } from "lucide-react";

const getCountdownDays = (dueDate) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const due = new Date(dueDate);
  due.setHours(0, 0, 0, 0);
  return Math.ceil((due - today) / (1000 * 60 * 60 * 24));
};

const getCountdownBadge = (days) => {
  if (days < 0) return { text: `${Math.abs(days)} days overdue`, className: "bg-red-100 text-red-700" };
  if (days === 0) return { text: "Due Today!", className: "bg-red-500 text-white animate-pulse" };
  if (days === 1) return { text: "Due Tomorrow", className: "bg-orange-500 text-white" };
  if (days <= 3) return { text: `${days} days left`, className: "bg-orange-100 text-orange-700" };
  if (days <= 5) return { text: `${days} days left`, className: "bg-amber-100 text-amber-700" };
  return { text: `${days} days left`, className: "bg-green-100 text-green-700" };
};

const DueDateCountdown = ({ upcomingDueDates, onNavigate }) => {
  if (!upcomingDueDates.length) return null;

  return (
    <Card className="border-2 border-orange-200 bg-gradient-to-r from-orange-50 to-amber-50">
      <CardHeader>
        <CardTitle className="font-heading flex items-center gap-2">
          <Bell className="h-5 w-5 text-orange-500 animate-bounce" />
          Agreement Due Date Countdown
        </CardTitle>
        <CardDescription>Customers with agreement due dates in the next 5 days (10 days from booking to complete agreement)</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {upcomingDueDates.map((item) => {
            const countdownDays = getCountdownDays(item.due_date);
            const badge = getCountdownBadge(countdownDays);
            return (
              <div key={item.customer_id} className="p-4 bg-white rounded-lg border border-orange-200 hover:shadow-md transition-shadow cursor-pointer" onClick={() => onNavigate(`/customers/${item.customer_id}`)} data-testid={`due-date-card-${item.customer_id}`}>
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="font-semibold text-slate-900">{item.customer_name}</p>
                    <p className="text-sm text-slate-500">{item.project} - {item.unit_number}</p>
                  </div>
                  <Badge className={badge.className}>{badge.text}</Badge>
                </div>
                <div className="flex justify-between items-center mt-3">
                  <div className="flex items-center gap-2 text-sm text-slate-600">
                    <Calendar className="w-4 h-4" />
                    <span>Agreement Due: {new Date(item.due_date).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}</span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-400" />
                </div>
                <p className="text-xs text-slate-500 mt-2">Booked: {new Date(item.booking_date).toLocaleDateString("en-IN")}</p>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default DueDateCountdown;
