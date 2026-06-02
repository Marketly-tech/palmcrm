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

const PropertyPricingCard = ({
  customer,
  editing,
  editData,
  setEditData,
  liveCalc,
  formatCurrency,
  handleEditChange,
}) => {
  return (
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
              <Label>Car Parking Charges</Label>
              {editing ? (
                <Input
                  type="number"
                  min="0"
                  value={editData.additional_parking_charges ?? 200000}
                  onChange={(e) => setEditData({ ...editData, additional_parking_charges: parseFloat(e.target.value) || 0 })}
                  className="mt-1"
                  data-testid="car-parking-charges-input"
                />
              ) : (
                <p className="text-slate-700 mt-1">{formatCurrency(customer.additional_parking_charges ?? 200000)}</p>
              )}
            </div>
            <div>
              <Label>BESCOM Rate (&#8377;/sq.ft)</Label>
              {editing ? (
                <>
                  <Input
                    type="number"
                    min="0"
                    value={editData.bescom_rate ?? 0}
                    onChange={(e) => setEditData({ ...editData, bescom_rate: parseFloat(e.target.value) || 0 })}
                    placeholder="e.g. 50"
                    className="mt-1"
                    data-testid="bescom-rate-input"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    {(editData.bescom_rate || 0) > 0 && (editData.saleable_area || 0) > 0
                      ? `Total: ${formatCurrency(Math.round((parseFloat(editData.bescom_rate) || 0) * (parseFloat(editData.saleable_area) || 0)))} (rate × ${editData.saleable_area} sq.ft)`
                      : "Manual entry · multiplied by saleable area · included in subtotal (before GST)"}
                  </p>
                </>
              ) : (
                <p className="text-slate-700 mt-1" data-testid="bescom-amount-value">
                  {formatCurrency(Math.round((customer.bescom_rate || 0) * (customer.saleable_area || 0)))}
                  {(customer.bescom_rate || 0) > 0 && (
                    <span className="text-xs text-slate-500 ml-2">(&#8377;{customer.bescom_rate}/sq.ft &times; {customer.saleable_area || 0})</span>
                  )}
                </p>
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
                  value={editData.club_house_charges ?? 300000}
                  onChange={(e) => setEditData({ ...editData, club_house_charges: parseFloat(e.target.value) || 0 })}
                  className="mt-1"
                />
              ) : (
                <p className="text-slate-700 mt-1">{formatCurrency(customer.club_house_charges)}</p>
              )}
            </div>
            <div>
              <Label>Additional Charges</Label>
              {editing ? (
                <Input
                  type="number"
                  value={editData.additional_charges || 0}
                  onChange={(e) => setEditData({ ...editData, additional_charges: parseFloat(e.target.value) || 0 })}
                  className="mt-1"
                  placeholder="Enter additional charges"
                />
              ) : (
                <p className="text-slate-700 mt-1">{formatCurrency(customer.additional_charges || 0)}</p>
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
              <Label>Interest Amount</Label>
              {editing ? (
                <>
                  <Input
                    type="number"
                    value={editData.interest_amount ?? ""}
                    onChange={(e) => setEditData({ ...editData, interest_amount: parseFloat(e.target.value) || 0 })}
                    placeholder="0"
                    className="mt-1"
                    data-testid="interest-amount-input"
                  />
                  <p className="text-xs text-slate-500 mt-1">Manual entry · added after GST (non GST-taxable)</p>
                </>
              ) : (
                <p className="text-slate-700 mt-1" data-testid="interest-amount-value">
                  {formatCurrency(customer.interest_amount || 0)}
                </p>
              )}
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
              <p className="text-sm text-green-700 font-medium mb-2">Live Price Preview</p>
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
                <span>Car Parking:</span>
                <span className="font-medium text-right">{formatCurrency(liveCalc.parkingCharges)}</span>
                {liveCalc.bescomAmount > 0 && (
                  <>
                    <span>BESCOM (&#8377;{liveCalc.bescomRate}/sq.ft):</span>
                    <span className="font-medium text-right">{formatCurrency(liveCalc.bescomAmount)}</span>
                  </>
                )}
                {liveCalc.interestAmount > 0 && (
                  <>
                    <span>Interest Amount (post-GST):</span>
                    <span className="font-medium text-right">{formatCurrency(liveCalc.interestAmount)}</span>
                  </>
                )}
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
  );
};

export default PropertyPricingCard;
