import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { Button } from "../ui/button";
import { Avatar, AvatarFallback } from "../ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import {
  LayoutDashboard,
  Users,
  CreditCard,
  FileText,
  Calculator,
  BarChart3,
  Settings,
  LogOut,
  Menu,
  X,
  Building2,
  ChevronDown,
  UserPlus,
} from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Leads", href: "/leads", icon: UserPlus },
  { name: "Customers", href: "/customers", icon: Users },
  { name: "Payments", href: "/payments", icon: CreditCard },
  { name: "Documents", href: "/documents", icon: FileText },
  { name: "Calculator", href: "/calculator", icon: Calculator },
  { name: "Reports", href: "/reports", icon: BarChart3 },
  { name: "Settings", href: "/settings", icon: Settings },
];

const DashboardLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const getInitials = (name) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const getRoleBadgeColor = (role) => {
    const colors = {
      admin: "bg-yellow-900/30 text-yellow-400 border border-yellow-500/30",
      manager: "bg-purple-900/30 text-purple-400 border border-purple-500/30",
      accounts: "bg-blue-900/30 text-blue-400 border border-blue-500/30",
      sales: "bg-green-900/30 text-green-400 border border-green-500/30",
      support: "bg-orange-900/30 text-orange-400 border border-orange-500/30",
    };
    return colors[role] || "bg-gray-900/30 text-gray-400";
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/70 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar - Black with Gold accents */}
      <aside
        className={`fixed left-0 top-0 h-full bg-[#0a0a0a] text-slate-400 w-64 flex flex-col z-50 transform transition-transform duration-200 lg:translate-x-0 border-r border-[#d4af37]/20 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-[#d4af37]/20">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#d4af37] to-[#b8962e] flex items-center justify-center">
              <Building2 className="w-5 h-5 text-black" />
            </div>
            <span className="font-heading font-bold text-[#d4af37] text-lg">RRL CRM</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-slate-400 hover:text-[#d4af37]"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-md transition-all duration-200 ${
                  isActive
                    ? "bg-gradient-to-r from-[#d4af37] to-[#b8962e] text-black shadow-lg shadow-[#d4af37]/20"
                    : "hover:bg-[#d4af37]/10 hover:text-[#d4af37] hover:border-l-2 hover:border-[#d4af37]"
                }`
              }
              data-testid={`nav-${item.name.toLowerCase()}`}
            >
              <item.icon className="w-5 h-5" />
              {item.name}
            </NavLink>
          ))}
        </nav>

        {/* User section */}
        <div className="p-4 border-t border-[#d4af37]/20">
          <div className="flex items-center gap-3">
            <Avatar className="h-10 w-10 bg-gradient-to-br from-[#d4af37] to-[#b8962e]">
              <AvatarFallback className="bg-transparent text-black font-bold">
                {user ? getInitials(user.name) : "U"}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{user?.name}</p>
              <span
                className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium capitalize ${getRoleBadgeColor(
                  user?.role
                )}`}
              >
                {user?.role}
              </span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Header */}
        <header className="sticky top-0 z-30 h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 lg:px-6">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 rounded-md hover:bg-slate-100"
            data-testid="mobile-menu-btn"
          >
            <Menu className="w-5 h-5 text-slate-600" />
          </button>

          <div className="flex-1" />

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="flex items-center gap-2" data-testid="user-menu-btn">
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-primary text-white text-xs">
                    {user ? getInitials(user.name) : "U"}
                  </AvatarFallback>
                </Avatar>
                <span className="hidden sm:inline text-sm font-medium">{user?.name}</span>
                <ChevronDown className="w-4 h-4 text-slate-500" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <div className="px-2 py-1.5">
                <p className="text-sm font-medium">{user?.name}</p>
                <p className="text-xs text-muted-foreground">{user?.email}</p>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => navigate("/settings")} data-testid="settings-menu-item">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="text-red-600" data-testid="logout-menu-item">
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </header>

        {/* Page content */}
        <main className="p-4 lg:p-6 animate-fade-in">{children}</main>
      </div>
    </div>
  );
};

export default DashboardLayout;
