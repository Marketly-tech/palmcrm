import { useState, useEffect } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { logError } from "../utils/logger";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { ScrollArea } from "../components/ui/scroll-area";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table";
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
  LineChart,
  Line,
} from "recharts";
import {
  Activity,
  Loader2,
  TrendingUp,
  Users,
  FileText,
  CreditCard,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ReportsPage = () => {
  const { hasRole } = useAuth();
  const [stats, setStats] = useState(null);
  const [activities, setActivities] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReportData();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- runs once on mount
  }, []);

  const fetchReportData = async () => {
    try {
      const [statsRes, activitiesRes, customersRes] = await Promise.all([
        axios.get(`${API}/dashboard/stats`),
        axios.get(`${API}/activity-logs?limit=50`),
        axios.get(`${API}/customers`),
      ]);
      setStats(statsRes.data);
      setActivities(activitiesRes.data);
      setCustomers(customersRes.data.customers);
    } catch (error) {
      logError("Reports data fetch failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount || 0);
  };

  const COLORS = ["hsl(199, 89%, 48%)", "hsl(168, 80%, 28%)", "hsl(43, 74%, 66%)", "hsl(0, 84%, 60%)"];

  // Agreement status breakdown
  const agreementData = customers.reduce((acc, customer) => {
    const status = customer.agreement_status || "draft";
    acc[status] = (acc[status] || 0) + 1;
    return acc;
  }, {});

  const agreementChartData = Object.entries(agreementData).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
  }));

  // Project distribution
  const projectData = customers.reduce((acc, customer) => {
    const project = customer.project || "Unknown";
    acc[project] = (acc[project] || 0) + 1;
    return acc;
  }, {});

  const projectChartData = Object.entries(projectData).map(([name, value]) => ({
    name: name.replace("RRL ", ""),
    customers: value,
  }));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="reports-page">
      {/* Header */}
      <div>
        <h1 className="font-heading text-3xl font-bold text-slate-900">Reports</h1>
        <p className="text-slate-500 mt-1">Analytics and activity reports</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500">Total Customers</p>
                <p className="text-3xl font-bold text-slate-900">{stats?.total_customers || 0}</p>
              </div>
              <Users className="h-8 w-8 text-primary" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500">Pending Agreements</p>
                <p className="text-3xl font-bold text-slate-900">{stats?.pending_agreements || 0}</p>
              </div>
              <FileText className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500">Overdue Payments</p>
                <p className="text-3xl font-bold text-red-600">{stats?.overdue_payments || 0}</p>
              </div>
              <CreditCard className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
        {hasRole("admin") && (
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500">Total Revenue</p>
                  <p className="text-2xl font-bold text-green-600">{formatCurrency(stats?.total_revenue || 0)}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Project Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Customers by Project</CardTitle>
            <CardDescription>Distribution across RRL projects</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              {projectChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={projectChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="name" tick={{ fill: "#64748b", fontSize: 11 }} />
                    <YAxis tick={{ fill: "#64748b", fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#fff",
                        border: "1px solid #e2e8f0",
                        borderRadius: "8px",
                      }}
                    />
                    <Bar dataKey="customers" fill="hsl(199, 89%, 48%)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full text-slate-500">
                  No data available
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Agreement Status */}
        <Card>
          <CardHeader>
            <CardTitle>Agreement Status</CardTitle>
            <CardDescription>Breakdown by agreement stage</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center">
              {agreementChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={agreementChartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}`}
                    >
                      {agreementChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-slate-500">No data available</div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Activity Log */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-primary" />
            Activity Log
          </CardTitle>
          <CardDescription>Recent actions in the system</CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-96">
            {activities.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Time</TableHead>
                    <TableHead>User</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Entity</TableHead>
                    <TableHead>Details</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {activities.map((activity) => (
                    <TableRow key={activity.id || activity.timestamp}>
                      <TableCell className="text-sm text-slate-500">
                        {new Date(activity.timestamp).toLocaleString()}
                      </TableCell>
                      <TableCell className="font-medium">{activity.user_name}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{activity.action}</Badge>
                      </TableCell>
                      <TableCell className="capitalize">{activity.entity_type}</TableCell>
                      <TableCell className="max-w-xs truncate text-slate-600">
                        {activity.details}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-8 text-slate-500">
                No activity logs yet
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
};

export default ReportsPage;
