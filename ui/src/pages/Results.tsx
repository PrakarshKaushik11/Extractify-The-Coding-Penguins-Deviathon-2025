import { useState, useEffect, useMemo } from "react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Download, Search, BarChart3, Users, Award, FileText, Loader2 } from "lucide-react";
import StatCard from "@/components/StatCard";
import { toast } from "sonner";
import { api } from "@/lib/api";

interface Entity {
  name: string;
  type: string;
  url: string;
  snippet: string;
  score: number;
}

const Results = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [entities, setEntities] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [apiReady, setApiReady] = useState(false);
  const [stats, setStats] = useState({
    totalEntities: 0,
    avgScore: "0%",
    entityTypes: 0,
    pagesAnalyzed: 0,
  });

  // ...existing code...
  // ...existing code...
  // Only keep one set of crawlConfig, lastRun, and domain declarations
  const crawlConfig = useMemo(() => {
    try { return JSON.parse(localStorage.getItem("penguin:crawlConfig") || "{}"); }
    catch { return {}; }
  }, [localStorage.getItem("penguin:crawlConfig")]);
  const lastRun = useMemo(() => {
    try { return JSON.parse(localStorage.getItem("penguin:lastRunStats") || "{}"); }
    catch { return {}; }
  }, [localStorage.getItem("penguin:lastRunStats")]);
  const domain: string = crawlConfig?.domain || lastRun?.domain || "—";

  // Reset state on unmount or crawlConfig change
  useEffect(() => {
    return () => {
      setEntities([]);
      setStats({
        totalEntities: 0,
        avgScore: "0%",
        entityTypes: 0,
        pagesAnalyzed: 0,
      });
    };
  }, [crawlConfig]);

  // Gate: wait for API to be ready (warmup) before polling results to avoid 502 spam
  useEffect(() => {
    let cancelled = false;

    const ping = async () => {
      try {
        await api.health();
        if (!cancelled) {
          setApiReady(true);
        }
      } catch {
        // keep waiting
      }
    };

    // immediate try, then interval until success
    ping();
    const h = setInterval(() => {
      if (!apiReady) ping();
    }, 2000);

    return () => { cancelled = true; clearInterval(h); };
  }, [apiReady]);

  useEffect(() => {
    // Reset stats if new crawlConfig is detected
    setStats({
      totalEntities: 0,
      avgScore: "0%",
      entityTypes: 0,
      pagesAnalyzed: 0,
    });
    setEntities([]);

    let cancelled = false;
    let first = true;

    const fetchAndUpdate = async () => {
      try {
        if (first) setIsLoading(true);
        if (!apiReady) return; // wait for API warmup
        const data = await api.getResults();
        const arr = Array.isArray(data) ? data : [];
        if (cancelled) return;

        // Only update state if values actually changed
        setEntities(prev => {
          const prevLen = prev?.length || 0;
          if (prevLen === arr.length) return prev; // avoid re-render spam
          return arr;
        });

        const avgScoreNum = arr.length > 0 ? arr.reduce((sum, e) => sum + (e.score || 0), 0) / arr.length : 0;
        setStats(prev => {
          const next = {
            totalEntities: arr.length,
            avgScore: `${(avgScoreNum * 100).toFixed(1)}%`,
            entityTypes: new Set(arr.map((e) => e.type)).size,
            pagesAnalyzed:
              Number(lastRun?.pages_scanned ?? 0) || Number(crawlConfig?.max_pages ?? 0) || 0,
          };
          if (
            prev.totalEntities === next.totalEntities &&
            prev.avgScore === next.avgScore &&
            prev.entityTypes === next.entityTypes &&
            prev.pagesAnalyzed === next.pagesAnalyzed
          ) {
            return prev;
          }
          return next;
        });
      } catch (error) {
        if (!cancelled && apiReady) {
          console.error("Error fetching results:", error);
          // avoid noisy toasts while API is warming up
          toast.error("Failed to load results.");
        }
      } finally {
        if (first) setIsLoading(false);
        first = false;
      }
    };

    // Kick once immediately, then poll
    fetchAndUpdate();
    const handle = setInterval(fetchAndUpdate, 1500);
    return () => {
      cancelled = true;
      clearInterval(handle);
    };
  }, [crawlConfig, lastRun, apiReady]);

  // Filtered view matches table + export
  const filtered: Record<string, any>[] = useMemo(() => {
    if (!entities || entities.length === 0) return [];
    return entities.filter((e) => {
      return Object.values(e).some(
        v => (typeof v === "string" ? v.toLowerCase().includes(searchQuery.toLowerCase()) : false)
      );
    });
  }, [entities, searchQuery]);

  const exportEntities = (format: "csv" | "json" = "csv") => {
    if (!filtered || filtered.length === 0) {
      toast.info("No entities to export.");
      return;
    }
    const domainSafe = (domain || "domain")
      .replace(/^https?:\/\//, "")
      .replace(/[^\w.-]+/g, "_");
    const ts = new Date().toISOString().replace(/[:.]/g, "-");
    if (format === "json") {
      const jsonBlob = new Blob([JSON.stringify(filtered, null, 2)], {
        type: "application/json",
      });
      const jsonName = `entities_${domainSafe}_${ts}.json`;
      const url = URL.createObjectURL(jsonBlob);
      const a = document.createElement("a");
      a.href = url;
      a.download = jsonName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      toast.success(`Exported ${filtered.length} entities as JSON`);
      return;
    }
    // CSV: auto-detect all keys
    let keySet = new Set<string>();
    filtered.forEach(obj => {
      Object.keys(obj).forEach(k => keySet.add(k));
    });
    const allKeys = Array.from(keySet);
    const header = allKeys;
    const rows = filtered.map((e) => header.map(k => {
      const obj = e as Record<string, any>;
      if (k === "score") return `${((obj[k] ?? 0) * 100).toFixed(1)}%`;
      return obj[k] ?? "";
    }));
    const esc = (v: string) => {
      const s = String(v ?? "");
      return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    };
    const csv = [header, ...rows].map((r) => r.map(esc).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const filename = `entities_${domainSafe}_${ts}.csv`;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    toast.success(`Exported ${filtered.length} entities as CSV`);
  };

  return (
    <div className="p-8 animate-fade-in">
      <h1 className="text-4xl font-bold mb-3 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
        Extraction Results
      </h1>
      <p className="text-muted-foreground">
        Domain: <span className="font-medium">{domain}</span>
      </p>

      <div className="grid md:grid-cols-4 gap-4 mt-6 mb-8">
        <StatCard title="Entities Found" value={stats.totalEntities} icon={Users} glowColor="cyan" />
        <StatCard title="Average Confidence" value={stats.avgScore} icon={Award} glowColor="purple" />
        <StatCard title="Entity Types" value={stats.entityTypes} icon={BarChart3} glowColor="blue" />
        <StatCard title="Pages Analyzed" value={stats.pagesAnalyzed} icon={FileText} glowColor="blue" />
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
        </div>
      ) : (
        <Card className="glass-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <Search className="w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search entities..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <Button
              variant="outline"
              className="ml-auto"
              onClick={() => exportEntities("json")} // switch to "json" if you prefer JSON
            >
              <Download className="w-4 h-4 mr-2" /> Export
            </Button>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                {filtered.length > 0 && Object.keys(filtered[0]).map((key) => (
                  <TableHead key={key}>{key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, " ")}</TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((e, i) => (
                <TableRow key={i}>
                  {Object.keys(e).map((key) => (
                    <TableCell key={key} className={key === "snippet" ? "max-w-md truncate text-muted-foreground" : ""}>
                      {key === "score"
                        ? `${((e[key] ?? 0) * 100).toFixed(1)}%`
                        : key === "url" || key === "context_url"
                          ? (<a href={e[key]} target="_blank" className="text-primary underline" rel="noreferrer">View</a>)
                          : e[key] ?? ""}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}
    </div>
  );
};

export default Results;
