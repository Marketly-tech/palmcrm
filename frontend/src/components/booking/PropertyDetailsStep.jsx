import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Separator } from "../ui/separator";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "../ui/select";
import { projects, bhkTypes, formatCurrency } from "./constants";

const PropertyDetailsStep = ({ formData, onInputChange, onSelectChange, priceCalc }) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="project">Project *</Label>
          <Select value={formData.project} onValueChange={(v) => onSelectChange("project", v)}>
            <SelectTrigger data-testid="project-select"><SelectValue placeholder="Select project" /></SelectTrigger>
            <SelectContent>
              {projects.map((p) => (
                <SelectItem key={p.name} value={p.name}>{p.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="tower">Tower *</Label>
          <Input id="tower" name="tower" value={formData.tower} onChange={onInputChange} placeholder="e.g., Tower-1, Block-A" required data-testid="tower-input" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="unit_number">Unit Number *</Label>
          <Input id="unit_number" name="unit_number" value={formData.unit_number} onChange={onInputChange} placeholder="e.g., 0701" required data-testid="unit-number-input" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="bhk_type">BHK Type *</Label>
          <Select value={formData.bhk_type} onValueChange={(v) => onSelectChange("bhk_type", v)}>
            <SelectTrigger data-testid="bhk-type-select"><SelectValue placeholder="Select BHK" /></SelectTrigger>
            <SelectContent>
              {bhkTypes.map((bhk) => (
                <SelectItem key={bhk} value={bhk}>{bhk}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="floor">Floor Number</Label>
          <Input id="floor" name="floor" type="number" value={formData.floor} onChange={onInputChange} placeholder="e.g., 7" data-testid="floor-input" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="saleable_area">Total Saleable Area (sq.ft) *</Label>
          <Input id="saleable_area" name="saleable_area" type="number" value={formData.saleable_area} onChange={onInputChange} placeholder="e.g., 1630" required data-testid="saleable-area-input" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="rate_per_sqft">Rate per sq.ft (&#8377;) *</Label>
          <Input id="rate_per_sqft" name="rate_per_sqft" type="number" value={formData.rate_per_sqft} onChange={onInputChange} placeholder="e.g., 6600" required data-testid="rate-input" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="floor_rise_cost">Floor Rise (&#8377; per sq.ft)</Label>
          <Input id="floor_rise_cost" name="floor_rise_cost" type="number" value={formData.floor_rise_cost} onChange={onInputChange} placeholder="e.g., 50" data-testid="floor-rise-input" />
          <p className="text-xs text-slate-500">Additional cost per sq.ft based on floor (enter 0 if not applicable)</p>
        </div>
        <div className="space-y-2 col-span-2 grid grid-cols-2 gap-3">
          <div className="p-3 bg-slate-50 rounded-md border">
            <Label className="text-xs text-slate-600">Club House Charges</Label>
            <p className="font-semibold text-slate-800 mt-1">&#8377;3,00,000 <span className="text-xs font-normal text-slate-500">(fixed)</span></p>
          </div>
          <div className="p-3 bg-slate-50 rounded-md border">
            <Label className="text-xs text-slate-600">Car Parking Charges</Label>
            <p className="font-semibold text-slate-800 mt-1">&#8377;2,00,000 <span className="text-xs font-normal text-slate-500">(fixed)</span></p>
          </div>
          <p className="col-span-2 text-xs text-slate-500">These are fixed at booking. Admin can edit them later from the customer profile if required.</p>
        </div>
        <div className="space-y-2 col-span-2">
          <Label htmlFor="additional_charges">Additional Charges (&#8377;) - Manual Entry</Label>
          <Input id="additional_charges" name="additional_charges" type="number" min="0" value={formData.additional_charges} onChange={onInputChange} placeholder="Enter any additional charges" />
          <p className="text-xs text-slate-500">Enter any extra charges like parking, amenities, etc.</p>
        </div>
        <div className="space-y-2 col-span-2">
          <Label htmlFor="bescom_rate">BESCOM Charges (&#8377; per sq.ft)</Label>
          <Input id="bescom_rate" name="bescom_rate" type="number" min="0" step="0.01" value={formData.bescom_rate} onChange={onInputChange} placeholder="e.g., 50" data-testid="bescom-rate-input" />
          <p className="text-xs text-slate-500">BESCOM (electricity) charges per sq.ft. Total = rate &times; saleable area. Added to subtotal before GST &amp; Labour Cess.</p>
        </div>
      </div>

      {/* Live Price Calculator */}
      {formData.saleable_area && formData.rate_per_sqft && (
        <div className="mt-6 p-4 bg-primary/5 border border-primary/20 rounded-lg">
          <h3 className="font-semibold text-slate-700 mb-3">Price Calculation Preview</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <span className="text-slate-600">Base Price ({formData.saleable_area} sq.ft x &#8377;{formData.rate_per_sqft}):</span>
            <span className="font-medium text-right">{formatCurrency(priceCalc.basePrice)}</span>
            {priceCalc.floorRiseTotal > 0 && (
              <>
                <span className="text-slate-600">Floor Rise ({formData.saleable_area} sq.ft x &#8377;{formData.floor_rise_cost}):</span>
                <span className="font-medium text-right">+{formatCurrency(priceCalc.floorRiseTotal)}</span>
              </>
            )}
            <span className="text-slate-600">Club House & Infrastructure:</span>
            <span className="font-medium text-right">{formatCurrency(priceCalc.clubHouse)}</span>
            <span className="text-slate-600">Car Parking:</span>
            <span className="font-medium text-right">{formatCurrency(priceCalc.carParking)}</span>
            {priceCalc.additionalCharges > 0 && (
              <>
                <span className="text-slate-600">Additional Charges:</span>
                <span className="font-medium text-right">{formatCurrency(priceCalc.additionalCharges)}</span>
              </>
            )}
            {priceCalc.bescomAmount > 0 && (
              <>
                <span className="text-slate-600">BESCOM Charges (&#8377;{priceCalc.bescomRate}/sq.ft &times; {formData.saleable_area}):</span>
                <span className="font-medium text-right">{formatCurrency(priceCalc.bescomAmount)}</span>
              </>
            )}
            <span className="text-slate-600">Labour Cess (0.70%):</span>
            <span className="font-medium text-right">{formatCurrency(priceCalc.labourCess)}</span>
            <span className="text-slate-600">GST (5%):</span>
            <span className="font-medium text-right">{formatCurrency(priceCalc.gst)}</span>
            <Separator className="col-span-2 my-2" />
            <span className="font-semibold text-primary">Total Flat Value:</span>
            <span className="font-bold text-primary text-right text-lg">{formatCurrency(priceCalc.total)}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default PropertyDetailsStep;
