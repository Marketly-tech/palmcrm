import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { Label } from "../../ui/label";
import { Input } from "../../ui/input";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "../../ui/select";

const CoApplicantCard = ({ customer, editing, editData, setEditData }) => {
  if (!customer.co_applicant_name && !editing) return null;

  const updateCustomField = (key, value) => {
    setEditData({
      ...editData,
      custom_fields: { ...(editData.custom_fields || {}), [key]: value },
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Co-Applicant Details</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label>Name</Label>
            {editing ? (
              <Input
                value={editData.co_applicant_name || ""}
                onChange={(e) => setEditData({ ...editData, co_applicant_name: e.target.value })}
                placeholder="Co-applicant full name"
              />
            ) : (
              <p className="text-slate-700 mt-1">{customer.co_applicant_name}</p>
            )}
          </div>
          <div>
            <Label>
              {(editing ? editData.co_applicant_gender : customer.co_applicant_gender) === "female"
                ? "Father's/Spouse Name (D/o)"
                : (editing ? editData.co_applicant_gender : customer.co_applicant_gender) === "spouse"
                ? "Spouse Name (W/o)"
                : "Father's/Spouse Name (S/o)"}
            </Label>
            {editing ? (
              <Input
                value={editData.co_applicant_father_name || ""}
                onChange={(e) => setEditData({ ...editData, co_applicant_father_name: e.target.value })}
                placeholder="Father's/Spouse name"
              />
            ) : (
              <p className="text-slate-700 mt-1">{customer.co_applicant_father_name || "-"}</p>
            )}
          </div>
          <div>
            <Label>Gender</Label>
            {editing ? (
              <Select
                value={editData.co_applicant_gender || "male"}
                onValueChange={(v) => setEditData({ ...editData, co_applicant_gender: v })}
              >
                <SelectTrigger data-testid="co-applicant-gender-edit"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="male">Male (S/o)</SelectItem>
                  <SelectItem value="female">Female (D/o)</SelectItem>
                  <SelectItem value="spouse">Spouse (W/o)</SelectItem>
                </SelectContent>
              </Select>
            ) : (
              <p className="text-slate-700 mt-1">
                {customer.co_applicant_gender === "female" ? "Female (D/o)" :
                 customer.co_applicant_gender === "spouse" ? "Spouse (W/o)" :
                 customer.co_applicant_gender === "male" ? "Male (S/o)" : "-"}
              </p>
            )}
          </div>
          <div>
            <Label>Date of Birth</Label>
            {editing ? (
              <Input
                type="date"
                value={editData.co_applicant_date_of_birth || ""}
                onChange={(e) => setEditData({ ...editData, co_applicant_date_of_birth: e.target.value })}
              />
            ) : (
              <p className="text-slate-700 mt-1">{customer.co_applicant_date_of_birth || "-"}</p>
            )}
          </div>
          <div>
            <Label>Phone</Label>
            {editing ? (
              <Input
                value={editData.co_applicant_phone || ""}
                onChange={(e) => setEditData({ ...editData, co_applicant_phone: e.target.value })}
                placeholder="Phone number"
              />
            ) : (
              <p className="text-slate-700 mt-1">{customer.co_applicant_phone || "-"}</p>
            )}
          </div>
          <div>
            <Label>Email</Label>
            {editing ? (
              <Input
                value={editData.co_applicant_email || ""}
                onChange={(e) => setEditData({ ...editData, co_applicant_email: e.target.value })}
                placeholder="Email address"
              />
            ) : (
              <p className="text-slate-700 mt-1">{customer.co_applicant_email || "-"}</p>
            )}
          </div>
          <div>
            <Label>PAN Number</Label>
            {editing ? (
              <Input
                value={editData.co_applicant_pan || ""}
                onChange={(e) => setEditData({ ...editData, co_applicant_pan: e.target.value })}
                placeholder="PAN number"
              />
            ) : (
              <p className="text-slate-700 mt-1">{customer.co_applicant_pan || "-"}</p>
            )}
          </div>
          <div>
            <Label>Aadhaar Number</Label>
            {editing ? (
              <Input
                value={editData.co_applicant_aadhar || ""}
                onChange={(e) => setEditData({ ...editData, co_applicant_aadhar: e.target.value })}
                placeholder="Aadhaar number"
              />
            ) : (
              <p className="text-slate-700 mt-1">{customer.co_applicant_aadhar || "-"}</p>
            )}
          </div>
          <div>
            <Label>Profession</Label>
            {editing ? (
              <Input
                value={editData.custom_fields?.co_applicant_profession || ""}
                onChange={(e) => updateCustomField('co_applicant_profession', e.target.value)}
                placeholder="Profession"
              />
            ) : (
              <p className="text-slate-700 mt-1">{customer.custom_fields?.co_applicant_profession || "-"}</p>
            )}
          </div>
          <div>
            <Label>Nationality</Label>
            {editing ? (
              <Input
                value={editData.custom_fields?.co_applicant_nationality || "Indian"}
                onChange={(e) => updateCustomField('co_applicant_nationality', e.target.value)}
                placeholder="Nationality"
              />
            ) : (
              <p className="text-slate-700 mt-1">{customer.custom_fields?.co_applicant_nationality || "Indian"}</p>
            )}
          </div>
        </div>
        <div className="mt-4">
          <Label>Address</Label>
          {editing ? (
            <Input
              value={editData.co_applicant_address || ""}
              onChange={(e) => setEditData({ ...editData, co_applicant_address: e.target.value })}
              placeholder="Co-applicant address"
            />
          ) : (
            <p className="text-slate-700 mt-1">{customer.co_applicant_address || "-"}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default CoApplicantCard;
