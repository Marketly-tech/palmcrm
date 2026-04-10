import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger,
} from "../ui/dialog";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "../ui/select";
import { Plus, Loader2 } from "lucide-react";

const CreateCustomerDialog = ({
  open, onOpenChange, formData, setFormData, projects, submitting, onSubmit,
}) => {
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogTrigger asChild>
        <Button data-testid="add-customer-btn">
          <Plus className="w-4 h-4 mr-2" />
          Add Customer
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="font-heading">Add New Customer</DialogTitle>
        </DialogHeader>
        <form onSubmit={onSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Customer Name *</Label>
              <Input id="name" name="name" value={formData.name} onChange={handleInputChange} required data-testid="customer-name-input" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email *</Label>
              <Input id="email" name="email" type="email" value={formData.email} onChange={handleInputChange} required data-testid="customer-email-input" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Phone *</Label>
              <Input id="phone" name="phone" value={formData.phone} onChange={handleInputChange} required data-testid="customer-phone-input" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="father_name">Father's Name</Label>
              <Input id="father_name" name="father_name" value={formData.father_name} onChange={handleInputChange} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="pan_number">PAN Number</Label>
              <Input id="pan_number" name="pan_number" value={formData.pan_number} onChange={handleInputChange} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="project">Project *</Label>
              <Select value={formData.project} onValueChange={(value) => setFormData((prev) => ({ ...prev, project: value }))}>
                <SelectTrigger data-testid="customer-project-select"><SelectValue placeholder="Select project" /></SelectTrigger>
                <SelectContent>
                  {projects.map((project) => (
                    <SelectItem key={project.name} value={project.name}>{project.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="tower">Tower *</Label>
              <Input id="tower" name="tower" value={formData.tower} onChange={handleInputChange} required data-testid="customer-tower-input" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="unit_number">Unit Number *</Label>
              <Input id="unit_number" name="unit_number" value={formData.unit_number} onChange={handleInputChange} required data-testid="customer-unit-input" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="saleable_area">Saleable Area (sq.ft)</Label>
              <Input id="saleable_area" name="saleable_area" type="number" value={formData.saleable_area} onChange={handleInputChange} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="parking">Parking</Label>
              <Input id="parking" name="parking" value={formData.parking} onChange={handleInputChange} placeholder="e.g., 1 Covered" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="total_price">Total Price</Label>
              <Input id="total_price" name="total_price" type="number" value={formData.total_price} onChange={handleInputChange} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="booking_amount">Booking Amount</Label>
              <Input id="booking_amount" name="booking_amount" type="number" value={formData.booking_amount} onChange={handleInputChange} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="booking_date">Booking Date</Label>
              <Input id="booking_date" name="booking_date" type="date" value={formData.booking_date} onChange={handleInputChange} />
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-4">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
            <Button type="submit" disabled={submitting} data-testid="submit-customer-btn">
              {submitting ? (<><Loader2 className="w-4 h-4 mr-2 animate-spin" />Creating...</>) : "Create Customer"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default CreateCustomerDialog;
