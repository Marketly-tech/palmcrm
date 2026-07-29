import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { Label } from "../../ui/label";
import { Input } from "../../ui/input";
import { Badge } from "../../ui/badge";
import { Lock } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../../ui/select";

// Keep in lockstep with LEGACY_PRICING_CUTOFF in hooks/useCustomerPage.js.
const LEGACY_PRICING_CUTOFF = new Date("2026-06-02T00:00:00Z");
const isLegacyPricingRecord = (customer) => {
  const raw = customer?.created_at;
  if (!raw) return false;
  const d = new Date(raw);
  return !Number.isNaN(d.getTime()) && d < LEGACY_PRICING_CUTOFF;
};

const PropertyPricingCard = ({
  customer,
  editing,
  editData,
  setEditData,
  liveCalc,
  formatCurrency,
  handleEditChange,
}) => {
  const legacyPricing = isLegacyPricingRecord(customer);
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between gap-3">
          <span>Property &amp; Pricing</span>
          {legacyPricing && (
            <Badge
              variant="outline"
              className="border-amber-300 bg-amber-50 text-amber-800 font-normal gap-1"
              title="This customer was created before 02 Jun 2026, when the pricing formula changed (BESCOM added to subtotal). Their original agreed total price is preserved and will NOT be recalculated on save."
              data-testid="legacy-price-locked-badge"
            >
              <Lock className="w-3 h-3" />
              Historical price (locked)
            </Badge>
          )}
        </CardTitle>
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
                  value={editData.additional_parking_charges ?? 0}
                  onChange={(e) => setEditData({ ...editData, additional_parking_charges: parseFloat(e.target.value) || 0 })}
                  className="mt-1"
                  data-testid="car-parking-charges-input"
                  placeholder="Enter 0 if not applicable"
                />
              ) : (
                <p className="text-slate-700 mt-1" data-testid="car-parking-charges-value">
                  {formatCurrency(customer.additional_parking_charges ?? 0)}
                </p>
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
              <p className="text-slate-700 mt-1" data-testid="base-price-value">
                {editing && liveCalc && !legacyPricing
                  ? formatCurrency(liveCalc.basePrice)
                  : formatCurrency(customer.base_price ?? 0)}
              </p>
            </div>
            <div>
              <Label>Floor Rise Total</Label>
              <p className="text-slate-700 mt-1" data-testid="floor-rise-total-value">
                {editing && liveCalc && !legacyPricing
                  ? formatCurrency(liveCalc.floorRiseTotal)
                  : formatCurrency(customer.custom_fields?.floor_rise_total ?? 0)}
              </p>
            </div>
            <div>
              <Label>Club House</Label>
              {editing ? (
                <Input
                  type="number"
                  min="0"
                  value={editData.club_house_charges ?? 0}
                  onChange={(e) => setEditData({ ...editData, club_house_charges: parseFloat(e.target.value) || 0 })}
                  className="mt-1"
                  data-testid="club-house-input"
                  placeholder="Enter 0 if not applicable"
                />
              ) : (
                <p className="text-slate-700 mt-1" data-testid="club-house-value">
                  {formatCurrency(customer.club_house_charges ?? 0)}
                </p>
              )}
            </div>
            <div>
              <Label>Additional Charges</Label>
              {editing ? (
                <>
                  <Input
                    type="number"
                    value={editData.additional_charges || 0}
                    onChange={(e) => setEditData({ ...editData, additional_charges: parseFloat(e.target.value) || 0 })}
                    className="mt-1"
                    placeholder="Enter additional charges amount"
                    data-testid="additional-charges-input"
                  />
                  <Input
                    type="text"
                    value={editData.additional_charges_description ?? ""}
                    onChange={(e) =>
                      setEditData({ ...editData, additional_charges_description: e.target.value })
                    }
                    className="mt-2"
                    placeholder="Description (e.g. Corner Unit Premium) — shown on Price Breakup"
                    maxLength={80}
                    data-testid="additional-charges-description-input"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Optional label &mdash; defaults to &ldquo;Additional Charges&rdquo; when blank
                  </p>
                </>
              ) : (
                <>
                  <p className="text-slate-700 mt-1" data-testid="additional-charges-value">
                    {formatCurrency(customer.additional_charges || 0)}
                  </p>
                  {(customer.additional_charges || 0) > 0 && customer.additional_charges_description && (
                    <p
                      className="text-xs text-slate-500 mt-0.5"
                      data-testid="additional-charges-description-value"
                    >
                      {customer.additional_charges_description}
                    </p>
                  )}
                </>
              )}
            </div>
            <div>
              <Label>Labour Cess (0.70%)</Label>
              {editing ? (
                <>
                  <div className="flex items-center gap-2 mt-1">
                    <Input
                      type="number"
                      min="0"
                      step="0.01"
                      value={
                        editData.labour_cess_manual
                          ? (editData.labour_cess ?? 0)
                          : (liveCalc ? liveCalc.labourCess : (customer.labour_cess ?? 0))
                      }
                      disabled={!editData.labour_cess_manual}
                      onChange={(e) =>
                        setEditData({
                          ...editData,
                          labour_cess: parseFloat(e.target.value) || 0,
                          labour_cess_manual: true,
                        })
                      }
                      className="flex-1"
                      data-testid="labour-cess-input"
                    />
                    <label
                      className="flex items-center gap-1 text-xs text-slate-600 whitespace-nowrap cursor-pointer"
                      title="Toggle to enter a custom value; untick to auto-compute at 0.70% of subtotal"
                    >
                      <input
                        type="checkbox"
                        checked={Boolean(editData.labour_cess_manual)}
                        onChange={(e) =>
                          setEditData({
                            ...editData,
                            labour_cess_manual: e.target.checked,
                            // Seed the manual value with the currently-shown auto value so admin has a sensible starting point.
                            labour_cess: e.target.checked
                              ? (liveCalc ? liveCalc.labourCess : (customer.labour_cess ?? 0))
                              : editData.labour_cess,
                          })
                        }
                        data-testid="labour-cess-manual-toggle"
                      />
                      Manual
                    </label>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    {editData.labour_cess_manual
                      ? "Manual override active · auto value would be " +
                        formatCurrency(liveCalc ? liveCalc.autoLabourCess : 0)
                      : "Auto-computed as 0.70% of subtotal · tick Manual to override"}
                  </p>
                </>
              ) : (
                <p className="text-slate-700 mt-1" data-testid="labour-cess-value">
                  {formatCurrency(customer.labour_cess ?? 0)}
                  {customer.labour_cess_manual && (
                    <span className="text-xs text-amber-700 ml-2">(manual override)</span>
                  )}
                </p>
              )}
            </div>
            <div>
              <Label>GST (5%)</Label>
              <p className="text-slate-700 mt-1" data-testid="gst-value">
                {editing && liveCalc && !legacyPricing
                  ? formatCurrency(liveCalc.gst)
                  : formatCurrency(customer.gst_amount ?? 0)}
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
              <p className={`font-bold mt-1 ${editing && liveCalc && !legacyPricing ? 'text-green-600' : 'text-primary'}`}>
                {editing && liveCalc && !legacyPricing
                  ? formatCurrency(liveCalc.total)
                  : formatCurrency(customer.total_price)}
                {editing && liveCalc && !legacyPricing && liveCalc.total !== customer.total_price && (
                  <span className="text-xs font-normal text-slate-500 ml-2">(live preview)</span>
                )}
                {editing && legacyPricing && (
                  <span
                    className="text-xs font-normal text-amber-700 ml-2"
                    data-testid="legacy-price-note"
                  >
                    (legacy — recalc skipped on save)
                  </span>
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
