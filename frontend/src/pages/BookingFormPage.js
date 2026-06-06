import { useState, useRef } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { User, Building2, CreditCard, Eye, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { initialFormData, initialUploadedFiles, calculatePrice } from "../components/booking/constants";
import BookingSuccess from "../components/booking/BookingSuccess";
import ApplicantDetailsStep from "../components/booking/ApplicantDetailsStep";
import PropertyDetailsStep from "../components/booking/PropertyDetailsStep";
import PaymentStep from "../components/booking/PaymentStep";
import ReviewStep from "../components/booking/ReviewStep";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

const BookingFormPage = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState(initialFormData);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submissionResult, setSubmissionResult] = useState(null);
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState(initialUploadedFiles);

  // File refs
  const panFileRef = useRef(null);
  const panCameraRef = useRef(null);
  const aadharFileRef = useRef(null);
  const aadharCameraRef = useRef(null);
  const passportFileRef = useRef(null);
  const passportCameraRef = useRef(null);
  const coPanFileRef = useRef(null);
  const coPanCameraRef = useRef(null);
  const coAadharFileRef = useRef(null);
  const coAadharCameraRef = useRef(null);
  const coPassportFileRef = useRef(null);
  const coPassportCameraRef = useRef(null);

  const fileRefs = { pan: panFileRef, aadhar: aadharFileRef, passport: passportFileRef, coPan: coPanFileRef, coAadhar: coAadharFileRef, coPassport: coPassportFileRef };
  const cameraRefs = { pan: panCameraRef, aadhar: aadharCameraRef, passport: passportCameraRef, coPan: coPanCameraRef, coAadhar: coAadharCameraRef, coPassport: coPassportCameraRef };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleFileUpload = (fileType, file) => {
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) { toast.error("File size should be less than 5MB"); return; }
    const allowed = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
    if (!allowed.includes(file.type)) { toast.error("Only JPEG, PNG, and PDF files are allowed"); return; }
    setUploadedFiles(prev => ({ ...prev, [fileType]: file }));
    toast.success(`${file.name} uploaded successfully`);
  };

  const removeFile = (fileType) => {
    setUploadedFiles(prev => ({ ...prev, [fileType]: null }));
  };

  const priceCalc = calculatePrice(formData);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!termsAccepted) { toast.error("Please accept the Terms and Conditions to proceed"); return; }
    setSubmitting(true);
    try {
      const payload = {
        ...formData,
        floor: parseInt(formData.floor) || 0,
        saleable_area: parseFloat(formData.saleable_area) || 0,
        rate_per_sqft: parseFloat(formData.rate_per_sqft) || 0,
        floor_rise_cost: parseFloat(formData.floor_rise_cost) || 0,
        club_house_charges: parseFloat(formData.club_house_charges) || 200000,
        additional_charges: parseFloat(formData.additional_charges) || 0,
        bescom_rate: parseFloat(formData.bescom_rate) || 0,
        booking_amount: parseFloat(formData.booking_amount) || 0,
        total_price: priceCalc.total,
        base_price: priceCalc.basePrice,
        floor_rise_total: priceCalc.floorRiseTotal,
        labour_cess: priceCalc.labourCess,
        gst_amount: priceCalc.gst,
      };

      const response = await axios.post(`${API}/public/booking-form`, payload);
      const customerId = response.data.reference_id;

      // Upload documents
      const uploads = [];
      const fileMap = {
        pan_card: 'pan_card', aadhar_card: 'aadhar_card', passport: 'passport',
        co_pan_card: 'co_pan_card', co_aadhar_card: 'co_aadhar_card', co_passport: 'co_passport',
      };
      for (const [key, docType] of Object.entries(fileMap)) {
        if (uploadedFiles[key]) {
          const fd = new FormData();
          fd.append('file', uploadedFiles[key]);
          fd.append('doc_type', docType);
          uploads.push(axios.post(`${API}/public/upload-document/${customerId}`, fd));
        }
      }
      try { await Promise.all(uploads); } catch (uploadErr) { console.warn("Some document uploads failed:", uploadErr.message); }

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
    if (stepNum === 1) return formData.name && formData.phone && formData.email;
    if (stepNum === 2) return formData.project && formData.tower && formData.unit_number && formData.bhk_type && formData.saleable_area && formData.rate_per_sqft;
    if (stepNum === 3) return true;
    if (stepNum === 4) return termsAccepted;
    return true;
  };

  const nextStep = () => {
    if (validateStep(step)) setStep(step + 1);
    else toast.error("Please fill all required fields");
  };

  if (submitted) {
    return <BookingSuccess submissionResult={submissionResult} email={formData.email} />;
  }

  const stepIcons = [
    <><User className="w-5 h-5" /> Applicant Details</>,
    <><Building2 className="w-5 h-5" /> Property Details</>,
    <><CreditCard className="w-5 h-5" /> Payment Information</>,
    <><Eye className="w-5 h-5" /> Review & Submit</>,
  ];
  const stepDescs = [
    "Enter primary and co-applicant details",
    "Enter property details and pricing",
    "Enter booking payment details",
    "Review your information before submitting",
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 to-pink-100 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">RRL Builders</h1>
          <p className="text-slate-600">Property Booking Form</p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-8">
          {[1, 2, 3, 4].map((s) => (
            <div key={s} className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${s <= step ? "bg-primary text-white" : "bg-slate-200 text-slate-500"}`}>
                {s}
              </div>
              {s < 4 && <div className={`w-16 h-1 ${s < step ? "bg-primary" : "bg-slate-200"}`} />}
            </div>
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">{stepIcons[step - 1]}</CardTitle>
            <CardDescription>{stepDescs[step - 1]}</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit}>
              {step === 1 && (
                <ApplicantDetailsStep
                  formData={formData}
                  onInputChange={handleInputChange}
                  onSelectChange={handleSelectChange}
                  uploadedFiles={uploadedFiles}
                  onFileUpload={handleFileUpload}
                  onRemoveFile={removeFile}
                  fileRefs={fileRefs}
                  cameraRefs={cameraRefs}
                />
              )}
              {step === 2 && (
                <PropertyDetailsStep
                  formData={formData}
                  onInputChange={handleInputChange}
                  onSelectChange={handleSelectChange}
                  priceCalc={priceCalc}
                />
              )}
              {step === 3 && (
                <PaymentStep
                  formData={formData}
                  onInputChange={handleInputChange}
                  onSelectChange={handleSelectChange}
                />
              )}
              {step === 4 && (
                <ReviewStep
                  formData={formData}
                  priceCalc={priceCalc}
                  uploadedFiles={uploadedFiles}
                  termsAccepted={termsAccepted}
                  setTermsAccepted={setTermsAccepted}
                />
              )}

              {/* Navigation */}
              <div className="flex justify-between pt-6">
                {step > 1 ? (
                  <Button type="button" variant="outline" onClick={() => setStep(step - 1)}>Previous</Button>
                ) : <div />}
                {step < 4 ? (
                  <Button type="button" onClick={nextStep} data-testid="next-step-btn">Next</Button>
                ) : (
                  <Button type="submit" disabled={submitting} data-testid="submit-booking-btn">
                    {submitting ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Submitting...</> : "Submit Booking"}
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
