import { Link, useLocation } from "react-router-dom";
import { Home, Settings, Brain, BarChart3, Info } from "lucide-react";
import { cn } from "@/lib/utils";
import penguinLogo from "@/assets/penguin-logo.png";

const navItems = [
  { name: "Home", path: "/", icon: Home },
  { name: "Crawl Settings", path: "/crawl", icon: Settings },
  { name: "AI Extraction", path: "/extraction", icon: Brain },
  { name: "Results", path: "/results", icon: BarChart3 },
  { name: "System Info", path: "/system", icon: Info },
];

const Navigation = () => {
  const location = useLocation();

  return (
    <nav className="glass-card border-b sticky top-0 z-50 bg-black">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 group">
            <img src={penguinLogo} alt="Penguin Logo" className="w-10 h-10 transition-transform group-hover:scale-110" />
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                Extractify
              </h1>
            </div>
          </Link>
          
          <div className="flex gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200",
                    isActive 
                      ? "bg-primary/20 text-primary glow-cyan" 
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  )}
                >
                  <Icon className="w-4 h-4" />
                  <span className="text-sm font-medium hidden md:inline">{item.name}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
