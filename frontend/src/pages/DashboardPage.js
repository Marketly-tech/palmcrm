import { useState, useEffect } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { ScrollArea } from "../components/ui/scroll-area";
import {
  Users,
  FileText,
  AlertTriangle,
  Clock,
  IndianRupee,
  TrendingUp,
  Activity,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DashboardPage = () => {
  const { user, hasRole } = useAuth();
  const [stats, setStats] = useState(null);
  const [activities, setActivities] = useState([]);
  const [paymentsOverview, setPaymentsOverview] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, activitiesRes, paymentsRes] = await Promise.all([
        axios.get(`${API}/dashboard/stats`),
        axios.get(`${API}/dashboard/recent-activities`),
        axios.get(`${API}/payments/overview`),
      ]);
      setStats(statsRes.data);
      setActivities(activitiesRes.data);
      setPaymentsOverview(paymentsRes.data);
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const COLORS = ["hsl(199, 89%, 48%)", "hsl(168, 80%, 28%)", "hsl(43, 74%, 66%)", "hsl(0, 84%, 60%)"];

  const pieData = stats
    ? [
        { name: "Paid", value: stats.payment_status_breakdown.paid || 0 },
        { name: "Pending", value: stats.payment_status_breakdown.pending || 0 },
        { name: "Partial", value: stats.payment_status_breakdown.partial || 0 },
        { name: "Overdue", value: stats.payment_status_breakdown.overdue || 0 },
      ]
    : [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="dashboard-page">
      {/* Welcome */}
      <div>
        <h1 className="font-heading text-3xl font-bold text-slate-900">
          Welcome back, {user?.name?.split(" ")[0]}!
        </h1>
        <p className="text-slate-500 mt-1">Here's what's happening with your CRM today.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Customers</p>
                <p className="text-3xl font-bold text-slate-900 mt-1">{stats?.total_customers || 0}</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Pending Agreements</p>
                <p className="text-3xl font-bold text-slate-900 mt-1">{stats?.pending_agreements || 0}</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-purple-100 flex items-center justify-center">
                <FileText className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Due This Week</p>
                <p className="text-3xl font-bold text-slate-900 mt-1">{stats?.payments_due_this_week || 0}</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-amber-100 flex items-center justify-center">
                <Clock className="h-6 w-6 text-amber-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow border-red-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Overdue Payments</p>
                <p className="text-3xl font-bold text-red-600 mt-1">{stats?.overdue_payments || 0}</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Revenue (Admin only) */}
      {hasRole("admin") && stats?.total_revenue > 0 && (
        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Revenue Collected</p>
                <p className="text-3xl font-bold text-green-600 mt-1">{formatCurrency(stats.total_revenue)}</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
                <IndianRupee className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Revenue Chart (Admin only) */}
        {hasRole("admin") && stats?.monthly_revenue?.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="font-heading flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" />
                Monthly Revenue Trend
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stats.monthly_revenue}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="month" tick={{ fill: "#64748b", fontSize: 12 }} />
                    <YAxis tick={{ fill: "#64748b", fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#fff",
                        border: "1px solid #e2e8f0",
                        borderRadius: "8px",
                      }}
                      formatter={(value) => [formatCurrency(value), "Revenue"]}
                    />
                    <Bar dataKey="revenue" fill="hsl(199, 89%, 48%)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Payment Status Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="font-heading">Payment Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center">
              {pieData.some((d) => d.value > 0) ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
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
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                  />
                  <span className="text-sm text-slate-600">
                    {entry.name}: {entry.value}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Overdue & Upcoming Payments */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Overdue Payments */}
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="font-heading flex items-center gap-2 text-red-600">
              <AlertTriangle className="h-5 w-5" />
              Overdue Payments
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-64">
              {paymentsOverview?.overdue?.length > 0 ? (
                <div className="space-y-3">
                  {paymentsOverview.overdue.slice(0, 5).map((item, index) => (
                    <div key={index} className="p-3 bg-red-50 rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium text-slate-900">{item.customer_name}</p>
                          <p className="text-sm text-slate-500">
                            {item.installment_name} - {item.unit_number}
                          </p>
                        </div>
                        <p className="font-semibold text-red-600">{formatCurrency(item.amount)}</p>
                      </div>
                      <p className="text-xs text-red-500 mt-1">Due: {item.due_date}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-muted-foreground py-8">No overdue payments</p>
              )}
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Upcoming Payments */}
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
                    <div key={index} className="p-3 bg-amber-50 rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium text-slate-900">{item.customer_name}</p>
                          <p className="text-sm text-slate-500">
                            {item.installment_name} - {item.unit_number}
                          </p>
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
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="font-heading flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            Recent Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-64">
            {activities.length > 0 ? (
              <div className="space-y-3">
                {activities.map((activity, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 hover:bg-slate-50 rounded-lg">
                    <div className="h-8 w-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0">
                      <Activity className="h-4 w-4 text-slate-500" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-900">
                        <span className="font-medium">{activity.user_name}</span>{" "}
                        {activity.action} {activity.entity_type}
                      </p>
                      <p className="text-xs text-slate-500 truncate">{activity.details}</p>
                      <p className="text-xs text-slate-400 mt-1">
                        {new Date(activity.timestamp).toLocaleString()}
                      </p>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {activity.entity_type}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-muted-foreground py-8">No recent activity</p>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardPage;
