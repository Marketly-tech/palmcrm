import { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { toast } from "sonner";
import {
  Clock,
  AlertTriangle,
  CheckCircle,
  IndianRupee,
  Loader2,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PaymentsPage = () => {
  const [paymentsOverview, setPaymentsOverview] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPayments();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- runs once on mount
  }, []);

  const fetchPayments = async () => {
    try {
      const response = await axios.get(`${API}/payments/overview`);
      setPaymentsOverview(response.data);
    } catch (error) {
      toast.error("Failed to fetch payments");
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

  const handleUpdateStatus = async (customerId, itemId, status) => {
    try {
      await axios.put(`${API}/payments/item/${customerId}/${itemId}`, {
        payment_status: status,
        payment_date: status === "paid" ? new Date().toISOString().split("T")[0] : null,
      });
      fetchPayments();
      toast.success("Payment status updated");
    } catch (error) {
      toast.error("Failed to update status");
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      pending: "bg-yellow-100 text-yellow-700",
      paid: "bg-green-100 text-green-700",
      overdue: "bg-red-100 text-red-700",
      partial: "bg-blue-100 text-blue-700",
    };
    return styles[status] || "bg-slate-100 text-slate-700";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  const overdueCount = paymentsOverview?.overdue?.length || 0;
  const upcomingCount = paymentsOverview?.upcoming?.length || 0;
  const pendingCount = paymentsOverview?.pending?.length || 0;

  const overdueTotal = paymentsOverview?.overdue?.reduce((sum, item) => sum + item.amount, 0) || 0;
  const upcomingTotal = paymentsOverview?.upcoming?.reduce((sum, item) => sum + item.amount, 0) || 0;

  return (
    <div className="space-y-6" data-testid="payments-page">
      {/* Header */}
      <div>
        <h1 className="font-heading text-3xl font-bold text-slate-900">Payments</h1>
        <p className="text-slate-500 mt-1">Track and manage all payment schedules</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-red-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500">Overdue Payments</p>
                <p className="text-3xl font-bold text-red-600 mt-1">{overdueCount}</p>
                <p className="text-sm text-red-500 mt-1">{formatCurrency(overdueTotal)}</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-amber-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500">Due This Week</p>
                <p className="text-3xl font-bold text-amber-600 mt-1">{upcomingCount}</p>
                <p className="text-sm text-amber-500 mt-1">{formatCurrency(upcomingTotal)}</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-amber-100 flex items-center justify-center">
                <Clock className="h-6 w-6 text-amber-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500">Pending Payments</p>
                <p className="text-3xl font-bold text-slate-900 mt-1">{pendingCount}</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-slate-100 flex items-center justify-center">
                <IndianRupee className="h-6 w-6 text-slate-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overdue" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overdue" data-testid="tab-overdue">
            <AlertTriangle className="w-4 h-4 mr-2 text-red-500" />
            Overdue ({overdueCount})
          </TabsTrigger>
          <TabsTrigger value="upcoming" data-testid="tab-upcoming">
            <Clock className="w-4 h-4 mr-2 text-amber-500" />
            Upcoming ({upcomingCount})
          </TabsTrigger>
          <TabsTrigger value="pending" data-testid="tab-pending">
            <IndianRupee className="w-4 h-4 mr-2" />
            All Pending ({pendingCount})
          </TabsTrigger>
        </TabsList>

        {/* Overdue Tab */}
        <TabsContent value="overdue">
          <Card>
            <CardHeader>
              <CardTitle className="text-red-600">Overdue Payments</CardTitle>
              <CardDescription>Payments that are past their due date</CardDescription>
            </CardHeader>
            <CardContent>
              {paymentsOverview?.overdue?.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Customer</TableHead>
                      <TableHead>Unit</TableHead>
                      <TableHead>Installment</TableHead>
                      <TableHead>Amount</TableHead>
                      <TableHead>Due Date</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {paymentsOverview.overdue.map((item, index) => (
                      <TableRow key={`overdue-${index}`}>
                        <TableCell>
                          <div>
                            <p className="font-medium">{item.customer_name}</p>
                            <p className="text-sm text-slate-500">{item.customer_ref}</p>
                          </div>
                        </TableCell>
                        <TableCell className="font-mono">{item.unit_number}</TableCell>
                        <TableCell>{item.installment_name}</TableCell>
                        <TableCell className="font-semibold text-red-600">
                          {formatCurrency(item.amount)}
                        </TableCell>
                        <TableCell className="text-red-600">{item.due_date}</TableCell>
                        <TableCell>
                          <Badge className={getStatusBadge("overdue")}>Overdue</Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-300" />
                  <p>No overdue payments</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Upcoming Tab */}
        <TabsContent value="upcoming">
          <Card>
            <CardHeader>
              <CardTitle className="text-amber-600">Upcoming Payments</CardTitle>
              <CardDescription>Payments due within the next 7 days</CardDescription>
            </CardHeader>
            <CardContent>
              {paymentsOverview?.upcoming?.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Customer</TableHead>
                      <TableHead>Unit</TableHead>
                      <TableHead>Installment</TableHead>
                      <TableHead>Amount</TableHead>
                      <TableHead>Due Date</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {paymentsOverview.upcoming.map((item, index) => (
                      <TableRow key={`upcoming-${index}`}>
                        <TableCell>
                          <div>
                            <p className="font-medium">{item.customer_name}</p>
                            <p className="text-sm text-slate-500">{item.customer_ref}</p>
                          </div>
                        </TableCell>
                        <TableCell className="font-mono">{item.unit_number}</TableCell>
                        <TableCell>{item.installment_name}</TableCell>
                        <TableCell className="font-semibold text-amber-600">
                          {formatCurrency(item.amount)}
                        </TableCell>
                        <TableCell>{item.due_date}</TableCell>
                        <TableCell>
                          <Badge className={getStatusBadge("pending")}>Pending</Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <Clock className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                  <p>No upcoming payments this week</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Pending Tab */}
        <TabsContent value="pending">
          <Card>
            <CardHeader>
              <CardTitle>All Pending Payments</CardTitle>
              <CardDescription>Future payments not yet due</CardDescription>
            </CardHeader>
            <CardContent>
              {paymentsOverview?.pending?.length > 0 ? (
                <ScrollArea className="h-96">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Customer</TableHead>
                        <TableHead>Unit</TableHead>
                        <TableHead>Installment</TableHead>
                        <TableHead>Amount</TableHead>
                        <TableHead>Due Date</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {paymentsOverview.pending.map((item, index) => (
                        <TableRow key={`pending-${index}`}>
                          <TableCell>
                            <div>
                              <p className="font-medium">{item.customer_name}</p>
                              <p className="text-sm text-slate-500">{item.customer_ref}</p>
                            </div>
                          </TableCell>
                          <TableCell className="font-mono">{item.unit_number}</TableCell>
                          <TableCell>{item.installment_name}</TableCell>
                          <TableCell className="font-semibold">
                            {formatCurrency(item.amount)}
                          </TableCell>
                          <TableCell>{item.due_date}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </ScrollArea>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <CheckCircle className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                  <p>No pending payments</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PaymentsPage;
