import { Separator } from "../ui/separator";
import { Checkbox } from "../ui/checkbox";
import { formatCurrency } from "./constants";

const ReviewStep = ({ formData, priceCalc, uploadedFiles, termsAccepted, setTermsAccepted }) => {
  return (
    <div className="space-y-6">
      <div className="bg-slate-50 p-4 rounded-lg space-y-4">
        <h3 className="font-semibold text-slate-700">Applicant Details</h3>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <p className="text-slate-500">Name:</p><p className="font-medium">{formData.name}</p>
          <p className="text-slate-500">Phone:</p><p className="font-medium">{formData.phone}</p>
          <p className="text-slate-500">Email:</p><p className="font-medium">{formData.email}</p>
          {formData.pan_number && (<><p className="text-slate-500">PAN:</p><p className="font-medium">{formData.pan_number}</p></>)}
          {formData.profession && (<><p className="text-slate-500">Profession:</p><p className="font-medium">{formData.profession}</p></>)}
        </div>
      </div>

      {formData.co_applicant_name && (
        <div className="bg-slate-50 p-4 rounded-lg space-y-4">
          <h3 className="font-semibold text-slate-700">Co-Applicant Details</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <p className="text-slate-500">Name:</p><p className="font-medium">{formData.co_applicant_name}</p>
            {formData.co_applicant_phone && (<><p className="text-slate-500">Phone:</p><p className="font-medium">{formData.co_applicant_phone}</p></>)}
            {formData.co_applicant_email && (<><p className="text-slate-500">Email:</p><p className="font-medium">{formData.co_applicant_email}</p></>)}
          </div>
        </div>
      )}

      <div className="bg-slate-50 p-4 rounded-lg space-y-4">
        <h3 className="font-semibold text-slate-700">Property Details</h3>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <p className="text-slate-500">Project:</p><p className="font-medium">{formData.project}</p>
          <p className="text-slate-500">Tower:</p><p className="font-medium">{formData.tower}</p>
          <p className="text-slate-500">Unit:</p><p className="font-medium">{formData.unit_number}</p>
          <p className="text-slate-500">BHK:</p><p className="font-medium">{formData.bhk_type}</p>
          <p className="text-slate-500">Floor:</p><p className="font-medium">{formData.floor || "Ground"}</p>
          <p className="text-slate-500">Total Saleable Area:</p><p className="font-medium">{formData.saleable_area} sq.ft</p>
          <p className="text-slate-500">Rate/Sq.ft:</p><p className="font-medium">&#8377;{formData.rate_per_sqft}</p>
          {parseFloat(formData.floor_rise_cost) > 0 && (
            <><p className="text-slate-500">Floor Rise/Sq.ft:</p><p className="font-medium">&#8377;{formData.floor_rise_cost}</p></>
          )}
        </div>
      </div>

      <div className="bg-primary/10 p-4 rounded-lg space-y-4">
        <h3 className="font-semibold text-slate-700">Price Summary</h3>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <p className="text-slate-600">Base Price ({formData.saleable_area} x &#8377;{formData.rate_per_sqft}):</p>
          <p className="font-medium text-right">{formatCurrency(priceCalc.basePrice)}</p>
          {priceCalc.floorRiseTotal > 0 && (
            <><p className="text-slate-600">Floor Rise:</p><p className="font-medium text-right">{formatCurrency(priceCalc.floorRiseTotal)}</p></>
          )}
          <p className="text-slate-600">Club House & Infrastructure:</p>
          <p className="font-medium text-right">{formatCurrency(priceCalc.clubHouse)}</p>
          {priceCalc.additionalCharges > 0 && (
            <><p className="text-slate-600">Additional Charges:</p><p className="font-medium text-right">{formatCurrency(priceCalc.additionalCharges)}</p></>
          )}
          {priceCalc.bescomAmount > 0 && (
            <><p className="text-slate-600">BESCOM Charges (&#8377;{priceCalc.bescomRate}/sq.ft):</p><p className="font-medium text-right">{formatCurrency(priceCalc.bescomAmount)}</p></>
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
            {uploadedFiles.pan_card && <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-sm">PAN Card</span>}
            {uploadedFiles.aadhar_card && <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-sm">Aadhaar</span>}
            {uploadedFiles.passport && <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-sm">Passport</span>}
            {uploadedFiles.co_pan_card && <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-sm">Co-Applicant PAN</span>}
            {uploadedFiles.co_aadhar_card && <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-sm">Co-Applicant Aadhaar</span>}
            {uploadedFiles.co_passport && <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-sm">Co-Applicant Passport</span>}
          </div>
        </div>
      )}

      {formData.booking_amount && (
        <div className="bg-slate-50 p-4 rounded-lg space-y-4">
          <h3 className="font-semibold text-slate-700">Payment Details</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <p className="text-slate-500">Booking Amount:</p>
            <p className="font-medium">{formatCurrency(parseFloat(formData.booking_amount))}</p>
            {formData.transaction_bank && (<><p className="text-slate-500">Bank:</p><p className="font-medium">{formData.transaction_bank}</p></>)}
          </div>
        </div>
      )}

      {/* Terms and Conditions */}
      <div className="border border-slate-300 rounded-lg p-4 max-h-48 overflow-y-auto bg-white">
        <h3 className="font-semibold text-slate-700 mb-3">Terms and Conditions</h3>
        <div className="text-sm text-slate-600 space-y-2">
          <p>1. This booking is subject to verification by RRL Builders and Developers Pvt. Ltd.</p>
          <p>2. All payments must be made via A/c Payee Cheque/Banker Cheque/Pay order/Demand Draft or through Electronic Fund Transfer (EFT) to &quot;RRL BUILDERS AND DEVELOPERS PVT LTD&quot;.</p>
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
        <Checkbox id="terms" checked={termsAccepted} onCheckedChange={(checked) => setTermsAccepted(checked)} data-testid="terms-checkbox" />
        <label htmlFor="terms" className="text-sm text-amber-800 cursor-pointer">
          I have read, understood, and agree to the above Terms and Conditions. I confirm that all information provided is accurate and complete. I understand that submitting this form does not guarantee the allotment of the property.
        </label>
      </div>
    </div>
  );
};

export default ReviewStep;
