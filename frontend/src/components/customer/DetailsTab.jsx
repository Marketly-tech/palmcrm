import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Label } from "../ui/label";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Edit, Save, Pencil } from "lucide-react";

const DetailsTab = ({
  customer,
  editing,
  editData,
  setEditData,
  liveCalc,
  formatCurrency,
  handleEditChange,
  // Booking details
  editingBooking,
  setEditingBooking,
  savingBooking,
  bookingForm,
  setBookingForm,
  handleSaveBookingDetails,
  // Bank details
  bankDetailsEditing,
  setBankDetailsEditing,
  bankDetails,
  setBankDetails,
  handleSaveBankDetails,
  // Auth
  user,
  isAccountsRole,
}) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Personal Information */}
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

      {/* Property & Pricing */}
      <Card>
        <CardHeader>
          <CardTitle>Property & Pricing</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>BHK Type</Label>
                {editing ? (
                  <Select
                    value={editData.bhk_type || ""}
                    onValueChange={(value) => setEditData({ ...editData, bhk_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select BHK" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="2BHK">2 BHK</SelectItem>
                      <SelectItem value="2.5BHK">2.5 BHK</SelectItem>
                      <SelectItem value="3BHK">3 BHK</SelectItem>
                      <SelectItem value="3.5BHK">3.5 BHK</SelectItem>
                      <SelectItem value="4BHK">4 BHK</SelectItem>
                    </SelectContent>
                  </Select>
                ) : (
                  <p className="text-slate-700 mt-1">{customer.bhk_type || "-"}</p>
                )}
              </div>
              <div>
                <Label>Floor</Label>
                {editing ? (
                  <Input
                    type="number"
                    value={editData.floor || ""}
                    onChange={(e) => handleEditChange('floor', parseInt(e.target.value) || 0)}
                    placeholder="Floor number"
                  />
                ) : (
                  <p className="text-slate-700 mt-1">{customer.floor || "0"}</p>
                )}
              </div>
              <div>
                <Label>Saleable Area (sq.ft)</Label>
                {editing ? (
                  <Input
                    type="number"
                    value={editData.saleable_area || ""}
                    onChange={(e) => handleEditChange('saleable_area', parseFloat(e.target.value) || 0)}
                  />
                ) : (
                  <p className="text-slate-700 mt-1">{customer.saleable_area || 0} sq.ft</p>
                )}
              </div>
              <div>
                <Label>Rate/Sq.ft (₹)</Label>
                {editing ? (
                  <Input
                    type="number"
                    value={editData.rate_per_sqft || ""}
                    onChange={(e) => handleEditChange('rate_per_sqft', parseFloat(e.target.value) || 0)}
                  />
                ) : (
                  <p className="text-slate-700 mt-1">₹{customer.rate_per_sqft?.toLocaleString() || 0}</p>
                )}
              </div>
              <div>
                <Label>Floor Rise (₹/sq.ft)</Label>
                {editing ? (
                  <>
                    <Input
                      type="number"
                      value={editData.floor_rise_cost || ""}
                      onChange={(e) => handleEditChange('floor_rise_cost', parseFloat(e.target.value) || 0)}
                      placeholder="e.g., 50"
                    />
                    <p className="text-xs text-slate-500 mt-1">Manual floor rise cost per sq.ft</p>
                  </>
                ) : (
                  <p className="text-slate-700 mt-1">₹{customer.custom_fields?.floor_rise_cost || 0}/sq.ft</p>
                )}
              </div>
              <div>
                <Label>Additional Parking</Label>
                {editing ? (
                  <Input
                    type="number"
                    min="0"
                    value={editData.additional_parking || "0"}
                    onChange={(e) => handleEditChange('additional_parking', parseInt(e.target.value) || 0)}
                  />
                ) : (
                  <p className="text-slate-700 mt-1">{customer.additional_parking || 0}</p>
                )}
              </div>
              <div>
                <Label>Base Price</Label>
                <p className="text-slate-700 mt-1">
                  {editing && liveCalc ? formatCurrency(liveCalc.basePrice) : formatCurrency(customer.base_price)}
                </p>
              </div>
              <div>
                <Label>Floor Rise Total</Label>
                <p className="text-slate-700 mt-1">
                  {editing && liveCalc ? formatCurrency(liveCalc.floorRiseTotal) : formatCurrency(customer.custom_fields?.floor_rise_total || 0)}
                </p>
              </div>
              <div>
                <Label>Club House</Label>
                {editing ? (
                  <Input
                    type="number"
                    value={editData.club_house_charges || 200000}
                    onChange={(e) => setEditData({...editData, club_house_charges: parseFloat(e.target.value) || 0})}
                    className="mt-1"
                  />
                ) : (
                  <p className="text-slate-700 mt-1">
                    {formatCurrency(customer.club_house_charges)}
                  </p>
                )}
              </div>
              <div>
                <Label>Additional Charges</Label>
                {editing ? (
                  <Input
                    type="number"
                    value={editData.additional_charges || 0}
                    onChange={(e) => setEditData({...editData, additional_charges: parseFloat(e.target.value) || 0})}
                    className="mt-1"
                    placeholder="Enter additional charges"
                  />
                ) : (
                  <p className="text-slate-700 mt-1">
                    {formatCurrency(customer.additional_charges || 0)}
                  </p>
                )}
              </div>
              <div>
                <Label>Labour Cess (0.70%)</Label>
                <p className="text-slate-700 mt-1">
                  {editing && liveCalc ? formatCurrency(liveCalc.labourCess) : formatCurrency(customer.labour_cess)}
                </p>
              </div>
              <div>
                <Label>GST (5%)</Label>
                <p className="text-slate-700 mt-1">
                  {editing && liveCalc ? formatCurrency(liveCalc.gst) : formatCurrency(customer.gst_amount)}
                </p>
              </div>
              <div>
                <Label>Total Price</Label>
                <p className={`font-bold mt-1 ${editing && liveCalc ? 'text-green-600' : 'text-primary'}`}>
                  {editing && liveCalc ? formatCurrency(liveCalc.total) : formatCurrency(customer.total_price)}
                  {editing && liveCalc && liveCalc.total !== customer.total_price && (
                    <span className="text-xs font-normal text-slate-500 ml-2">(live preview)</span>
                  )}
                </p>
              </div>
              <div>
                <Label>UDS</Label>
                <p className="text-slate-700 mt-1">
                  {editing && liveCalc ? liveCalc.uds : (customer.uds || "-")}
                </p>
              </div>
            </div>
            {editing && liveCalc && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-700 font-medium mb-2">
                  Live Price Preview
                </p>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <span>Base Price ({editData.saleable_area || 0} × ₹{editData.rate_per_sqft || 0}):</span>
                  <span className="font-medium text-right">{formatCurrency(liveCalc.basePrice)}</span>
                  {liveCalc.floorRiseTotal > 0 && (
                    <>
                      <span>Floor Rise ({editData.saleable_area || 0} × ₹{editData.floor_rise_cost || 0}):</span>
                      <span className="font-medium text-right">{formatCurrency(liveCalc.floorRiseTotal)}</span>
                    </>
                  )}
                  <span>Club House & Infrastructure:</span>
                  <span className="font-medium text-right">{formatCurrency(liveCalc.clubHouse)}</span>
                  {liveCalc.additionalCharges > 0 && (
                    <>
                      <span>Additional Charges:</span>
                      <span className="font-medium text-right">{formatCurrency(liveCalc.additionalCharges)}</span>
                    </>
                  )}
                  <span>Additional Parking:</span>
                  <span className="font-medium text-right">{formatCurrency(liveCalc.parkingCharges)}</span>
                  <span className="font-semibold pt-2 border-t">New Total:</span>
                  <span className="font-bold text-right text-green-700 pt-2 border-t">{formatCurrency(liveCalc.total)}</span>
                </div>
                <p className="text-xs text-green-600 mt-2">
                  Price updates automatically as you edit. Click "Save Changes" to persist.
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Booking Details */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Booking Details</CardTitle>
          {user?.role === "admin" && !editingBooking && (
            <Button variant="outline" size="sm" onClick={() => setEditingBooking(true)} data-testid="edit-booking-btn">
              <Pencil className="w-4 h-4 mr-1" /> Edit
            </Button>
          )}
        </CardHeader>
        <CardContent>
          {editingBooking ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="edit-finance-type">Finance Type</Label>
                  <Select value={bookingForm.finance_type} onValueChange={(v) => setBookingForm(prev => ({...prev, finance_type: v}))}>
                    <SelectTrigger id="edit-finance-type" data-testid="edit-finance-type">
                      <SelectValue placeholder="Select" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="self">Self</SelectItem>
                      <SelectItem value="loan">Loan</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="edit-finance-bank">Bank</Label>
                  <Input id="edit-finance-bank" data-testid="edit-finance-bank" value={bookingForm.finance_bank} onChange={(e) => setBookingForm(prev => ({...prev, finance_bank: e.target.value}))} />
                </div>
                <div>
                  <Label htmlFor="edit-booking-amount">Booking Amount</Label>
                  <Input id="edit-booking-amount" data-testid="edit-booking-amount" type="number" value={bookingForm.booking_amount} onChange={(e) => setBookingForm(prev => ({...prev, booking_amount: e.target.value}))} />
                </div>
                <div>
                  <Label htmlFor="edit-booking-date">Booking Date</Label>
                  <Input id="edit-booking-date" data-testid="edit-booking-date" type="date" value={bookingForm.booking_date} onChange={(e) => setBookingForm(prev => ({...prev, booking_date: e.target.value}))} />
                </div>
              </div>
              <div className="flex gap-2 justify-end">
                <Button variant="outline" size="sm" onClick={() => setEditingBooking(false)} data-testid="cancel-booking-edit">Cancel</Button>
                <Button size="sm" onClick={handleSaveBookingDetails} disabled={savingBooking} data-testid="save-booking-btn">
                  {savingBooking ? "Saving..." : "Save"}
                </Button>
              </div>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Finance Type</Label>
                  <p className="text-slate-700 mt-1 capitalize">{customer.finance_type || "Self"}</p>
                </div>
                <div>
                  <Label>Bank</Label>
                  <p className="text-slate-700 mt-1">{customer.finance_bank || "-"}</p>
                </div>
                <div>
                  <Label>Booking Amount</Label>
                  <p className="text-slate-700 mt-1">{formatCurrency(customer.booking_amount)}</p>
                </div>
                <div>
                  <Label>Booking Date</Label>
                  <p className="text-slate-700 mt-1">{customer.booking_date || "-"}</p>
                </div>
              </div>
              {(customer.transaction_details || customer.transaction_date || customer.transaction_bank) && (
                <div className="mt-4 pt-4 border-t">
                  <p className="font-medium text-slate-700 mb-3">Transaction Details</p>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Transaction Date</Label>
                      <p className="text-slate-700 mt-1">{customer.transaction_date || "-"}</p>
                    </div>
                    <div>
                      <Label>Transaction Bank</Label>
                      <p className="text-slate-700 mt-1">{customer.transaction_bank || "-"}</p>
                    </div>
                  </div>
                  {customer.transaction_details && (
                    <div className="mt-2">
                      <Label>Transaction Reference</Label>
                      <p className="text-slate-700 mt-1">{customer.transaction_details}</p>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
          {customer.remarks && (
            <div className="mt-4 pt-4 border-t">
              <Label>Remarks</Label>
              <p className="text-slate-700 mt-1">{customer.remarks}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Bank Opted for Loan */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Bank Opted for Loan</CardTitle>
          {!isAccountsRole && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setBankDetailsEditing(!bankDetailsEditing)}
              data-testid="edit-bank-details-btn"
            >
              {bankDetailsEditing ? (
                <>Cancel</>
              ) : (
                <>
                  <Edit className="w-4 h-4 mr-1" />
                  Edit
                </>
              )}
            </Button>
          )}
        </CardHeader>
        <CardContent>
          {bankDetailsEditing ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Bank Name *</Label>
                  <Select
                    value={bankDetails.bank_name || ""}
                    onValueChange={(value) => setBankDetails({ ...bankDetails, bank_name: value, bank_name_other: value !== "Others" ? "" : bankDetails.bank_name_other })}
                  >
                    <SelectTrigger data-testid="bank-name-select">
                      <SelectValue placeholder="Select bank" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="HDFC">HDFC Bank</SelectItem>
                      <SelectItem value="BOB">Bank of Baroda</SelectItem>
                      <SelectItem value="TATA">Tata Capital</SelectItem>
                      <SelectItem value="SBI">State Bank of India</SelectItem>
                      <SelectItem value="ICICI">ICICI Bank</SelectItem>
                      <SelectItem value="AXIS">Axis Bank</SelectItem>
                      <SelectItem value="PNB">Punjab National Bank</SelectItem>
                      <SelectItem value="KOTAK">Kotak Mahindra Bank</SelectItem>
                      <SelectItem value="Others">Others</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                {bankDetails.bank_name === "Others" && (
                  <div>
                    <Label>Other Bank Name *</Label>
                    <Input
                      value={bankDetails.bank_name_other || ""}
                      onChange={(e) => setBankDetails({ ...bankDetails, bank_name_other: e.target.value })}
                      placeholder="Enter bank name"
                      data-testid="bank-name-other-input"
                    />
                  </div>
                )}
                <div>
                  <Label>Account Holder Name</Label>
                  <Input
                    value={bankDetails.bank_account_holder || ""}
                    onChange={(e) => setBankDetails({ ...bankDetails, bank_account_holder: e.target.value })}
                    placeholder="Enter account holder name"
                    data-testid="bank-account-holder-input"
                  />
                </div>
                <div>
                  <Label>Account Number</Label>
                  <Input
                    value={bankDetails.bank_account_number || ""}
                    onChange={(e) => setBankDetails({ ...bankDetails, bank_account_number: e.target.value })}
                    placeholder="Enter account number"
                    data-testid="bank-account-number-input"
                  />
                </div>
                <div>
                  <Label>IFSC Code</Label>
                  <Input
                    value={bankDetails.bank_ifsc_code || ""}
                    onChange={(e) => setBankDetails({ ...bankDetails, bank_ifsc_code: e.target.value.toUpperCase() })}
                    placeholder="Enter IFSC code"
                    data-testid="bank-ifsc-input"
                  />
                </div>
                <div>
                  <Label>Branch</Label>
                  <Input
                    value={bankDetails.bank_branch || ""}
                    onChange={(e) => setBankDetails({ ...bankDetails, bank_branch: e.target.value })}
                    placeholder="Enter branch name"
                    data-testid="bank-branch-input"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => {
                  setBankDetailsEditing(false);
                  setBankDetails({
                    bank_name: customer.bank_name || "",
                    bank_name_other: customer.bank_name_other || "",
                    bank_account_number: customer.bank_account_number || "",
                    bank_ifsc_code: customer.bank_ifsc_code || "",
                    bank_branch: customer.bank_branch || "",
                    bank_account_holder: customer.bank_account_holder || "",
                  });
                }}>
                  Cancel
                </Button>
                <Button onClick={handleSaveBankDetails} data-testid="save-bank-details-btn">
                  <Save className="w-4 h-4 mr-1" />
                  Save Bank Details
                </Button>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Bank Name</Label>
                <p className="text-slate-700 mt-1">
                  {customer.bank_name === "Others" 
                    ? customer.bank_name_other || "-" 
                    : customer.bank_name || "-"}
                </p>
              </div>
              <div>
                <Label>Account Holder</Label>
                <p className="text-slate-700 mt-1">{customer.bank_account_holder || "-"}</p>
              </div>
              <div>
                <Label>Account Number</Label>
                <p className="text-slate-700 mt-1 font-mono">{customer.bank_account_number || "-"}</p>
              </div>
              <div>
                <Label>IFSC Code</Label>
                <p className="text-slate-700 mt-1 font-mono">{customer.bank_ifsc_code || "-"}</p>
              </div>
              <div>
                <Label>Branch</Label>
                <p className="text-slate-700 mt-1">{customer.bank_branch || "-"}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Co-Applicant Details */}
      {customer.co_applicant_name && (
        <Card>
          <CardHeader>
            <CardTitle>Co-Applicant Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Name</Label>
                <p className="text-slate-700 mt-1">{customer.co_applicant_name}</p>
              </div>
              <div>
                <Label>Father's/Spouse Name</Label>
                <p className="text-slate-700 mt-1">{customer.co_applicant_father_name || "-"}</p>
              </div>
              <div>
                <Label>Date of Birth</Label>
                <p className="text-slate-700 mt-1">{customer.co_applicant_date_of_birth || "-"}</p>
              </div>
              <div>
                <Label>Phone</Label>
                <p className="text-slate-700 mt-1">{customer.co_applicant_phone || "-"}</p>
              </div>
              <div>
                <Label>Email</Label>
                <p className="text-slate-700 mt-1">{customer.co_applicant_email || "-"}</p>
              </div>
              <div>
                <Label>PAN Number</Label>
                <p className="text-slate-700 mt-1">{customer.co_applicant_pan || "-"}</p>
              </div>
              <div>
                <Label>Aadhaar Number</Label>
                <p className="text-slate-700 mt-1">{customer.co_applicant_aadhar || "-"}</p>
              </div>
              <div>
                <Label>Profession</Label>
                <p className="text-slate-700 mt-1">{customer.custom_fields?.co_applicant_profession || "-"}</p>
              </div>
              <div>
                <Label>Nationality</Label>
                <p className="text-slate-700 mt-1">{customer.custom_fields?.co_applicant_nationality || "Indian"}</p>
              </div>
            </div>
            {customer.co_applicant_address && (
              <div className="mt-4">
                <Label>Address</Label>
                <p className="text-slate-700 mt-1">{customer.co_applicant_address}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DetailsTab;
