import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import { Separator } from "../ui/separator";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "../ui/select";
import { FileText } from "lucide-react";
import DocumentUploadField from "./DocumentUploadField";
import { professions } from "./constants";

const ApplicantDetailsStep = ({
  formData, onInputChange, onSelectChange,
  uploadedFiles, onFileUpload, onRemoveFile,
  fileRefs, cameraRefs,
}) => {
  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <h3 className="font-semibold text-slate-700">Primary Applicant</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="name">Full Name *</Label>
            <Input id="name" name="name" value={formData.name} onChange={onInputChange} required data-testid="applicant-name-input" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="phone">Phone Number *</Label>
            <Input id="phone" name="phone" value={formData.phone} onChange={onInputChange} required data-testid="applicant-phone-input" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email *</Label>
            <Input id="email" name="email" type="email" value={formData.email} onChange={onInputChange} required data-testid="applicant-email-input" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="father_name">Father/Spouse Name</Label>
            <Input id="father_name" name="father_name" value={formData.father_name} onChange={onInputChange} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="date_of_birth">Date of Birth</Label>
            <Input id="date_of_birth" name="date_of_birth" type="date" value={formData.date_of_birth} onChange={onInputChange} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="gender">Gender</Label>
            <Select value={formData.gender} onValueChange={(v) => onSelectChange("gender", v)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="male">Male (S/o)</SelectItem>
                <SelectItem value="female">Female (D/o)</SelectItem>
                <SelectItem value="spouse">Spouse (W/o)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="nationality">Nationality</Label>
            <Select value={formData.nationality} onValueChange={(v) => onSelectChange("nationality", v)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="Indian">Indian</SelectItem>
                <SelectItem value="NRI">NRI</SelectItem>
                <SelectItem value="OCI">OCI</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="pan_number">PAN Number</Label>
            <Input id="pan_number" name="pan_number" value={formData.pan_number} onChange={onInputChange} placeholder="ABCDE1234F" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="aadhar_number">Aadhaar Number</Label>
            <Input id="aadhar_number" name="aadhar_number" value={formData.aadhar_number} onChange={onInputChange} placeholder="1234 5678 9012" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="profession">Profession</Label>
            <Select value={formData.profession} onValueChange={(v) => onSelectChange("profession", v)}>
              <SelectTrigger><SelectValue placeholder="Select profession" /></SelectTrigger>
              <SelectContent>
                {professions.map((prof) => (
                  <SelectItem key={prof} value={prof}>{prof}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="address">Address</Label>
          <Textarea id="address" name="address" value={formData.address} onChange={onInputChange} rows={2} />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="company">Company</Label>
            <Input id="company" name="company" value={formData.company} onChange={onInputChange} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="designation">Designation</Label>
            <Input id="designation" name="designation" value={formData.designation} onChange={onInputChange} />
          </div>
        </div>

        {/* Document Uploads */}
        <div className="mt-4 p-4 bg-slate-50 rounded-lg">
          <h4 className="font-medium text-slate-700 mb-3 flex items-center gap-2">
            <FileText className="w-4 h-4" /> Upload Documents
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <DocumentUploadField label="PAN Card" fileType="pan_card" fileRef={fileRefs.pan} cameraRef={cameraRefs.pan} uploadedFile={uploadedFiles.pan_card} onUpload={onFileUpload} onRemove={onRemoveFile} />
            <DocumentUploadField label="Aadhaar Card" fileType="aadhar_card" fileRef={fileRefs.aadhar} cameraRef={cameraRefs.aadhar} uploadedFile={uploadedFiles.aadhar_card} onUpload={onFileUpload} onRemove={onRemoveFile} />
            {(formData.nationality === "NRI" || formData.nationality === "OCI") && (
              <DocumentUploadField label="Passport" fileType="passport" fileRef={fileRefs.passport} cameraRef={cameraRefs.passport} uploadedFile={uploadedFiles.passport} onUpload={onFileUpload} onRemove={onRemoveFile} />
            )}
          </div>
          <p className="text-xs text-slate-500 mt-2">Accepted formats: JPEG, PNG, PDF. Max size: 5MB.</p>
        </div>
      </div>

      <Separator />

      {/* Co-Applicant */}
      <div className="space-y-4">
        <h3 className="font-semibold text-slate-700">Co-Applicant (Optional)</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="co_applicant_name">Full Name</Label>
            <Input id="co_applicant_name" name="co_applicant_name" value={formData.co_applicant_name} onChange={onInputChange} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="co_applicant_father_name">
              {formData.co_applicant_gender === "female" ? "Father/Spouse Name (D/o)"
                : formData.co_applicant_gender === "spouse" ? "Spouse Name (W/o)"
                : "Father/Spouse Name (S/o)"}
            </Label>
            <Input id="co_applicant_father_name" name="co_applicant_father_name" value={formData.co_applicant_father_name} onChange={onInputChange} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="co_applicant_gender">Gender</Label>
            <Select value={formData.co_applicant_gender} onValueChange={(v) => onSelectChange("co_applicant_gender", v)}>
              <SelectTrigger data-testid="co-applicant-gender-select"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="male">Male (S/o)</SelectItem>
                <SelectItem value="female">Female (D/o)</SelectItem>
                <SelectItem value="spouse">Spouse (W/o)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="co_applicant_date_of_birth">Date of Birth</Label>
            <Input id="co_applicant_date_of_birth" name="co_applicant_date_of_birth" type="date" value={formData.co_applicant_date_of_birth} onChange={onInputChange} data-testid="co-applicant-dob-input" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="co_applicant_phone">Phone</Label>
            <Input id="co_applicant_phone" name="co_applicant_phone" value={formData.co_applicant_phone} onChange={onInputChange} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="co_applicant_email">Email</Label>
            <Input id="co_applicant_email" name="co_applicant_email" type="email" value={formData.co_applicant_email} onChange={onInputChange} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="co_applicant_pan">PAN Number</Label>
            <Input id="co_applicant_pan" name="co_applicant_pan" value={formData.co_applicant_pan} onChange={onInputChange} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="co_applicant_aadhar">Aadhaar Number</Label>
            <Input id="co_applicant_aadhar" name="co_applicant_aadhar" value={formData.co_applicant_aadhar} onChange={onInputChange} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="co_applicant_profession">Profession</Label>
            <Select value={formData.co_applicant_profession} onValueChange={(v) => onSelectChange("co_applicant_profession", v)}>
              <SelectTrigger><SelectValue placeholder="Select profession" /></SelectTrigger>
              <SelectContent>
                {professions.map((prof) => (
                  <SelectItem key={prof} value={prof}>{prof}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="co_applicant_nationality">Nationality</Label>
            <Select value={formData.co_applicant_nationality} onValueChange={(v) => onSelectChange("co_applicant_nationality", v)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
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
          <Textarea id="co_applicant_address" name="co_applicant_address" value={formData.co_applicant_address} onChange={onInputChange} rows={2} />
        </div>

        {/* Co-Applicant Document Uploads */}
        {formData.co_applicant_name && (
          <div className="mt-4 p-4 bg-slate-50 rounded-lg">
            <h4 className="font-medium text-slate-700 mb-3 flex items-center gap-2">
              <FileText className="w-4 h-4" /> Co-Applicant Documents
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <DocumentUploadField label="PAN Card" fileType="co_pan_card" fileRef={fileRefs.coPan} cameraRef={cameraRefs.coPan} uploadedFile={uploadedFiles.co_pan_card} onUpload={onFileUpload} onRemove={onRemoveFile} />
              <DocumentUploadField label="Aadhaar Card" fileType="co_aadhar_card" fileRef={fileRefs.coAadhar} cameraRef={cameraRefs.coAadhar} uploadedFile={uploadedFiles.co_aadhar_card} onUpload={onFileUpload} onRemove={onRemoveFile} />
              {(formData.co_applicant_nationality === "NRI" || formData.co_applicant_nationality === "OCI") && (
                <DocumentUploadField label="Passport" fileType="co_passport" fileRef={fileRefs.coPassport} cameraRef={cameraRefs.coPassport} uploadedFile={uploadedFiles.co_passport} onUpload={onFileUpload} onRemove={onRemoveFile} />
              )}
            </div>
            <p className="text-xs text-slate-500 mt-2">Accepted formats: JPEG, PNG, PDF. Max size: 5MB.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ApplicantDetailsStep;
