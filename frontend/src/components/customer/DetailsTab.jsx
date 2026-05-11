import PersonalInfoCard from "./details/PersonalInfoCard";
import PropertyPricingCard from "./details/PropertyPricingCard";
import BookingDetailsCard from "./details/BookingDetailsCard";
import BankDetailsCard from "./details/BankDetailsCard";
import CoApplicantCard from "./details/CoApplicantCard";

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
      <PersonalInfoCard
        customer={customer}
        editing={editing}
        editData={editData}
        setEditData={setEditData}
      />
      <PropertyPricingCard
        customer={customer}
        editing={editing}
        editData={editData}
        setEditData={setEditData}
        liveCalc={liveCalc}
        formatCurrency={formatCurrency}
        handleEditChange={handleEditChange}
      />
      <BookingDetailsCard
        customer={customer}
        user={user}
        editingBooking={editingBooking}
        setEditingBooking={setEditingBooking}
        savingBooking={savingBooking}
        bookingForm={bookingForm}
        setBookingForm={setBookingForm}
        handleSaveBookingDetails={handleSaveBookingDetails}
        formatCurrency={formatCurrency}
      />
      <BankDetailsCard
        customer={customer}
        bankDetailsEditing={bankDetailsEditing}
        setBankDetailsEditing={setBankDetailsEditing}
        bankDetails={bankDetails}
        setBankDetails={setBankDetails}
        handleSaveBankDetails={handleSaveBankDetails}
        isAccountsRole={isAccountsRole}
      />
      <CoApplicantCard
        customer={customer}
        editing={editing}
        editData={editData}
        setEditData={setEditData}
      />
    </div>
  );
};

export default DetailsTab;
