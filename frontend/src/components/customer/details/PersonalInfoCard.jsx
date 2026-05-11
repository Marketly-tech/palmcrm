import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { Label } from "../../ui/label";
import { Input } from "../../ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../../ui/select";

const PersonalInfoCard = ({ customer, editing, editData, setEditData }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Personal Information</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Full Name</Label>
              {editing ? (
                <Input
                  value={editData.name}
                  onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                />
              ) : (
                <p className="text-slate-700 mt-1">{customer.name}</p>
              )}
            </div>
            <div>
              <Label>Phone</Label>
              {editing ? (
                <Input
                  value={editData.phone}
                  onChange={(e) => setEditData({ ...editData, phone: e.target.value })}
                />
              ) : (
                <p className="text-slate-700 mt-1">{customer.phone}</p>
              )}
            </div>
            <div>
              <Label>Email</Label>
              {editing ? (
                <Input
                  value={editData.email}
                  onChange={(e) => setEditData({ ...editData, email: e.target.value })}
                />
              ) : (
                <p className="text-slate-700 mt-1">{customer.email}</p>
              )}
            </div>
            <div>
              <Label>Father's/Spouse Name</Label>
              {editing ? (
                <Input
                  value={editData.father_name || ""}
                  onChange={(e) => setEditData({ ...editData, father_name: e.target.value })}
                />
              ) : (
                <p className="text-slate-700 mt-1">{customer.father_name || "-"}</p>
              )}
            </div>
            <div>
              <Label>Date of Birth</Label>
              {editing ? (
                <Input
                  type="date"
                  value={editData.date_of_birth || ""}
                  onChange={(e) => setEditData({ ...editData, date_of_birth: e.target.value })}
                />
              ) : (
                <p className="text-slate-700 mt-1">{customer.date_of_birth || "-"}</p>
              )}
            </div>
            <div>
              <Label>Gender</Label>
              {editing ? (
                <Select
                  value={editData.gender || "male"}
                  onValueChange={(value) => setEditData({ ...editData, gender: value })}
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
              ) : (
                <p className="text-slate-700 mt-1">
                  {customer.gender === 'female' ? 'Female (D/o)' :
                   customer.gender === 'spouse' ? 'Spouse (W/o)' : 'Male (S/o)'}
                </p>
              )}
            </div>
            <div>
              <Label>Nationality</Label>
              <p className="text-slate-700 mt-1">{customer.nationality || "Indian"}</p>
            </div>
            <div>
              <Label>PAN Number</Label>
              <p className="text-slate-700 mt-1">{customer.pan_number || "-"}</p>
            </div>
            <div>
              <Label>Aadhaar Number</Label>
              <p className="text-slate-700 mt-1">{customer.aadhar_number || "-"}</p>
            </div>
            <div>
              <Label>Profession</Label>
              <p className="text-slate-700 mt-1">{customer.custom_fields?.profession || "-"}</p>
            </div>
            <div>
              <Label>Company</Label>
              <p className="text-slate-700 mt-1">{customer.company || "-"}</p>
            </div>
            <div>
              <Label>Designation</Label>
              <p className="text-slate-700 mt-1">{customer.designation || "-"}</p>
            </div>
          </div>
          <div>
            <Label>Address</Label>
            <p className="text-slate-700 mt-1">{customer.address || "-"}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default PersonalInfoCard;
