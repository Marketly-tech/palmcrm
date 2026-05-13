import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import { Separator } from "../ui/separator";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "../ui/select";
import { CANONICAL_BANKS } from "../../utils/banks";

const PaymentStep = ({ formData, onInputChange, onSelectChange }) => {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="booking_amount">Booking Amount (&#8377;)</Label>
          <Input id="booking_amount" name="booking_amount" type="number" value={formData.booking_amount} onChange={onInputChange} placeholder="e.g., 200000" data-testid="booking-amount-input" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="transaction_date">Transaction Date</Label>
          <Input id="transaction_date" name="transaction_date" type="date" value={formData.transaction_date} onChange={onInputChange} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="transaction_bank">Bank Name</Label>
          <Input id="transaction_bank" name="transaction_bank" value={formData.transaction_bank} onChange={onInputChange} placeholder="e.g., HDFC Bank" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="transaction_details">Transaction Details</Label>
          <Input id="transaction_details" name="transaction_details" value={formData.transaction_details} onChange={onInputChange} placeholder="Cheque No. / NEFT Ref" />
        </div>
      </div>

      <Separator />

      <div className="space-y-4">
        <h3 className="font-semibold text-slate-700">Finance Preference</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="finance_type">Payment Type</Label>
            <Select value={formData.finance_type} onValueChange={(v) => onSelectChange("finance_type", v)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
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
              <Select value={formData.finance_bank} onValueChange={(v) => onSelectChange("finance_bank", v)}>
                <SelectTrigger><SelectValue placeholder="Select preferred bank" /></SelectTrigger>
                <SelectContent>
                  {CANONICAL_BANKS.map((b) => (
                    <SelectItem key={b} value={b}>{b}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="remarks">Additional Remarks</Label>
        <Textarea id="remarks" name="remarks" value={formData.remarks} onChange={onInputChange} rows={3} placeholder="Any additional information..." />
      </div>
    </div>
  );
};

export default PaymentStep;
