import { useState, useRef } from "react";
import axios from "axios";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Separator } from "../components/ui/separator";
import { Textarea } from "../components/ui/textarea";
import { Checkbox } from "../components/ui/checkbox";
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
  Upload,
  FileText,
  X,
  Camera,
  Mail,
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
  const [termsAccepted, setTermsAccepted] = useState(false);
  
  // File upload refs
  const panFileRef = useRef(null);
  const aadharFileRef = useRef(null);
  const passportFileRef = useRef(null);
  const coPanFileRef = useRef(null);
  const coAadharFileRef = useRef(null);
  const coPassportFileRef = useRef(null);
  
  // Camera capture refs
  const panCameraRef = useRef(null);
  const aadharCameraRef = useRef(null);
  const passportCameraRef = useRef(null);
  const coPanCameraRef = useRef(null);
  const coAadharCameraRef = useRef(null);
  const coPassportCameraRef = useRef(null);
  
  // Projects list
  const projects = [
    { name: "RRL Palm Altezze" },
    { name: "RRL NC 216" },
    { name: "RRL Palacio" },
    { name: "RRL Nature Woods" },
    { name: "RRL Towers" },
    { name: "RRL Complex" },
  ];

  // BHK Types
  const bhkTypes = ["2BHK", "2.5BHK", "3BHK", "3.5BHK", "4BHK"];
  
  // Profession options
  const professions = ["Salaried", "Self-Employed", "Business Owner", "Professional", "Government Employee", "Retired", "Other"];
  
  const [formData, setFormData] = useState({
    // Primary Applicant
    name: "",
    phone: "",
    email: "",
    father_name: "",
    date_of_birth: "",
    gender: "male",  // male, female, or spouse
    pan_number: "",
    aadhar_number: "",
    address: "",
    company: "",
    designation: "",
    profession: "",
    nationality: "Indian",
    
    // Co-Applicant (Optional)
    co_applicant_name: "",
    co_applicant_father_name: "",
    co_applicant_phone: "",
    co_applicant_email: "",
    co_applicant_pan: "",
    co_applicant_aadhar: "",
    co_applicant_address: "",
    co_applicant_profession: "",
    co_applicant_nationality: "Indian",
    
    // Property Details
    project: "",
    tower: "",  // Changed to text input
    unit_number: "",
    bhk_type: "",
    floor: "",
    saleable_area: "",
    rate_per_sqft: "6600",
    floor_rise_cost: "0",  // Manual floor rise cost input
    parking: "1",
    club_house_charges: "200000",  // Editable club house charges
    additional_charges: "0",  // Manual additional charges
    
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
  
  // File upload states
  const [uploadedFiles, setUploadedFiles] = useState({
    pan_card: null,
    aadhar_card: null,
    passport: null,
    co_pan_card: null,
    co_aadhar_card: null,
    co_passport: null,
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };
  
  // Handle file uploads
  const handleFileUpload = (fileType, file) => {
    if (file) {
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        toast.error("File size should be less than 5MB");
        return;
      }
      // Validate file type (images and PDFs)
      const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
      if (!allowedTypes.includes(file.type)) {
        toast.error("Only JPEG, PNG, and PDF files are allowed");
        return;
      }
      setUploadedFiles(prev => ({ ...prev, [fileType]: file }));
      toast.success(`${file.name} uploaded successfully`);
    }
  };
  
  const removeFile = (fileType) => {
    setUploadedFiles(prev => ({ ...prev, [fileType]: null }));
  };

  // Reusable Document Upload Component with Camera Option
  const DocumentUploadField = ({ label, fileType, fileRef, cameraRef, uploadedFile }) => {
    return (
      <div className="space-y-2">
        <Label>{label}</Label>
        <input
          type="file"
          ref={fileRef}
          className="hidden"
          accept="image/*,.pdf"
          onChange={(e) => handleFileUpload(fileType, e.target.files[0])}
        />
        <input
          type="file"
          ref={cameraRef}
          className="hidden"
          accept="image/*"
          capture="environment"
          onChange={(e) => handleFileUpload(fileType, e.target.files[0])}
        />
        {uploadedFile ? (
          <div className="flex items-center gap-2 p-2 bg-green-50 border border-green-200 rounded">
            <FileText className="w-4 h-4 text-green-600" />
            <span className="text-sm truncate flex-1">{uploadedFile.name}</span>
            <Button type="button" variant="ghost" size="sm" onClick={() => removeFile(fileType)}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        ) : (
          <div className="flex gap-2">
            <Button 
              type="button" 
              variant="outline" 
              className="flex-1" 
              onClick={() => fileRef.current?.click()}
              data-testid={`${fileType}-upload-btn`}
            >
              <Upload className="w-4 h-4 mr-1" /> Upload
            </Button>
            <Button 
              type="button" 
              variant="outline" 
              className="flex-1 bg-blue-50 border-blue-200 hover:bg-blue-100 text-blue-700" 
              onClick={() => cameraRef.current?.click()}
              data-testid={`${fileType}-camera-btn`}
            >
              <Camera className="w-4 h-4 mr-1" /> Camera
            </Button>
          </div>
        )}
      </div>
    );
  };

  // Calculate price based on inputs - Updated with manual floor rise and additional charges
  const calculatePrice = () => {
    const saleableArea = parseFloat(formData.saleable_area) || 0;
    const ratePerSqft = parseFloat(formData.rate_per_sqft) || 0;
    const floorRiseCost = parseFloat(formData.floor_rise_cost) || 0;  // Manual input
    const clubHouseCharges = parseFloat(formData.club_house_charges) || 200000;  // Editable
    const additionalCharges = parseFloat(formData.additional_charges) || 0;  // Manual input
    
    // Base price = Total Saleable Area × Rate/sqft
    const basePrice = saleableArea * ratePerSqft;
    
    // Floor Rise is now a manual cost input (added to base price)
    const floorRiseTotal = saleableArea * floorRiseCost;
    
    const subtotal = basePrice + floorRiseTotal + clubHouseCharges + additionalCharges;
    const labourCess = subtotal * 0.007; // 0.70%
    const gst = subtotal * 0.05; // 5%
    const total = subtotal + labourCess + gst;
    
    return {
      basePrice,
      floorRiseCost,
      floorRiseTotal,
      effectiveRate: ratePerSqft + floorRiseCost,
      clubHouse: clubHouseCharges,
      additionalCharges,
      subtotal,
      labourCess,
      gst,
      total
    };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!termsAccepted) {
      toast.error("Please accept the Terms and Conditions to proceed");
      return;
    }
    
    setSubmitting(true);

    try {
      const priceCalc = calculatePrice();
      
      const payload = {
        ...formData,
        floor: parseInt(formData.floor) || 0,
        saleable_area: parseFloat(formData.saleable_area) || 0,
        rate_per_sqft: parseFloat(formData.rate_per_sqft) || 0,
        floor_rise_cost: parseFloat(formData.floor_rise_cost) || 0,
        club_house_charges: parseFloat(formData.club_house_charges) || 200000,
        additional_charges: parseFloat(formData.additional_charges) || 0,
        booking_amount: parseFloat(formData.booking_amount) || 0,
        total_price: priceCalc.total,
        base_price: priceCalc.basePrice,
        floor_rise_total: priceCalc.floorRiseTotal,
        labour_cess: priceCalc.labourCess,
        gst_amount: priceCalc.gst,
      };

      const response = await axios.post(`${API}/public/booking-form`, payload);
      const customerId = response.data.reference_id;
      
      // Upload documents if any
      const uploadPromises = [];
      if (uploadedFiles.pan_card) {
        const formDataPan = new FormData();
        formDataPan.append('file', uploadedFiles.pan_card);
        formDataPan.append('doc_type', 'pan_card');
        uploadPromises.push(axios.post(`${API}/public/upload-document/${customerId}`, formDataPan));
      }
      if (uploadedFiles.aadhar_card) {
        const formDataAadhar = new FormData();
        formDataAadhar.append('file', uploadedFiles.aadhar_card);
        formDataAadhar.append('doc_type', 'aadhar_card');
        uploadPromises.push(axios.post(`${API}/public/upload-document/${customerId}`, formDataAadhar));
      }
      if (uploadedFiles.passport) {
        const formDataPassport = new FormData();
        formDataPassport.append('file', uploadedFiles.passport);
        formDataPassport.append('doc_type', 'passport');
        uploadPromises.push(axios.post(`${API}/public/upload-document/${customerId}`, formDataPassport));
      }
      if (uploadedFiles.co_pan_card) {
        const formDataCoPan = new FormData();
        formDataCoPan.append('file', uploadedFiles.co_pan_card);
        formDataCoPan.append('doc_type', 'co_pan_card');
        uploadPromises.push(axios.post(`${API}/public/upload-document/${customerId}`, formDataCoPan));
      }
      if (uploadedFiles.co_aadhar_card) {
        const formDataCoAadhar = new FormData();
        formDataCoAadhar.append('file', uploadedFiles.co_aadhar_card);
        formDataCoAadhar.append('doc_type', 'co_aadhar_card');
        uploadPromises.push(axios.post(`${API}/public/upload-document/${customerId}`, formDataCoAadhar));
      }
      if (uploadedFiles.co_passport) {
        const formDataCoPassport = new FormData();
        formDataCoPassport.append('file', uploadedFiles.co_passport);
        formDataCoPassport.append('doc_type', 'co_passport');
        uploadPromises.push(axios.post(`${API}/public/upload-document/${customerId}`, formDataCoPassport));
      }
      
      // Execute uploads (don't fail the whole submission if uploads fail)
      try {
        await Promise.all(uploadPromises);
      } catch (uploadError) {
        console.error("Document upload failed:", uploadError);
      }
      
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
      case 4:
        return termsAccepted; // Must accept terms
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
            
            {/* Email Confirmation */}
            <div className="bg-green-50 border border-green-200 p-4 rounded-lg mb-4">
              <div className="flex items-center justify-center gap-2 text-green-700">
                <Mail className="w-5 h-5" />
                <span className="font-medium">Welcome Email Sent!</span>
              </div>
              <p className="text-sm text-green-600 mt-2">
                A confirmation email with your <strong>Price Breakup</strong> and <strong>Terms & Conditions</strong> has been sent to:
              </p>
              <p className="text-sm font-medium text-green-800 mt-1">{formData.email}</p>
            </div>
            
            <p className="text-xs text-slate-400">
              Please check your inbox (and spam folder) for the booking confirmation.
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
                        <Label htmlFor="gender">Gender</Label>
                        <Select
                          value={formData.gender}
                          onValueChange={(value) => setFormData(prev => ({ ...prev, gender: value }))}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="male">Male (S/o)</SelectItem>
                            <SelectItem value="female">Female (D/o)</SelectItem>
                            <SelectItem value="spouse">Spouse (W/o)</SelectItem>
                          </SelectContent>
                        </Select>
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
                      <div className="space-y-2">
                        <Label htmlFor="profession">Profession</Label>
                        <Select
                          value={formData.profession}
                          onValueChange={(value) => setFormData(prev => ({ ...prev, profession: value }))}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select profession" />
                          </SelectTrigger>
                          <SelectContent>
                            {professions.map((prof) => (
                              <SelectItem key={prof} value={prof}>
                                {prof}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
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
                    
                    {/* Document Uploads for Primary Applicant */}
                    <div className="mt-4 p-4 bg-slate-50 rounded-lg">
                      <h4 className="font-medium text-slate-700 mb-3 flex items-center gap-2">
                        <FileText className="w-4 h-4" />
                        Upload Documents
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <DocumentUploadField
                          label="PAN Card"
                          fileType="pan_card"
                          fileRef={panFileRef}
                          cameraRef={panCameraRef}
                          uploadedFile={uploadedFiles.pan_card}
                        />
                        <DocumentUploadField
                          label="Aadhaar Card"
                          fileType="aadhar_card"
                          fileRef={aadharFileRef}
                          cameraRef={aadharCameraRef}
                          uploadedFile={uploadedFiles.aadhar_card}
                        />
                        {(formData.nationality === "NRI" || formData.nationality === "OCI") && (
                          <DocumentUploadField
                            label="Passport"
                            fileType="passport"
                            fileRef={passportFileRef}
                            cameraRef={passportCameraRef}
                            uploadedFile={uploadedFiles.passport}
                          />
                        )}
                      </div>
                      <p className="text-xs text-slate-500 mt-2">
                        Accepted formats: JPEG, PNG, PDF. Max size: 5MB. Use Camera to capture directly from your device.
                      </p>
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
                        <Label htmlFor="co_applicant_father_name">Father/Spouse Name</Label>
                        <Input
                          id="co_applicant_father_name"
                          name="co_applicant_father_name"
                          value={formData.co_applicant_father_name}
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
                      <div className="space-y-2">
                        <Label htmlFor="co_applicant_aadhar">Aadhaar Number</Label>
                        <Input
                          id="co_applicant_aadhar"
                          name="co_applicant_aadhar"
                          value={formData.co_applicant_aadhar}
                          onChange={handleInputChange}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="co_applicant_profession">Profession</Label>
                        <Select
                          value={formData.co_applicant_profession}
                          onValueChange={(value) => setFormData(prev => ({ ...prev, co_applicant_profession: value }))}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select profession" />
                          </SelectTrigger>
                          <SelectContent>
                            {professions.map((prof) => (
                              <SelectItem key={prof} value={prof}>
                                {prof}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="co_applicant_nationality">Nationality</Label>
                        <Select
                          value={formData.co_applicant_nationality}
                          onValueChange={(value) => setFormData(prev => ({ ...prev, co_applicant_nationality: value }))}
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
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="co_applicant_address">Address</Label>
                      <Textarea
                        id="co_applicant_address"
                        name="co_applicant_address"
                        value={formData.co_applicant_address}
                        onChange={handleInputChange}
                        rows={2}
                      />
                    </div>
                    
                    {/* Document Uploads for Co-Applicant */}
                    {formData.co_applicant_name && (
                      <div className="mt-4 p-4 bg-slate-50 rounded-lg">
                        <h4 className="font-medium text-slate-700 mb-3 flex items-center gap-2">
                          <FileText className="w-4 h-4" />
                          Co-Applicant Documents
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <DocumentUploadField
                            label="PAN Card"
                            fileType="co_pan_card"
                            fileRef={coPanFileRef}
                            cameraRef={coPanCameraRef}
                            uploadedFile={uploadedFiles.co_pan_card}
                          />
                          <DocumentUploadField
                            label="Aadhaar Card"
                            fileType="co_aadhar_card"
                            fileRef={coAadharFileRef}
                            cameraRef={coAadharCameraRef}
                            uploadedFile={uploadedFiles.co_aadhar_card}
                          />
                          {(formData.co_applicant_nationality === "NRI" || formData.co_applicant_nationality === "OCI") && (
                            <DocumentUploadField
                              label="Passport"
                              fileType="co_passport"
                              fileRef={coPassportFileRef}
                              cameraRef={coPassportCameraRef}
                              uploadedFile={uploadedFiles.co_passport}
                            />
                          )}
                        </div>
                        <p className="text-xs text-slate-500 mt-2">
                          Accepted formats: JPEG, PNG, PDF. Max size: 5MB. Use Camera to capture directly from your device.
                        </p>
                      </div>
                    )}
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
                        onValueChange={(value) => setFormData(prev => ({ ...prev, project: value }))}
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
                      <Input
                        id="tower"
                        name="tower"
                        value={formData.tower}
                        onChange={handleInputChange}
                        placeholder="e.g., Tower-1, Block-A"
                        required
                        data-testid="tower-input"
                      />
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
                      <Label htmlFor="floor">Floor Number</Label>
                      <Input
                        id="floor"
                        name="floor"
                        type="number"
                        value={formData.floor}
                        onChange={handleInputChange}
                        placeholder="e.g., 7"
                        data-testid="floor-input"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="saleable_area">Total Saleable Area (sq.ft) *</Label>
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
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="floor_rise_cost">Floor Rise (₹ per sq.ft)</Label>
                      <Input
                        id="floor_rise_cost"
                        name="floor_rise_cost"
                        type="number"
                        value={formData.floor_rise_cost}
                        onChange={handleInputChange}
                        placeholder="e.g., 50"
                        data-testid="floor-rise-input"
                      />
                      <p className="text-xs text-slate-500">Additional cost per sq.ft based on floor (enter 0 if not applicable)</p>
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
                      <Label htmlFor="club_house_charges">Club House Charges (₹)</Label>
                      <Input
                        id="club_house_charges"
                        name="club_house_charges"
                        type="number"
                        min="0"
                        value={formData.club_house_charges}
                        onChange={handleInputChange}
                        placeholder="200000"
                      />
                    </div>
                    <div className="space-y-2 col-span-2">
                      <Label htmlFor="additional_charges">Additional Charges (₹) - Manual Entry</Label>
                      <Input
                        id="additional_charges"
                        name="additional_charges"
                        type="number"
                        min="0"
                        value={formData.additional_charges}
                        onChange={handleInputChange}
                        placeholder="Enter any additional charges"
                      />
                      <p className="text-xs text-slate-500">Enter any extra charges like parking, amenities, etc.</p>
                    </div>
                  </div>

                  {/* Live Price Calculator */}
                  {formData.saleable_area && formData.rate_per_sqft && (
                    <div className="mt-6 p-4 bg-primary/5 border border-primary/20 rounded-lg">
                      <h3 className="font-semibold text-slate-700 mb-3">Price Calculation Preview</h3>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <span className="text-slate-600">Base Price ({formData.saleable_area} sq.ft × ₹{formData.rate_per_sqft}):</span>
                        <span className="font-medium text-right">{formatCurrency(priceCalc.basePrice)}</span>
                        
                        {priceCalc.floorRiseTotal > 0 && (
                          <>
                            <span className="text-slate-600">Floor Rise ({formData.saleable_area} sq.ft × ₹{formData.floor_rise_cost}):</span>
                            <span className="font-medium text-right">+{formatCurrency(priceCalc.floorRiseTotal)}</span>
                          </>
                        )}
                        
                        <span className="text-slate-600">Club House & Infrastructure:</span>
                        <span className="font-medium text-right">{formatCurrency(priceCalc.clubHouse)}</span>
                        
                        {priceCalc.additionalCharges > 0 && (
                          <>
                            <span className="text-slate-600">Additional Charges:</span>
                            <span className="font-medium text-right">{formatCurrency(priceCalc.additionalCharges)}</span>
                          </>
                        )}
                        
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
                      {formData.profession && (
                        <>
                          <p className="text-slate-500">Profession:</p>
                          <p className="font-medium">{formData.profession}</p>
                        </>
                      )}
                    </div>
                  </div>
                  
                  {formData.co_applicant_name && (
                    <div className="bg-slate-50 p-4 rounded-lg space-y-4">
                      <h3 className="font-semibold text-slate-700">Co-Applicant Details</h3>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <p className="text-slate-500">Name:</p>
                        <p className="font-medium">{formData.co_applicant_name}</p>
                        {formData.co_applicant_phone && (
                          <>
                            <p className="text-slate-500">Phone:</p>
                            <p className="font-medium">{formData.co_applicant_phone}</p>
                          </>
                        )}
                        {formData.co_applicant_email && (
                          <>
                            <p className="text-slate-500">Email:</p>
                            <p className="font-medium">{formData.co_applicant_email}</p>
                          </>
                        )}
                      </div>
                    </div>
                  )}

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
                      <p className="text-slate-500">Total Saleable Area:</p>
                      <p className="font-medium">{formData.saleable_area} sq.ft</p>
                      <p className="text-slate-500">Rate/Sq.ft:</p>
                      <p className="font-medium">₹{formData.rate_per_sqft}</p>
                      {parseFloat(formData.floor_rise_cost) > 0 && (
                        <>
                          <p className="text-slate-500">Floor Rise/Sq.ft:</p>
                          <p className="font-medium">₹{formData.floor_rise_cost}</p>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="bg-primary/10 p-4 rounded-lg space-y-4">
                    <h3 className="font-semibold text-slate-700">Price Summary</h3>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <p className="text-slate-600">Base Price ({formData.saleable_area} × ₹{formData.rate_per_sqft}):</p>
                      <p className="font-medium text-right">{formatCurrency(priceCalc.basePrice)}</p>
                      {priceCalc.floorRiseTotal > 0 && (
                        <>
                          <p className="text-slate-600">Floor Rise:</p>
                          <p className="font-medium text-right">{formatCurrency(priceCalc.floorRiseTotal)}</p>
                        </>
                      )}
                      <p className="text-slate-600">Club House & Infrastructure:</p>
                      <p className="font-medium text-right">{formatCurrency(priceCalc.clubHouse)}</p>
                      {priceCalc.additionalCharges > 0 && (
                        <>
                          <p className="text-slate-600">Additional Charges:</p>
                          <p className="font-medium text-right">{formatCurrency(priceCalc.additionalCharges)}</p>
                        </>
                      )}
                      <p className="text-slate-600">Labour Cess (0.70%):</p>
                      <p className="font-medium text-right">{formatCurrency(priceCalc.labourCess)}</p>
                      <p className="text-slate-600">GST (5%):</p>
                      <p className="font-medium text-right">{formatCurrency(priceCalc.gst)}</p>
                      <Separator className="col-span-2 my-2" />
                      <p className="font-bold text-primary">Total Flat Value:</p>
                      <p className="font-bold text-primary text-right text-lg">{formatCurrency(priceCalc.total)}</p>
                    </div>
                  </div>
                  
                  {/* Uploaded Documents Summary */}
                  {Object.values(uploadedFiles).some(f => f !== null) && (
                    <div className="bg-slate-50 p-4 rounded-lg space-y-4">
                      <h3 className="font-semibold text-slate-700">Uploaded Documents</h3>
                      <div className="flex flex-wrap gap-2">
                        {uploadedFiles.pan_card && (
                          <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-sm">PAN Card</span>
                        )}
                        {uploadedFiles.aadhar_card && (
                          <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-sm">Aadhaar</span>
                        )}
                        {uploadedFiles.passport && (
                          <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-sm">Passport</span>
                        )}
                        {uploadedFiles.co_pan_card && (
                          <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-sm">Co-Applicant PAN</span>
                        )}
                        {uploadedFiles.co_aadhar_card && (
                          <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-sm">Co-Applicant Aadhaar</span>
                        )}
                        {uploadedFiles.co_passport && (
                          <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-sm">Co-Applicant Passport</span>
                        )}
                      </div>
                    </div>
                  )}

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

                  {/* Terms and Conditions */}
                  <div className="border border-slate-300 rounded-lg p-4 max-h-48 overflow-y-auto bg-white">
                    <h3 className="font-semibold text-slate-700 mb-3">Terms and Conditions</h3>
                    <div className="text-sm text-slate-600 space-y-2">
                      <p>1. This booking is subject to verification by RRL Builders and Developers Pvt. Ltd.</p>
                      <p>2. All payments must be made via A/c Payee Cheque/Banker Cheque/Pay order/Demand Draft or through Electronic Fund Transfer (EFT) to "RRL BUILDERS AND DEVELOPERS PVT LTD".</p>
                      <p>3. The buyer is responsible for paying applicable stamp duty, registration charges, and other statutory levies.</p>
                      <p>4. Any delay or default in payment will attract penal interest as per the Rules on the Outstanding amount.</p>
                      <p>5. This booking is neither transferable nor assignable without prior written consent from the Developer.</p>
                      <p>6. The buyer agrees to comply with provisions of section 194IA of the Income Tax Act, 1961 (TDS deduction).</p>
                      <p>7. In case of cancellation, the developer reserves the right to forfeit the booking amount plus 5% of the Total Sale Consideration.</p>
                      <p>8. The buyer acknowledges that they have reviewed and are satisfied with the title documents of the property.</p>
                      <p>9. Maintenance charges as per prevailing rates will be applicable from the date of possession.</p>
                      <p>10. All disputes shall be referred exclusively to the jurisdictional Real Estate Regulatory Authority (RERA).</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3 p-4 bg-amber-50 border border-amber-200 rounded-lg">
                    <Checkbox
                      id="terms"
                      checked={termsAccepted}
                      onCheckedChange={(checked) => setTermsAccepted(checked)}
                      data-testid="terms-checkbox"
                    />
                    <label htmlFor="terms" className="text-sm text-amber-800 cursor-pointer">
                      I have read, understood, and agree to the above Terms and Conditions. I confirm that all information provided is accurate and complete. I understand that submitting this form does not guarantee the allotment of the property.
                    </label>
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
