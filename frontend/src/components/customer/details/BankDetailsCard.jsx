import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { Label } from "../../ui/label";
import { Input } from "../../ui/input";
import { Button } from "../../ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../../ui/select";
import { Edit, Save } from "lucide-react";

const BankDetailsCard = ({
  customer,
  bankDetailsEditing,
  setBankDetailsEditing,
  bankDetails,
  setBankDetails,
  handleSaveBankDetails,
  isAccountsRole,
}) => {
  return (
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
            {bankDetailsEditing ? "Cancel" : (
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
                  onValueChange={(value) => setBankDetails({
                    ...bankDetails,
                    bank_name: value,
                    bank_name_other: value !== "Others" ? "" : bankDetails.bank_name_other,
                  })}
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
  );
};

export default BankDetailsCard;
