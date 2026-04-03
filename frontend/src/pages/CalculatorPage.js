import { useState } from "react";
import axios from "axios";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Separator } from "../components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table";
import { toast } from "sonner";
import {
  IndianRupee,
  FileText,
  Percent,
  Receipt,
  CreditCard,
  RotateCcw,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CalculatorPage = () => {
  // Disbursement Calculator State
  const [disbursementData, setDisbursementData] = useState({
    total_flat_value: "",
    disbursement_percentage: "30",
  });
  const [disbursementResult, setDisbursementResult] = useState(null);
  
  // Payment Tracking State
  const [trackingData, setTrackingData] = useState({
    total_flat_value: "",
    total_received: "",
  });
  const [trackingResult, setTrackingResult] = useState(null);
  
  // Payment Schedule Template
  const [scheduleTemplate, setScheduleTemplate] = useState([]);

  const handleDisbursementCalculate = async () => {
    if (!disbursementData.total_flat_value) {
      toast.error("Please enter total flat value");
      return;
    }

    try {
      const response = await axios.post(`${API}/calculator/disbursement`, {
        total_flat_value: parseFloat(disbursementData.total_flat_value),
        disbursement_percentage: parseFloat(disbursementData.disbursement_percentage),
      });
      setDisbursementResult(response.data);
      
      // Also fetch schedule template with this total
      fetchScheduleTemplate(parseFloat(disbursementData.total_flat_value));
    } catch (error) {
      toast.error("Failed to calculate disbursement");
    }
  };

  const handleTrackingCalculate = async () => {
    if (!trackingData.total_flat_value || !trackingData.total_received) {
      toast.error("Please enter both total value and received amount");
      return;
    }

    try {
      const response = await axios.post(
        `${API}/calculator/payment-tracking?total_flat_value=${trackingData.total_flat_value}&total_received=${trackingData.total_received}`
      );
      setTrackingResult(response.data);
    } catch (error) {
      toast.error("Failed to calculate payment tracking");
    }
  };

  const fetchScheduleTemplate = async (totalAmount) => {
    try {
      const response = await axios.get(`${API}/calculator/payment-schedule-template?total_amount=${totalAmount || 0}`);
      setScheduleTemplate(response.data);
    } catch (error) {
      console.error("Failed to fetch schedule template:", error);
    }
  };

  const handleReset = () => {
    setDisbursementData({
      total_flat_value: "",
      disbursement_percentage: "30",
    });
    setTrackingData({
      total_flat_value: "",
      total_received: "",
    });
    setDisbursementResult(null);
    setTrackingResult(null);
    setScheduleTemplate([]);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount || 0);
  };

  return (
    <div className="space-y-6" data-testid="payment-tracking-page">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="font-heading text-3xl font-bold text-slate-900">Payment Tracking</h1>
          <p className="text-slate-500 mt-1">Calculate disbursements, track payments, and view payment schedules</p>
        </div>
        <Button variant="outline" onClick={handleReset} data-testid="reset-btn">
          <RotateCcw className="w-4 h-4 mr-2" />
          Reset All
        </Button>
      </div>

      <Tabs defaultValue="disbursement" className="space-y-4">
        <TabsList className="grid grid-cols-3 w-full max-w-xl">
          <TabsTrigger value="disbursement" data-testid="tab-disbursement">
            <Receipt className="w-4 h-4 mr-2" />
            Disbursement
          </TabsTrigger>
          <TabsTrigger value="tracking" data-testid="tab-tracking">
            <Percent className="w-4 h-4 mr-2" />
            Payment Tracking
          </TabsTrigger>
          <TabsTrigger value="schedule" data-testid="tab-schedule">
            <FileText className="w-4 h-4 mr-2" />
            Schedule
          </TabsTrigger>
        </TabsList>

        {/* Disbursement Tab */}
        <TabsContent value="disbursement">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Receipt className="w-5 h-5 text-primary" />
                  Disbursement Calculator
                </CardTitle>
                <CardDescription>
                  Formula: Total Flat Value × Disbursement % = Disbursement Amount
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Total Flat Value (₹)</Label>
                  <Input
                    type="number"
                    value={disbursementData.total_flat_value}
                    onChange={(e) => setDisbursementData(prev => ({ ...prev, total_flat_value: e.target.value }))}
                    placeholder="e.g., 11295900"
                    data-testid="disbursement-total-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Disbursement Percentage (%)</Label>
                  <Input
                    type="number"
                    value={disbursementData.disbursement_percentage}
                    onChange={(e) => setDisbursementData(prev => ({ ...prev, disbursement_percentage: e.target.value }))}
                    placeholder="e.g., 30"
                    data-testid="disbursement-percent-input"
                  />
                </div>
                {/* Quick percentage buttons */}
                <div className="flex gap-2">
                  {[30, 50, 70, 100].map((pct) => (
                    <Button
                      key={pct}
                      variant="outline"
                      size="sm"
                      onClick={() => setDisbursementData(prev => ({ ...prev, disbursement_percentage: pct.toString() }))}
                      className={disbursementData.disbursement_percentage === pct.toString() ? "border-primary" : ""}
                    >
                      {pct}%
                    </Button>
                  ))}
                </div>
                <Button onClick={handleDisbursementCalculate} className="w-full" data-testid="disbursement-calc-btn">
                  Calculate Disbursement
                </Button>
              </CardContent>
            </Card>

            <Card className={disbursementResult ? "border-primary" : ""}>
              <CardHeader>
                <CardTitle>Disbursement Result</CardTitle>
              </CardHeader>
              <CardContent>
                {disbursementResult ? (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center py-2">
                      <span className="text-slate-600">Total Flat Value</span>
                      <span className="font-semibold">{formatCurrency(disbursementResult.total_flat_value)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-slate-600">Disbursement %</span>
                      <span className="font-semibold">{disbursementResult.disbursement_percentage}%</span>
                    </div>
                    <Separator />
                    <div className="flex justify-between items-center py-4 bg-green-50 rounded-lg px-4">
                      <span className="font-semibold text-lg">Disbursement Amount</span>
                      <span className="font-bold text-2xl text-green-600">
                        {formatCurrency(disbursementResult.disbursement_amount)}
                      </span>
                    </div>
                    <p className="text-xs text-amber-600 bg-amber-50 p-2 rounded">
                      Note: Email with Demand Letter will be sent automatically when disbursement is processed
                    </p>
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-500">
                    <Receipt className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                    <p>Enter values and calculate</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Payment Tracking Tab */}
        <TabsContent value="tracking">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Percent className="w-5 h-5 text-primary" />
                  Payment Tracking Calculator
                </CardTitle>
                <CardDescription>
                  Track payment received percentage and balance
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Total Flat Value (₹)</Label>
                  <Input
                    type="number"
                    value={trackingData.total_flat_value}
                    onChange={(e) => setTrackingData(prev => ({ ...prev, total_flat_value: e.target.value }))}
                    placeholder="e.g., 11295900"
                    data-testid="tracking-total-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Total Received (₹)</Label>
                  <Input
                    type="number"
                    value={trackingData.total_received}
                    onChange={(e) => setTrackingData(prev => ({ ...prev, total_received: e.target.value }))}
                    placeholder="e.g., 2000000"
                    data-testid="tracking-received-input"
                  />
                </div>
                <Button onClick={handleTrackingCalculate} className="w-full" data-testid="tracking-calc-btn">
                  Calculate
                </Button>
              </CardContent>
            </Card>

            <Card className={trackingResult ? "border-primary" : ""}>
              <CardHeader>
                <CardTitle>Payment Status</CardTitle>
              </CardHeader>
              <CardContent>
                {trackingResult ? (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center py-2">
                      <span className="text-slate-600">Total Flat Value</span>
                      <span className="font-semibold">{formatCurrency(trackingResult.total_flat_value)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-slate-600">Total Received</span>
                      <span className="font-semibold text-green-600">{formatCurrency(trackingResult.total_received)}</span>
                    </div>
                    <Separator />
                    <div className="flex justify-between items-center py-2">
                      <span className="text-slate-600">Balance Amount</span>
                      <span className="font-semibold text-red-600">{formatCurrency(trackingResult.balance_amount)}</span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 pt-4">
                      <div className="text-center p-4 bg-green-50 rounded-lg">
                        <p className="text-sm text-slate-600">Received %</p>
                        <p className="text-2xl font-bold text-green-600">{trackingResult.payment_received_percentage.toFixed(2)}%</p>
                      </div>
                      <div className="text-center p-4 bg-red-50 rounded-lg">
                        <p className="text-sm text-slate-600">Pending %</p>
                        <p className="text-2xl font-bold text-red-600">{trackingResult.payment_pending_percentage.toFixed(2)}%</p>
                      </div>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="mt-4">
                      <div className="h-4 bg-slate-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-green-500 transition-all duration-500"
                          style={{ width: `${trackingResult.payment_received_percentage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-500">
                    <Percent className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                    <p>Enter values and calculate</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Payment Schedule Tab */}
        <TabsContent value="schedule">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-primary" />
                Payment Schedule Template
              </CardTitle>
              <CardDescription>
                Standard 13-milestone payment structure based on construction progress
              </CardDescription>
            </CardHeader>
            <CardContent>
              {scheduleTemplate.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">#</TableHead>
                      <TableHead>Milestone</TableHead>
                      <TableHead className="text-center">%</TableHead>
                      <TableHead className="text-right">Amount</TableHead>
                      <TableHead className="text-right">Cumulative</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {scheduleTemplate.map((item, index) => (
                      <TableRow key={item.id || item.installment_name || index}>
                        <TableCell className="font-mono">{index + 1}</TableCell>
                        <TableCell>{item.installment_name}</TableCell>
                        <TableCell className="text-center">{item.percentage}%</TableCell>
                        <TableCell className="text-right font-mono">{formatCurrency(item.amount)}</TableCell>
                        <TableCell className="text-right font-mono text-primary">{formatCurrency(item.cumulative)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-12 text-slate-500">
                  <FileText className="w-16 h-16 mx-auto mb-4 text-slate-300" />
                  <p className="text-lg">Enter total value in Disbursement tab</p>
                  <p className="text-sm mt-1">Payment schedule will be generated based on total flat value</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CalculatorPage;
