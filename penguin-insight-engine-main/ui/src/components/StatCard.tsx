import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: string;
  glowColor?: "cyan" | "purple" | "blue";
}

const StatCard = ({ title, value, icon: Icon, trend, glowColor = "cyan" }: StatCardProps) => {
  return (
    <div className={cn(
      "glass-card rounded-xl p-6 transition-all duration-300 hover:scale-105",
      glowColor === "cyan" && "hover:glow-cyan",
      glowColor === "purple" && "hover:glow-purple",
      glowColor === "blue" && "hover:glow-blue"
    )}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-muted-foreground mb-1">{title}</p>
          <p className="text-3xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            {value}
          </p>
          {trend && (
            <p className="text-xs text-muted-foreground mt-2">{trend}</p>
          )}
        </div>
        <div className={cn(
          "p-3 rounded-lg",
          glowColor === "cyan" && "bg-primary/20",
          glowColor === "purple" && "bg-secondary/20",
          glowColor === "blue" && "bg-accent/20"
        )}>
          <Icon className={cn(
            "w-6 h-6",
            glowColor === "cyan" && "text-primary",
            glowColor === "purple" && "text-secondary",
            glowColor === "blue" && "text-accent"
          )} />
        </div>
      </div>
    </div>
  );
};

export default StatCard;
