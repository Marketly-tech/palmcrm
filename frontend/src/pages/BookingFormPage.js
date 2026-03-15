import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Separator } from "../components/ui/separator";
import { Textarea } from "../components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { toast } from "sonner";
import {
  User,
  Building2,
  CreditCard,
  CheckCircle,
  Loader2,
  Eye,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../components/ui/dialog";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const BookingFormPage = () => {
  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submissionResult, setSubmissionResult] = useState(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  
  // Projects list
  const projects = [
    { name: "RRL Palm Altezze", towers: ["Tower-1", "Tower-2"] },
    { name: "RRL NC 216", towers: ["Tower-A", "Tower-B"] },
    { name: "RRL Palacio", towers: ["Tower-1"] },
    { name: "RRL Nature Woods", towers: ["Tower-1"] },
    { name: "RRL Towers", towers: ["Tower-1", "Tower-2"] },
    { name: "RRL Complex", towers: ["Tower-A"] },
  ];

  // BHK Types
  const bhkTypes = ["2BHK", "2.5BHK", "3BHK", "3.5BHK", "4BHK"];
  
  const [formData, setFormData] = useState({
    // Primary Applicant
    name: "",
    phone: "",
    email: "",
    father_name: "",
    date_of_birth: "",
    pan_number: "",
    aadhar_number: "",
    address: "",
    company: "",
    designation: "",
    nationality: "Indian",
    
    // Co-Applicant
    co_applicant_name: "",
    co_applicant_phone: "",
    co_applicant_email: "",
    co_applicant_pan: "",
    co_applicant_aadhar: "",
    
    // Property Details
    project: "",
    tower: "",
    unit_number: "",
    bhk_type: "",
    floor: "",
    carpet_area: "",
    saleable_area: "",
    rate_per_sqft: "6600",
    parking: "1",
    additional_parking: "0",
    
    // Payment
    booking_amount: "",
    transaction_details: "",
    transaction_date: "",
    transaction_bank: "",
    
    // Finance
    finance_type: "self",
    finance_bank: "",
    
    // Remarks
    remarks: "",
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Calculate price based on inputs
  const calculatePrice = () => {
    const saleableArea = parseFloat(formData.saleable_area) || 0;
    const ratePerSqft = parseFloat(formData.rate_per_sqft) || 0;
    const floor = parseInt(formData.floor) || 0;
    const additionalParking = parseInt(formData.additional_parking) || 0;
    
    // Floor rise: ₹50 per sqft for every floor above ground
    const floorRise = floor > 0 ? floor * 50 : 0;
    const effectiveRate = ratePerSqft + floorRise;
    
    const basePrice = saleableArea * effectiveRate;
    const clubHouse = 200000; // ₹2L
    const parkingCharges = additionalParking * 300000; // ₹3L per additional
    const subtotal = basePrice + clubHouse + parkingCharges;
    const labourCess = subtotal * 0.007; // 0.70%
    const gst = subtotal * 0.05; // 5%
    const total = subtotal + labourCess + gst;
    
    return {
      basePrice,
      floorRise: saleableArea * floorRise,
      effectiveRate,
      clubHouse,
      parkingCharges,
      subtotal,
      labourCess,
      gst,
      total
    };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const priceCalc = calculatePrice();
      
      const payload = {
        ...formData,
        floor: parseInt(formData.floor) || 0,
        carpet_area: parseFloat(formData.carpet_area) || 0,
        saleable_area: parseFloat(formData.saleable_area) || 0,
        rate_per_sqft: parseFloat(formData.rate_per_sqft) || 0,
        additional_parking: parseInt(formData.additional_parking) || 0,
        booking_amount: parseFloat(formData.booking_amount) || 0,
        total_price: priceCalc.total,
        base_price: priceCalc.basePrice,
        club_house_charges: priceCalc.clubHouse,
        additional_parking_charges: priceCalc.parkingCharges,
        labour_cess: priceCalc.labourCess,
        gst_amount: priceCalc.gst,
      };

      const response = await axios.post(`${API}/public/booking-form`, payload);
      setSubmissionResult(response.data);
      setSubmitted(true);
      toast.success("Booking submitted successfully!");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to submit booking");
    } finally {
      setSubmitting(false);
    }
  };

  const validateStep = (stepNum) => {
    switch (stepNum) {
      case 1:
        return formData.name && formData.phone && formData.email;
      case 2:
        return formData.project && formData.tower && formData.unit_number && 
               formData.bhk_type && formData.saleable_area && formData.rate_per_sqft;
      case 3:
        return true; // Payment details are optional
      default:
        return true;
    }
  };

  const nextStep = () => {
    if (validateStep(step)) {
      setStep(step + 1);
    } else {
      toast.error("Please fill all required fields");
    }
  };

  const prevStep = () => {
    setStep(step - 1);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount || 0);
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-50 to-pink-100 flex items-center justify-center p-4">
        <Card className="max-w-lg w-full">
          <CardContent className="p-8 text-center">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-10 h-10 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Booking Submitted!</h2>
            <p className="text-slate-600 mb-6">
              Thank you for your booking. Our team will contact you shortly.
            </p>
            <div className="bg-slate-50 p-4 rounded-lg text-left mb-6">
              <p className="text-sm text-slate-500">Reference Number</p>
              <p className="text-lg font-mono font-bold text-primary">{submissionResult?.customer_id}</p>
            </div>
            <p className="text-sm text-slate-500">
              A confirmation email will be sent to {formData.email}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const priceCalc = calculatePrice();

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 to-pink-100 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">RRL Builders</h1>
          <p className="text-slate-600">Property Booking Form</p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-8">
          {[1, 2, 3, 4].map((s) => (
            <div key={s} className="flex items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                  s <= step
                    ? "bg-primary text-white"
                    : "bg-slate-200 text-slate-500"
                }`}
              >
                {s}
              </div>
              {s < 4 && (
                <div
                  className={`w-16 h-1 ${
                    s < step ? "bg-primary" : "bg-slate-200"
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {step === 1 && <><User className="w-5 h-5" /> Applicant Details</>}
              {step === 2 && <><Building2 className="w-5 h-5" /> Property Details</>}
              {step === 3 && <><CreditCard className="w-5 h-5" /> Payment Information</>}
              {step === 4 && <><Eye className="w-5 h-5" /> Review & Submit</>}
            </CardTitle>
            <CardDescription>
              {step === 1 && "Enter primary and co-applicant details"}
              {step === 2 && "Enter property details and pricing"}
              {step === 3 && "Enter booking payment details"}
              {step === 4 && "Review your information before submitting"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit}>
              {/* Step 1: Applicant Details */}
              {step === 1 && (
                <div className="space-y-6">
                  <div className="space-y-4">
                    <h3 className="font-semibold text-slate-700">Primary Applicant</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="name">Full Name *</Label>
                        <Input
                          id="name"
                          name="name"
                          value={formData.name}
                          onChange={handleInputChange}
                          required
                          data-testid="applicant-name-input"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="phone">Phone Number *</Label>
                        <Input
                          id="phone"
                          name="phone"
                          value={formData.phone}
                          onChange={handleInputChange}
                          required
                          data-testid="applicant-phone-input"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="email">Email *</Label>
                        <Input
                          id="email"
                          name="email"
                          type="email"
                          value={formData.email}
                          onChange={handleInputChange}
                          required
                          data-testid="applicant-email-input"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="father_name">Father/Spouse Name</Label>
                        <Input
                          id="father_name"
                          name="father_name"
                          value={formData.father_name}
                          onChange={handleInputChange}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="date_of_birth">Date of Birth</Label>
                        <Input
                          id="date_of_birth"
                          name="date_of_birth"
                          type="date"
                          value={formData.date_of_birth}
                          onChange={handleInputChange}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="nationality">Nationality</Label>
                        <Select
                          value={formData.nationality}
                          onValueChange={(value) => setFormData(prev => ({ ...prev, nationality: value }))}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Indian">Indian</SelectItem>
                            <SelectItem value="NRI">NRI</SelectItem>
                            <SelectItem value="OCI">OCI</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="pan_number">PAN Number</Label>
                        <Input
                          id="pan_number"
                          name="pan_number"
                          value={formData.pan_number}
                          onChange={handleInputChange}
                          placeholder="ABCDE1234F"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="aadhar_number">Aadhaar Number</Label>
                        <Input
                          id="aadhar_number"
                          name="aadhar_number"
                          value={formData.aadhar_number}
                          onChange={handleInputChange}
                          placeholder="1234 5678 9012"
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="address">Address</Label>
                      <Textarea
                        id="address"
                        name="address"
                        value={formData.address}
                        onChange={handleInputChange}
                        rows={2}
                      />
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="company">Company</Label>
                        <Input
                          id="company"
                          name="company"
                          value={formData.company}
                          onChange={handleInputChange}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="designation">Designation</Label>
                        <Input
                          id="designation"
                          name="designation"
                          value={formData.designation}
                          onChange={handleInputChange}
                        />
                      </div>
                    </div>
                  </div>

                  <Separator />

                  <div className="space-y-4">
                    <h3 className="font-semibold text-slate-700">Co-Applicant (Optional)</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="co_applicant_name">Full Name</Label>
                        <Input
                          id="co_applicant_name"
                          name="co_applicant_name"
                          value={formData.co_applicant_name}
                          onChange={handleInputChange}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="co_applicant_phone">Phone</Label>
                        <Input
                          id="co_applicant_phone"
                          name="co_applicant_phone"
                          value={formData.co_applicant_phone}
                          onChange={handleInputChange}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="co_applicant_email">Email</Label>
                        <Input
                          id="co_applicant_email"
                          name="co_applicant_email"
                          type="email"
                          value={formData.co_applicant_email}
                          onChange={handleInputChange}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="co_applicant_pan">PAN Number</Label>
                        <Input
                          id="co_applicant_pan"
                          name="co_applicant_pan"
                          value={formData.co_applicant_pan}
                          onChange={handleInputChange}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 2: Property Details */}
              {step === 2 && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="project">Project *</Label>
                      <Select
                        value={formData.project}
                        onValueChange={(value) => setFormData(prev => ({ ...prev, project: value, tower: "" }))}
                      >
                        <SelectTrigger data-testid="project-select">
                          <SelectValue placeholder="Select project" />
                        </SelectTrigger>
                        <SelectContent>
                          {projects.map((p) => (
                            <SelectItem key={p.name} value={p.name}>
                              {p.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="tower">Tower *</Label>
                      <Select
                        value={formData.tower}
                        onValueChange={(value) => setFormData(prev => ({ ...prev, tower: value }))}
                        disabled={!formData.project}
                      >
                        <SelectTrigger data-testid="tower-select">
                          <SelectValue placeholder="Select tower" />
                        </SelectTrigger>
                        <SelectContent>
                          {projects.find(p => p.name === formData.project)?.towers.map((t) => (
                            <SelectItem key={t} value={t}>
                              {t}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="unit_number">Unit Number *</Label>
                      <Input
                        id="unit_number"
                        name="unit_number"
                        value={formData.unit_number}
                        onChange={handleInputChange}
                        placeholder="e.g., 0701"
                        required
                        data-testid="unit-number-input"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="bhk_type">BHK Type *</Label>
                      <Select
                        value={formData.bhk_type}
                        onValueChange={(value) => setFormData(prev => ({ ...prev, bhk_type: value }))}
                      >
                        <SelectTrigger data-testid="bhk-type-select">
                          <SelectValue placeholder="Select BHK" />
                        </SelectTrigger>
                        <SelectContent>
                          {bhkTypes.map((bhk) => (
                            <SelectItem key={bhk} value={bhk}>
                              {bhk}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="floor">Floor Number *</Label>
                      <Input
                        id="floor"
                        name="floor"
                        type="number"
                        value={formData.floor}
                        onChange={handleInputChange}
                        placeholder="e.g., 7"
                        data-testid="floor-input"
                      />
                      <p className="text-xs text-slate-500">Floor rise: ₹50/sqft per floor</p>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="carpet_area">Carpet Area (sq.ft)</Label>
                      <Input
                        id="carpet_area"
                        name="carpet_area"
                        type="number"
                        value={formData.carpet_area}
                        onChange={handleInputChange}
                        placeholder="e.g., 1200"
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
                        required
                        data-testid="saleable-area-input"
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
                        placeholder="e.g., 6600"
                        required
                        data-testid="rate-input"
                      />
                      <p className="text-xs text-slate-500">
                        Effective rate: ₹{(parseFloat(formData.rate_per_sqft) || 0) + ((parseInt(formData.floor) || 0) * 50)}/sqft (incl. floor rise)
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="parking">Covered Car Parking</Label>
                      <Input
                        id="parking"
                        name="parking"
                        value={formData.parking}
                        onChange={handleInputChange}
                        placeholder="1"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="additional_parking">Additional Parking (₹3L each)</Label>
                      <Input
                        id="additional_parking"
                        name="additional_parking"
                        type="number"
                        min="0"
                        value={formData.additional_parking}
                        onChange={handleInputChange}
                      />
                    </div>
                  </div>

                  {/* Live Price Calculator */}
                  {formData.saleable_area && formData.rate_per_sqft && (
                    <div className="mt-6 p-4 bg-primary/5 border border-primary/20 rounded-lg">
                      <h3 className="font-semibold text-slate-700 mb-3">Price Calculation Preview</h3>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <span className="text-slate-600">Base Price ({formData.saleable_area} × ₹{priceCalc.effectiveRate}):</span>
                        <span className="font-medium text-right">{formatCurrency(priceCalc.basePrice)}</span>
                        
                        {priceCalc.floorRise > 0 && (
                          <>
                            <span className="text-slate-600">Floor Rise (Floor {formData.floor}):</span>
                            <span className="font-medium text-right">+{formatCurrency(priceCalc.floorRise)}</span>
                          </>
                        )}
                        
                        <span className="text-slate-600">Club House & Infrastructure:</span>
                        <span className="font-medium text-right">{formatCurrency(priceCalc.clubHouse)}</span>
                        
                        <span className="text-slate-600">Additional Parking ({formData.additional_parking || 0}):</span>
                        <span className="font-medium text-right">{formatCurrency(priceCalc.parkingCharges)}</span>
                        
                        <span className="text-slate-600">Labour Cess (0.70%):</span>
                        <span className="font-medium text-right">{formatCurrency(priceCalc.labourCess)}</span>
                        
                        <span className="text-slate-600">GST (5%):</span>
                        <span className="font-medium text-right">{formatCurrency(priceCalc.gst)}</span>
                        
                        <Separator className="col-span-2 my-2" />
                        
                        <span className="font-semibold text-primary">Total Flat Value:</span>
                        <span className="font-bold text-primary text-right text-lg">{formatCurrency(priceCalc.total)}</span>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Step 3: Payment Information */}
              {step === 3 && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="booking_amount">Booking Amount (₹)</Label>
                      <Input
                        id="booking_amount"
                        name="booking_amount"
                        type="number"
                        value={formData.booking_amount}
                        onChange={handleInputChange}
                        placeholder="e.g., 200000"
                        data-testid="booking-amount-input"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="transaction_date">Transaction Date</Label>
                      <Input
                        id="transaction_date"
                        name="transaction_date"
                        type="date"
                        value={formData.transaction_date}
                        onChange={handleInputChange}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="transaction_bank">Bank Name</Label>
                      <Input
                        id="transaction_bank"
                        name="transaction_bank"
                        value={formData.transaction_bank}
                        onChange={handleInputChange}
                        placeholder="e.g., HDFC Bank"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="transaction_details">Transaction Details</Label>
                      <Input
                        id="transaction_details"
                        name="transaction_details"
                        value={formData.transaction_details}
                        onChange={handleInputChange}
                        placeholder="Cheque No. / NEFT Ref"
                      />
                    </div>
                  </div>

                  <Separator />

                  <div className="space-y-4">
                    <h3 className="font-semibold text-slate-700">Finance Preference</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="finance_type">Payment Type</Label>
                        <Select
                          value={formData.finance_type}
                          onValueChange={(value) => setFormData(prev => ({ ...prev, finance_type: value }))}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="self">Self Payment</SelectItem>
                            <SelectItem value="loan">Bank Loan</SelectItem>
                            <SelectItem value="mixed">Mixed (Self + Loan)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      {formData.finance_type !== "self" && (
                        <div className="space-y-2">
                          <Label htmlFor="finance_bank">Preferred Bank</Label>
                          <Input
                            id="finance_bank"
                            name="finance_bank"
                            value={formData.finance_bank}
                            onChange={handleInputChange}
                            placeholder="e.g., HDFC, SBI"
                          />
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="remarks">Additional Remarks</Label>
                    <Textarea
                      id="remarks"
                      name="remarks"
                      value={formData.remarks}
                      onChange={handleInputChange}
                      rows={3}
                      placeholder="Any additional information..."
                    />
                  </div>
                </div>
              )}

              {/* Step 4: Review */}
              {step === 4 && (
                <div className="space-y-6">
                  <div className="bg-slate-50 p-4 rounded-lg space-y-4">
                    <h3 className="font-semibold text-slate-700">Applicant Details</h3>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <p className="text-slate-500">Name:</p>
                      <p className="font-medium">{formData.name}</p>
                      <p className="text-slate-500">Phone:</p>
                      <p className="font-medium">{formData.phone}</p>
                      <p className="text-slate-500">Email:</p>
                      <p className="font-medium">{formData.email}</p>
                      {formData.pan_number && (
                        <>
                          <p className="text-slate-500">PAN:</p>
                          <p className="font-medium">{formData.pan_number}</p>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="bg-slate-50 p-4 rounded-lg space-y-4">
                    <h3 className="font-semibold text-slate-700">Property Details</h3>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <p className="text-slate-500">Project:</p>
                      <p className="font-medium">{formData.project}</p>
                      <p className="text-slate-500">Tower:</p>
                      <p className="font-medium">{formData.tower}</p>
                      <p className="text-slate-500">Unit:</p>
                      <p className="font-medium">{formData.unit_number}</p>
                      <p className="text-slate-500">BHK:</p>
                      <p className="font-medium">{formData.bhk_type}</p>
                      <p className="text-slate-500">Floor:</p>
                      <p className="font-medium">{formData.floor || "Ground"}</p>
                      <p className="text-slate-500">Saleable Area:</p>
                      <p className="font-medium">{formData.saleable_area} sq.ft</p>
                      <p className="text-slate-500">Rate/Sq.ft:</p>
                      <p className="font-medium">₹{formData.rate_per_sqft}</p>
                    </div>
                  </div>

                  <div className="bg-primary/10 p-4 rounded-lg space-y-4">
                    <h3 className="font-semibold text-slate-700">Price Summary</h3>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <p className="text-slate-600">Base Price:</p>
                      <p className="font-medium text-right">{formatCurrency(priceCalc.basePrice)}</p>
                      <p className="text-slate-600">Club House & Infrastructure:</p>
                      <p className="font-medium text-right">{formatCurrency(priceCalc.clubHouse)}</p>
                      <p className="text-slate-600">Additional Parking:</p>
                      <p className="font-medium text-right">{formatCurrency(priceCalc.parkingCharges)}</p>
                      <p className="text-slate-600">Labour Cess (0.70%):</p>
                      <p className="font-medium text-right">{formatCurrency(priceCalc.labourCess)}</p>
                      <p className="text-slate-600">GST (5%):</p>
                      <p className="font-medium text-right">{formatCurrency(priceCalc.gst)}</p>
                      <Separator className="col-span-2 my-2" />
                      <p className="font-bold text-primary">Total Flat Value:</p>
                      <p className="font-bold text-primary text-right text-lg">{formatCurrency(priceCalc.total)}</p>
                    </div>
                  </div>

                  {formData.booking_amount && (
                    <div className="bg-slate-50 p-4 rounded-lg space-y-4">
                      <h3 className="font-semibold text-slate-700">Payment Details</h3>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <p className="text-slate-500">Booking Amount:</p>
                        <p className="font-medium">{formatCurrency(parseFloat(formData.booking_amount))}</p>
                        {formData.transaction_bank && (
                          <>
                            <p className="text-slate-500">Bank:</p>
                            <p className="font-medium">{formData.transaction_bank}</p>
                          </>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="bg-amber-50 border border-amber-200 p-4 rounded-lg">
                    <p className="text-sm text-amber-800">
                      By submitting this form, you confirm that all information provided is accurate.
                      Our team will verify the details and contact you for further processing.
                    </p>
                  </div>
                </div>
              )}

              {/* Navigation Buttons */}
              <div className="flex justify-between pt-6">
                {step > 1 ? (
                  <Button type="button" variant="outline" onClick={prevStep}>
                    Previous
                  </Button>
                ) : (
                  <div />
                )}
                
                {step < 4 ? (
                  <Button type="button" onClick={nextStep} data-testid="next-step-btn">
                    Next
                  </Button>
                ) : (
                  <Button type="submit" disabled={submitting} data-testid="submit-booking-btn">
                    {submitting ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Submitting...
                      </>
                    ) : (
                      "Submit Booking"
                    )}
                  </Button>
                )}
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default BookingFormPage;
