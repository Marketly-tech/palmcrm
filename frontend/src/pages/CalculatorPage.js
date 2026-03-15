import { useState } from "react";
import axios from "axios";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Separator } from "../components/ui/separator";
import { toast } from "sonner";
import {
  Calculator,
  IndianRupee,
  Loader2,
  RotateCcw,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CalculatorPage = () => {
  const [formData, setFormData] = useState({
    carpet_area: "",
    rate_per_sqft: "",
    floor_rise_charges: "",
    parking_charges: "",
    gst_percentage: "5",
    other_charges: "",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleCalculate = async () => {
    if (!formData.carpet_area || !formData.rate_per_sqft) {
      toast.error("Please enter carpet area and rate per sq.ft");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/calculator/price`, {
        carpet_area: parseFloat(formData.carpet_area) || 0,
        rate_per_sqft: parseFloat(formData.rate_per_sqft) || 0,
        floor_rise_charges: parseFloat(formData.floor_rise_charges) || 0,
        parking_charges: parseFloat(formData.parking_charges) || 0,
        gst_percentage: parseFloat(formData.gst_percentage) || 0,
        other_charges: parseFloat(formData.other_charges) || 0,
      });
      setResult(response.data);
    } catch (error) {
      toast.error("Failed to calculate price");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({
      carpet_area: "",
      rate_per_sqft: "",
      floor_rise_charges: "",
      parking_charges: "",
      gst_percentage: "5",
      other_charges: "",
    });
    setResult(null);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount || 0);
  };

  return (
    <div className="space-y-6" data-testid="calculator-page">
      {/* Header */}
      <div>
        <h1 className="font-heading text-3xl font-bold text-slate-900">Price Calculator</h1>
        <p className="text-slate-500 mt-1">Calculate total property price with all charges</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="w-5 h-5 text-primary" />
              Price Inputs
            </CardTitle>
            <CardDescription>Enter property details to calculate total price</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="carpet_area">Carpet Area (sq.ft) *</Label>
                <Input
                  id="carpet_area"
                  name="carpet_area"
                  type="number"
                  value={formData.carpet_area}
                  onChange={handleInputChange}
                  placeholder="e.g., 1200"
                  data-testid="carpet-area-input"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="rate_per_sqft">Rate per sq.ft (₹) *</Label>
                <Input
                  id="rate_per_sqft"
                  name="rate_per_sqft"
                  type="number"
                  value={formData.rate_per_sqft}
                  onChange={handleInputChange}
                  placeholder="e.g., 5500"
                  data-testid="rate-input"
                />
              </div>
            </div>

            <Separator />

            <div className="space-y-2">
              <Label htmlFor="floor_rise_charges">Floor Rise Charges (₹)</Label>
              <Input
                id="floor_rise_charges"
                name="floor_rise_charges"
                type="number"
                value={formData.floor_rise_charges}
                onChange={handleInputChange}
                placeholder="e.g., 50000"
                data-testid="floor-rise-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="parking_charges">Parking Charges (₹)</Label>
              <Input
                id="parking_charges"
                name="parking_charges"
                type="number"
                value={formData.parking_charges}
                onChange={handleInputChange}
                placeholder="e.g., 300000"
                data-testid="parking-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="other_charges">Other Charges (₹)</Label>
              <Input
                id="other_charges"
                name="other_charges"
                type="number"
                value={formData.other_charges}
                onChange={handleInputChange}
                placeholder="e.g., 100000"
                data-testid="other-charges-input"
              />
            </div>

            <Separator />

            <div className="space-y-2">
              <Label htmlFor="gst_percentage">GST Percentage (%)</Label>
              <Input
                id="gst_percentage"
                name="gst_percentage"
                type="number"
                value={formData.gst_percentage}
                onChange={handleInputChange}
                placeholder="e.g., 5"
                data-testid="gst-input"
              />
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
            <CardDescription>Calculated property price details</CardDescription>
          </CardHeader>
          <CardContent>
            {result ? (
              <div className="space-y-4">
                <div className="flex justify-between items-center py-2">
                  <span className="text-slate-600">Base Price</span>
                  <span className="font-semibold">{formatCurrency(result.base_price)}</span>
                </div>
                <div className="flex justify-between items-center py-2">
                  <span className="text-slate-600">Floor Rise Charges</span>
                  <span className="font-semibold">{formatCurrency(result.floor_rise)}</span>
                </div>
                <div className="flex justify-between items-center py-2">
                  <span className="text-slate-600">Parking Charges</span>
                  <span className="font-semibold">{formatCurrency(result.parking)}</span>
                </div>
                <div className="flex justify-between items-center py-2">
                  <span className="text-slate-600">Other Charges</span>
                  <span className="font-semibold">{formatCurrency(result.other_charges)}</span>
                </div>
                
                <Separator />
                
                <div className="flex justify-between items-center py-2">
                  <span className="text-slate-600">Subtotal</span>
                  <span className="font-semibold">{formatCurrency(result.subtotal)}</span>
                </div>
                <div className="flex justify-between items-center py-2">
                  <span className="text-slate-600">GST ({formData.gst_percentage}%)</span>
                  <span className="font-semibold">{formatCurrency(result.gst_amount)}</span>
                </div>
                
                <Separator />
                
                <div className="flex justify-between items-center py-4 bg-primary/10 rounded-lg px-4 -mx-4">
                  <span className="font-semibold text-lg">Total Agreement Value</span>
                  <span className="font-bold text-2xl text-primary">
                    {formatCurrency(result.total_agreement_value)}
                  </span>
                </div>

                {/* Words representation */}
                <div className="p-4 bg-slate-50 rounded-lg">
                  <p className="text-sm text-slate-600">
                    <span className="font-medium">In Words:</span>{" "}
                    {numberToWords(result.total_agreement_value)} Rupees Only
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
    </div>
  );
};

// Helper function to convert number to words (Indian system)
function numberToWords(num) {
  if (num === 0) return "Zero";
  
  const ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"];
  const tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"];
  const teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"];

  function convertLessThanThousand(n) {
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
  }

  let result = "";
  const crore = Math.floor(num / 10000000);
  const lakh = Math.floor((num % 10000000) / 100000);
  const thousand = Math.floor((num % 100000) / 1000);
  const remainder = num % 1000;

  if (crore > 0) result += convertLessThanThousand(crore) + "Crore ";
  if (lakh > 0) result += convertLessThanThousand(lakh) + "Lakh ";
  if (thousand > 0) result += convertLessThanThousand(thousand) + "Thousand ";
  if (remainder > 0) result += convertLessThanThousand(remainder);

  return result.trim();
}

export default CalculatorPage;
