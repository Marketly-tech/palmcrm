import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { ScrollArea } from "../components/ui/scroll-area";
import { Button } from "../components/ui/button";
import {
  Users,
  FileText,
  AlertTriangle,
  Clock,
  IndianRupee,
  TrendingUp,
  Activity,
  Calendar,
  Bell,
  ChevronRight,
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
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [activities, setActivities] = useState([]);
  const [paymentsOverview, setPaymentsOverview] = useState(null);
  const [upcomingDueDates, setUpcomingDueDates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, activitiesRes, paymentsRes, dueDatesRes] = await Promise.all([
        axios.get(`${API}/dashboard/stats`),
        axios.get(`${API}/dashboard/recent-activities`),
        axios.get(`${API}/payments/overview`),
        axios.get(`${API}/dashboard/upcoming-due-dates`),
      ]);
      setStats(statsRes.data);
      setActivities(activitiesRes.data);
      setPaymentsOverview(paymentsRes.data);
      setUpcomingDueDates(dueDatesRes.data || []);
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

  // Calculate countdown days
  const getCountdownDays = (dueDate) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const due = new Date(dueDate);
    due.setHours(0, 0, 0, 0);
    const diffTime = due - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const getCountdownBadge = (days) => {
    if (days < 0) return { text: `${Math.abs(days)} days overdue`, className: "bg-red-100 text-red-700" };
    if (days === 0) return { text: "Due Today!", className: "bg-red-500 text-white animate-pulse" };
    if (days === 1) return { text: "Due Tomorrow", className: "bg-orange-500 text-white" };
    if (days <= 3) return { text: `${days} days left`, className: "bg-orange-100 text-orange-700" };
    if (days <= 5) return { text: `${days} days left`, className: "bg-amber-100 text-amber-700" };
    return { text: `${days} days left`, className: "bg-green-100 text-green-700" };
  };

  const COLORS = ["hsl(199, 89%, 48%)", "hsl(168, 80%, 28%)", "hsl(43, 74%, 66%)", "hsl(0, 84%, 60%)"];

  const handleExport = async (type, format) => {
    try {
      const endpoint = type === 'customers' 
        ? `/export/customers/${format}` 
        : `/export/payments/${format}`;
      
      const response = await axios.get(`${API}${endpoint}`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { 
        type: format === 'excel' 
          ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
          : 'text/csv' 
      });
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `RRL_${type.charAt(0).toUpperCase() + type.slice(1)}_Export.${format === 'excel' ? 'xlsx' : 'csv'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Export failed. Please try again.');
    }
  };

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

      {/* Revenue & Pending (Admin only) */}
      {hasRole("admin") && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="hover:shadow-md transition-shadow border-green-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Revenue Collected</p>
                  <p className="text-3xl font-bold text-green-600 mt-1">{formatCurrency(stats?.total_revenue || 0)}</p>
                  <p className="text-sm text-green-600 mt-1">{(100 - (stats?.pending_percentage || 0)).toFixed(1)}% collected</p>
                </div>
                <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
                  <IndianRupee className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="hover:shadow-md transition-shadow border-amber-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Pending Payments</p>
                  <p className="text-3xl font-bold text-amber-600 mt-1">{formatCurrency(stats?.total_pending || 0)}</p>
                  <p className="text-sm text-amber-600 mt-1">{(stats?.pending_percentage || 0).toFixed(1)}% pending</p>
                </div>
                <div className="h-12 w-12 rounded-full bg-amber-100 flex items-center justify-center">
                  <Clock className="h-6 w-6 text-amber-600" />
                </div>
              </div>
              {/* Progress bar */}
              <div className="mt-4">
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-green-500 transition-all duration-500"
                    style={{ width: `${100 - (stats?.pending_percentage || 0)}%` }}
                  />
                </div>
                <p className="text-xs text-muted-foreground mt-1">Payment Collection Progress</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Export Data Card (Admin/Manager only) */}
        {hasRole("admin") && (
          <Card>
            <CardHeader>
              <CardTitle className="font-heading flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                Export CRM Data
              </CardTitle>
              <CardDescription>Download all data for reporting and analysis</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <Button 
                  variant="outline" 
                  className="h-20 flex flex-col items-center justify-center gap-2"
                  onClick={() => handleExport('customers', 'csv')}
                  data-testid="export-customers-csv"
                >
                  <FileText className="h-6 w-6 text-green-600" />
                  <span className="text-sm">Customers CSV</span>
                </Button>
                <Button 
                  variant="outline" 
                  className="h-20 flex flex-col items-center justify-center gap-2"
                  onClick={() => handleExport('customers', 'excel')}
                  data-testid="export-customers-excel"
                >
                  <FileText className="h-6 w-6 text-blue-600" />
                  <span className="text-sm">Customers Excel</span>
                </Button>
                <Button 
                  variant="outline" 
                  className="h-20 flex flex-col items-center justify-center gap-2"
                  onClick={() => handleExport('payments', 'csv')}
                  data-testid="export-payments-csv"
                >
                  <IndianRupee className="h-6 w-6 text-amber-600" />
                  <span className="text-sm">Payments CSV</span>
                </Button>
                <Button 
                  variant="outline" 
                  className="h-20 flex flex-col items-center justify-center gap-2 opacity-50"
                  disabled
                >
                  <Activity className="h-6 w-6 text-purple-600" />
                  <span className="text-sm">Activity Logs</span>
                </Button>
              </div>
              <p className="text-xs text-muted-foreground text-center">Click to download data in your preferred format</p>
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

      {/* Agreement Due Dates Countdown - Next 5 Days */}
      {upcomingDueDates.length > 0 && (
        <Card className="border-2 border-orange-200 bg-gradient-to-r from-orange-50 to-amber-50">
          <CardHeader>
            <CardTitle className="font-heading flex items-center gap-2">
              <Bell className="h-5 w-5 text-orange-500 animate-bounce" />
              Agreement Due Date Countdown
            </CardTitle>
            <CardDescription>
              Customers with agreement due dates in the next 5 days (10 days from booking to complete agreement)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {upcomingDueDates.map((item, index) => {
                const countdownDays = getCountdownDays(item.due_date);
                const badge = getCountdownBadge(countdownDays);
                return (
                  <div
                    key={index}
                    className="p-4 bg-white rounded-lg border border-orange-200 hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => navigate(`/customers/${item.customer_id}`)}
                    data-testid={`due-date-card-${index}`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="font-semibold text-slate-900">{item.customer_name}</p>
                        <p className="text-sm text-slate-500">{item.project} - {item.unit_number}</p>
                      </div>
                      <Badge className={badge.className}>
                        {badge.text}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center mt-3">
                      <div className="flex items-center gap-2 text-sm text-slate-600">
                        <Calendar className="w-4 h-4" />
                        <span>Agreement Due: {new Date(item.due_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</span>
                      </div>
                      <ChevronRight className="w-4 h-4 text-slate-400" />
                    </div>
                    <p className="text-xs text-slate-500 mt-2">Booked: {new Date(item.booking_date).toLocaleDateString('en-IN')}</p>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

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
