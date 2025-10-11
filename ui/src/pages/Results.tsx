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
  const [entities, setEntities] = useState<Entity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState({
    totalEntities: 0,
    avgScore: "0%",
    entityTypes: 0,
    pagesAnalyzed: 0,
  });

  const crawlConfig = useMemo(() => {
    try { return JSON.parse(localStorage.getItem("penguin:crawlConfig") || "{}"); }
    catch { return {}; }
  }, []);
  const lastRun = useMemo(() => {
    try { return JSON.parse(localStorage.getItem("penguin:lastRunStats") || "{}"); }
    catch { return {}; }
  }, []);
  const domain = crawlConfig?.domain || lastRun?.domain || "—";

  useEffect(() => {
    const fetchResults = async () => {
      try {
        setIsLoading(true);
        const data = await api.getResults();

        const formatted: Entity[] = (Array.isArray(data) ? data : []).map((d: any) => ({
          name: d.name,
          type: d.type || "Unknown",
          url: d.url || d.context_url || "#",
          snippet: d.snippet || "",
          score: d.score || d.confidence || 0,
        }));

        const avgScore =
          formatted.length > 0
            ? formatted.reduce((sum, e) => sum + (e.score || 0), 0) / formatted.length
            : 0;

        setEntities(formatted);
        setStats({
          totalEntities: formatted.length,
          avgScore: `${(avgScore * 100).toFixed(1)}%`,
          entityTypes: new Set(formatted.map((e) => e.type)).size,
          pagesAnalyzed:
            Number(lastRun?.pages_scanned ?? 0) || Number(crawlConfig?.max_pages ?? 0) || 0,
        });

        if (formatted.length === 0) {
          toast.info("No entities found for this run.");
        }
      } catch (error) {
        console.error("Error fetching results:", error);
        toast.error("Failed to load results.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, [crawlConfig, lastRun]);

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
            <Button variant="outline" className="ml-auto" onClick={() => toast.info("Export coming soon")}>
              <Download className="w-4 h-4 mr-2" /> Export
            </Button>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Confidence</TableHead>
                <TableHead>Snippet</TableHead>
                <TableHead>Source</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {entities
                .filter((e) => e.name.toLowerCase().includes(searchQuery.toLowerCase()))
                .map((e, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-medium">{e.name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{e.type}</Badge>
                    </TableCell>
                    <TableCell>{(e.score * 100).toFixed(1)}%</TableCell>
                    <TableCell className="max-w-md truncate text-muted-foreground">
                      {e.snippet}
                    </TableCell>
                    <TableCell>
                      <a href={e.url} target="_blank" className="text-primary underline" rel="noreferrer">
                        View
                      </a>
                    </TableCell>
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
