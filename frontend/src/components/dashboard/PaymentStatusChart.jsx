import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import {
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip,
} from "recharts";

const COLORS = ["hsl(199, 89%, 48%)", "hsl(168, 80%, 28%)", "hsl(43, 74%, 66%)", "hsl(0, 84%, 60%)"];

const PaymentStatusChart = ({ stats }) => {
  const pieData = stats
    ? [
        { name: "Paid", value: stats.payment_status_breakdown.paid || 0 },
        { name: "Pending", value: stats.payment_status_breakdown.pending || 0 },
        { name: "Partial", value: stats.payment_status_breakdown.partial || 0 },
        { name: "Overdue", value: stats.payment_status_breakdown.overdue || 0 },
      ]
    : [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="font-heading">Payment Status Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64 flex items-center justify-center">
          {pieData.some((d) => d.value > 0) ? (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-muted-foreground">No payment data available</p>
          )}
        </div>
        <div className="flex justify-center gap-4 mt-4">
          {pieData.map((entry, index) => (
            <div key={entry.name} className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
              <span className="text-sm text-slate-600">{entry.name}: {entry.value}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default PaymentStatusChart;
