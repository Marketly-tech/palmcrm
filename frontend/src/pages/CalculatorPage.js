import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Separator } from "../components/ui/separator";
import { Switch } from "../components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
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
  Calculator,
  IndianRupee,
  Loader2,
  RotateCcw,
  FileText,
  Percent,
  Building2,
  Car,
  Receipt,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CalculatorPage = () => {
  // Price Calculator State
  const [formData, setFormData] = useState({
    unit_number: "",
    unit_type: "3BHK",
    floor_number: 0,
    saleable_area: "",
    rate_per_sqft: "6600",
    include_club_house: true,
    club_house_charges: "200000",
    additional_parking_count: "0",
    additional_parking_rate: "300000",
    gst_percentage: "5",
    labour_cess_percentage: "0.70",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  
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

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleCalculate = async () => {
    if (!formData.saleable_area || !formData.rate_per_sqft) {
      toast.error("Please enter saleable area and rate per sq.ft");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/calculator/price`, {
        unit_number: formData.unit_number || null,
        unit_type: formData.unit_type || null,
        floor_number: parseInt(formData.floor_number) || 0,
        saleable_area: parseFloat(formData.saleable_area) || 0,
        rate_per_sqft: parseFloat(formData.rate_per_sqft) || 0,
        include_club_house: formData.include_club_house,
        club_house_charges: parseFloat(formData.club_house_charges) || 200000,
        additional_parking_count: parseInt(formData.additional_parking_count) || 0,
        additional_parking_rate: parseFloat(formData.additional_parking_rate) || 300000,
        gst_percentage: parseFloat(formData.gst_percentage) || 5,
        labour_cess_percentage: parseFloat(formData.labour_cess_percentage) || 0.70,
      });
      setResult(response.data);
      
      // Auto-populate disbursement and tracking with the total
      setDisbursementData(prev => ({ ...prev, total_flat_value: response.data.total_flat_value.toString() }));
      setTrackingData(prev => ({ ...prev, total_flat_value: response.data.total_flat_value.toString() }));
      
      // Fetch payment schedule template with the total
      fetchScheduleTemplate(response.data.total_flat_value);
      
      toast.success("Price calculated successfully");
    } catch (error) {
      toast.error("Failed to calculate price");
    } finally {
      setLoading(false);
    }
  };

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
    setFormData({
      unit_number: "",
      unit_type: "3BHK",
      floor_number: 0,
      saleable_area: "",
      rate_per_sqft: "6600",
      include_club_house: true,
      club_house_charges: "200000",
      additional_parking_count: "0",
      additional_parking_rate: "300000",
      gst_percentage: "5",
      labour_cess_percentage: "0.70",
    });
    setResult(null);
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

  // Number to words (Indian system)
  const numberToWords = (num) => {
    if (num === 0) return "Zero";
    
    const ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"];
    const tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"];
    const teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"];

    const convertLessThanThousand = (n) => {
      let result = "";
      if (n >= 100) {
        result += ones[Math.floor(n / 100)] + " Hundred ";
        n %= 100;
      }
      if (n >= 20) {
        result += tens[Math.floor(n / 10)] + " ";
        n %= 10;
      }
      if (n >= 10) {
        result += teens[n - 10] + " ";
        n = 0;
      }
      if (n > 0) {
        result += ones[n] + " ";
      }
      return result;
    };

    let result = "";
    const crore = Math.floor(num / 10000000);
    const lakh = Math.floor((num % 10000000) / 100000);
    const thousand = Math.floor((num % 100000) / 1000);
    const remainder = Math.floor(num % 1000);

    if (crore > 0) result += convertLessThanThousand(crore) + "Crore ";
    if (lakh > 0) result += convertLessThanThousand(lakh) + "Lakh ";
    if (thousand > 0) result += convertLessThanThousand(thousand) + "Thousand ";
    if (remainder > 0) result += convertLessThanThousand(remainder);

    return result.trim();
  };

  return (
    <div className="space-y-6" data-testid="calculator-page">
      {/* Header */}
      <div>
        <h1 className="font-heading text-3xl font-bold text-slate-900">Price Calculator</h1>
        <p className="text-slate-500 mt-1">Calculate property prices, disbursements, and payment schedules</p>
      </div>

      <Tabs defaultValue="price" className="space-y-4">
        <TabsList className="grid grid-cols-4 w-full max-w-2xl">
          <TabsTrigger value="price" data-testid="tab-price">
            <Calculator className="w-4 h-4 mr-2" />
            Price Breakup
          </TabsTrigger>
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

        {/* Price Breakup Tab */}
        <TabsContent value="price">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Input Form */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calculator className="w-5 h-5 text-primary" />
                  Price Breakup Calculator
                </CardTitle>
                <CardDescription>
                  Formula: (Rate × Saleable Area) + Club House + Parking + Labour Cess (0.70%) + GST (5%)
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="unit_number">Unit Number</Label>
                    <Input
                      id="unit_number"
                      name="unit_number"
                      value={formData.unit_number}
                      onChange={handleInputChange}
                      placeholder="e.g., 0701"
                      data-testid="unit-number-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="unit_type">Unit Type</Label>
                    <Select
                      value={formData.unit_type}
                      onValueChange={(value) => setFormData(prev => ({ ...prev, unit_type: value }))}
                    >
                      <SelectTrigger data-testid="unit-type-select">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="2BHK">2 BHK</SelectItem>
                        <SelectItem value="3BHK">3 BHK</SelectItem>
                        <SelectItem value="4BHK">4 BHK</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="floor_number">Floor Number</Label>
                    <Input
                      id="floor_number"
                      name="floor_number"
                      type="number"
                      value={formData.floor_number}
                      onChange={handleInputChange}
                      placeholder="e.g., 7"
                      data-testid="floor-number-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="saleable_area">Saleable Area (sq.ft) *</Label>
                    <Input
                      id="saleable_area"
                      name="saleable_area"
                      type="number"
                      value={formData.saleable_area}
                      onChange={handleInputChange}
                      placeholder="e.g., 1630"
                      data-testid="saleable-area-input"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="rate_per_sqft">Rate per sq.ft (₹) *</Label>
                  <Input
                    id="rate_per_sqft"
                    name="rate_per_sqft"
                    type="number"
                    value={formData.rate_per_sqft}
                    onChange={handleInputChange}
                    placeholder="e.g., 6600"
                    data-testid="rate-input"
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-slate-500" />
                    <Label htmlFor="include_club_house">Include Club House (₹2L)</Label>
                  </div>
                  <Switch
                    id="include_club_house"
                    checked={formData.include_club_house}
                    onCheckedChange={(checked) => setFormData(prev => ({ ...prev, include_club_house: checked }))}
                    data-testid="club-house-switch"
                  />
                </div>

                <div className="flex items-center gap-4 p-3 bg-slate-50 rounded-lg">
                  <Car className="w-4 h-4 text-slate-500" />
                  <div className="flex-1">
                    <Label htmlFor="additional_parking_count">Additional Parking (₹3L each)</Label>
                    <Input
                      id="additional_parking_count"
                      name="additional_parking_count"
                      type="number"
                      min="0"
                      value={formData.additional_parking_count}
                      onChange={handleInputChange}
                      className="mt-1"
                      data-testid="parking-count-input"
                    />
                  </div>
                </div>

                <div className="flex gap-3 pt-4">
                  <Button
                    onClick={handleCalculate}
                    className="flex-1"
                    disabled={loading}
                    data-testid="calculate-btn"
                  >
                    {loading ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <Calculator className="w-4 h-4 mr-2" />
                    )}
                    Calculate
                  </Button>
                  <Button variant="outline" onClick={handleReset} data-testid="reset-btn">
                    <RotateCcw className="w-4 h-4 mr-2" />
                    Reset
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Result */}
            <Card className={result ? "border-primary" : ""}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <IndianRupee className="w-5 h-5 text-primary" />
                  Price Breakdown
                </CardTitle>
              </CardHeader>
              <CardContent>
                {result ? (
                  <div className="space-y-4">
                    {result.unit_number && (
                      <div className="flex justify-between items-center py-2 bg-slate-50 px-3 rounded">
                        <span className="text-slate-600">Unit</span>
                        <span className="font-semibold">{result.unit_number} ({result.unit_type})</span>
                      </div>
                    )}
                    
                    <div className="flex justify-between items-center py-2">
                      <span className="text-slate-600">Base Price ({result.saleable_area} sq.ft × ₹{result.rate_per_sqft})</span>
                      <span className="font-semibold">{formatCurrency(result.base_price)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-slate-600">Club House & Infrastructure</span>
                      <span className="font-semibold">{formatCurrency(result.club_house_charges)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-slate-600">Additional Parking</span>
                      <span className="font-semibold">{formatCurrency(result.additional_parking_charges)}</span>
                    </div>
                    
                    <Separator />
                    
                    <div className="flex justify-between items-center py-2">
                      <span className="text-slate-600">Subtotal</span>
                      <span className="font-semibold">{formatCurrency(result.subtotal_before_taxes)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-slate-600">Labour Cess (0.70%)</span>
                      <span className="font-semibold">{formatCurrency(result.labour_cess)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-slate-600">GST (5%)</span>
                      <span className="font-semibold">{formatCurrency(result.gst_amount)}</span>
                    </div>
                    
                    <Separator />
                    
                    <div className="flex justify-between items-center py-4 bg-primary/10 rounded-lg px-4 -mx-4">
                      <span className="font-semibold text-lg">Total Flat Value</span>
                      <span className="font-bold text-2xl text-primary">
                        {formatCurrency(result.total_flat_value)}
                      </span>
                    </div>

                    <div className="flex justify-between items-center py-2 bg-blue-50 px-3 rounded">
                      <span className="text-slate-600">UDS (Undivided Share)</span>
                      <span className="font-semibold">{result.uds}</span>
                    </div>

                    <div className="p-4 bg-slate-50 rounded-lg">
                      <p className="text-sm text-slate-600">
                        <span className="font-medium">In Words:</span>{" "}
                        {numberToWords(Math.round(result.total_flat_value))} Rupees Only
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-500">
                    <Calculator className="w-16 h-16 mx-auto mb-4 text-slate-300" />
                    <p className="text-lg">Enter values and click Calculate</p>
                    <p className="text-sm mt-1">Results will appear here</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

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
                      <TableRow key={index}>
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
                  <p className="text-lg">Calculate a price first</p>
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
