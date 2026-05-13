import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { toast } from "sonner";
import { logError } from "../utils/logger";
import {
  StatsCards, RevenueCards, PaymentStageCard, ExportDataCard,
  PaymentStatusChart, UpcomingPayments, DueDateCountdown, RecentActivity,
} from "../components/dashboard";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DashboardPage = () => {
  const { user, hasRole } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [activities, setActivities] = useState([]);
  const [paymentsOverview, setPaymentsOverview] = useState(null);
  const [upcomingDueDates, setUpcomingDueDates] = useState([]);
  const [loading, setLoading] = useState(true);

  const [paymentStages, setPaymentStages] = useState([]);
  const [currentStage, setCurrentStage] = useState(null);
  const [stageOverdue, setStageOverdue] = useState(null);
  const [updatingStage, setUpdatingStage] = useState(false);

  const fetchDashboardData = useCallback(async () => {
    try {
      const [statsRes, activitiesRes, paymentsRes, dueDatesRes] = await Promise.all([
        axios.get(`${API}/dashboard/stats`),
        axios.get(`${API}/dashboard/recent-activities`),
        axios.get(`${API}/payments/overview`),
        axios.get(`${API}/dashboard/upcoming-due-dates`),
      ]);
      setStats(statsRes.data);
      setActivities(activitiesRes.data);
      setPaymentsOverview(paymentsRes.data);
      setUpcomingDueDates(dueDatesRes.data || []);
    } catch (error) {
      logError("Dashboard data fetch failed:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchPaymentStages = useCallback(async () => {
    try {
      const [stagesRes, currentRes] = await Promise.all([
        axios.get(`${API}/settings/payment-stages`),
        axios.get(`${API}/settings/current-stage`),
      ]);
      setPaymentStages(stagesRes.data);
      setCurrentStage(currentRes.data);
    } catch (error) {
      logError("Failed to fetch payment stages:", error);
    }
  }, []);

  const fetchStageOverdue = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/dashboard/overdue-by-stage`);
      setStageOverdue(res.data);
    } catch (error) {
      logError("Failed to fetch overdue data:", error);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
    if (hasRole("admin")) {
      fetchPaymentStages();
      fetchStageOverdue();
    }
  }, [fetchDashboardData, fetchPaymentStages, fetchStageOverdue, hasRole]);

  const handleStageChange = async (newStage) => {
    setUpdatingStage(true);
    try {
      await axios.post(`${API}/settings/current-stage`, { current_stage: newStage });
      toast.success("Payment stage updated successfully");
      await Promise.all([fetchPaymentStages(), fetchStageOverdue(), fetchDashboardData()]);
    } catch {
      toast.error("Failed to update payment stage");
    } finally {
      setUpdatingStage(false);
    }
  };

  const formatCurrency = (amount) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);

  const handleExport = async (type, format) => {
    try {
      const endpoint = type === "customers" ? `/export/customers/${format}` : `/export/payments/${format}`;
      const response = await axios.get(`${API}${endpoint}`, { responseType: "blob" });
      const blob = new Blob([response.data], {
        type: format === "excel" ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" : "text/csv",
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `RRL_${type.charAt(0).toUpperCase() + type.slice(1)}_Export.${format === "excel" ? "xlsx" : "csv"}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch {
      alert("Export failed. Please try again.");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="dashboard-page">
      <div>
        <h1 className="font-heading text-3xl font-bold text-slate-900">Welcome back, {user?.name?.split(" ")[0]}!</h1>
        <p className="text-slate-500 mt-1">Here's what's happening with your CRM today.</p>
      </div>

      <StatsCards stats={stats} />

      {hasRole("admin") && <RevenueCards stats={stats} formatCurrency={formatCurrency} />}

      {hasRole("admin") && (
        <PaymentStageCard
          paymentStages={paymentStages} currentStage={currentStage}
          stageOverdue={stageOverdue} updatingStage={updatingStage}
          onStageChange={handleStageChange} onNavigate={navigate}
          formatCurrency={formatCurrency}
        />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {hasRole("admin") && <ExportDataCard onExport={handleExport} />}
        <PaymentStatusChart stats={stats} />
      </div>

      <div className="grid grid-cols-1 gap-6">
        <UpcomingPayments paymentsOverview={paymentsOverview} formatCurrency={formatCurrency} />
      </div>

      <DueDateCountdown upcomingDueDates={upcomingDueDates} onNavigate={navigate} />

      <RecentActivity activities={activities} />
    </div>
  );
};

export default DashboardPage;
