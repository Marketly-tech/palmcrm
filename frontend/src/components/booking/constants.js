// Booking form constants and configuration

export const projects = [
  { name: "RRL Palm Altezze" },
  { name: "RRL NC 216" },
  { name: "RRL Palacio" },
  { name: "RRL Nature Woods" },
  { name: "RRL Towers" },
  { name: "RRL Complex" },
];

export const bhkTypes = ["2BHK", "2.5BHK", "3BHK", "3.5BHK", "4BHK"];

export const professions = [
  "Salaried", "Self-Employed", "Business Owner", "Professional",
  "Government Employee", "Retired", "Other"
];

export const initialFormData = {
  // Primary Applicant
  name: "", phone: "", email: "", father_name: "", date_of_birth: "",
  gender: "male", pan_number: "", aadhar_number: "", address: "",
  company: "", designation: "", profession: "", nationality: "Indian",
  // Co-Applicant
  co_applicant_name: "", co_applicant_father_name: "", co_applicant_gender: "male",
  co_applicant_phone: "",
  co_applicant_email: "", co_applicant_pan: "", co_applicant_aadhar: "",
  co_applicant_address: "", co_applicant_date_of_birth: "",
  co_applicant_profession: "", co_applicant_nationality: "Indian",
  // Property
  project: "", tower: "", unit_number: "", bhk_type: "", floor: "",
  saleable_area: "", rate_per_sqft: "6600", floor_rise_cost: "0",
  parking: "1", club_house_charges: "300000", car_parking_charges: "200000",
  additional_charges: "0", bescom_rate: "0",
  // Payment
  booking_amount: "", transaction_details: "", transaction_date: "", transaction_bank: "",
  // Finance
  finance_type: "self", finance_bank: "",
  // Remarks
  remarks: "",
};

export const initialUploadedFiles = {
  pan_card: null, aadhar_card: null, passport: null,
  co_pan_card: null, co_aadhar_card: null, co_passport: null,
};

export const formatCurrency = (amount) => {
  return new Intl.NumberFormat("en-IN", {
    style: "currency", currency: "INR", maximumFractionDigits: 0,
  }).format(amount || 0);
};

export const calculatePrice = (formData) => {
  const saleableArea = parseFloat(formData.saleable_area) || 0;
  const ratePerSqft = parseFloat(formData.rate_per_sqft) || 0;
  const floorRiseCost = parseFloat(formData.floor_rise_cost) || 0;
  const clubHouseCharges = parseFloat(formData.club_house_charges) || 300000;
  const carParkingCharges = parseFloat(formData.car_parking_charges) || 200000;
  const additionalCharges = parseFloat(formData.additional_charges) || 0;
  const bescomRate = parseFloat(formData.bescom_rate) || 0;

  const basePrice = saleableArea * ratePerSqft;
  const floorRiseTotal = saleableArea * floorRiseCost;
  const bescomAmount = bescomRate * saleableArea;
  const subtotal = basePrice + floorRiseTotal + clubHouseCharges + carParkingCharges + additionalCharges + bescomAmount;
  const labourCess = subtotal * 0.007;
  const gst = subtotal * 0.05;
  const total = subtotal + labourCess + gst;

  return {
    basePrice, floorRiseCost, floorRiseTotal,
    effectiveRate: ratePerSqft + floorRiseCost,
    clubHouse: clubHouseCharges, carParking: carParkingCharges, additionalCharges,
    bescomRate, bescomAmount,
    subtotal, labourCess, gst, total,
  };
};
