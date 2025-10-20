import { useEffect, useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Brain, CheckCircle2, Loader2, StopCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import StatCard from "@/components/StatCard";
import { Database, Target, Clock } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";

const Extraction = () => {
  // Clear state on unmount to prevent stale data
  useEffect(() => {
    return () => {
      setEntitiesFound(0);
      setAvgScore(0);
      setStartTime(null);
      setEndTime(null);
      setLogMessages([]);
      setProgress(0);
      setIsRunning(false);
    };
  }, []);
  const navigate = useNavigate();
  const [progress, setProgress] = useState(0);
  const [isRunning, setIsRunning] = useState(true);
  const [entitiesFound, setEntitiesFound] = useState(0);
  const [avgScore, setAvgScore] = useState(0);
  const [logMessages, setLogMessages] = useState<string[]>([]);
  const [startTime, setStartTime] = useState<number | null>(null);
  const [endTime, setEndTime] = useState<number | null>(null);

  // Read persisted config + last run stats
    const crawlConfig = useMemo(() => {
      try { return JSON.parse(localStorage.getItem("penguin:crawlConfig") || "{}"); }
      catch { return {}; }
    }, [localStorage.getItem("penguin:crawlConfig")]);
    const lastRun = useMemo(() => {
      try { return JSON.parse(localStorage.getItem("penguin:lastRunStats") || "{}"); }
      catch { return {}; }
    }, [localStorage.getItem("penguin:lastRunStats")]);

  // Use max_pages from config, fallback to pages_scanned from lastRun, fallback to 1
  const totalPages = Number(crawlConfig?.max_pages) || Number(lastRun?.pages_scanned) || 1;
  const domain = (crawlConfig?.domain || lastRun?.domain || "—") as string;

  useEffect(() => {
  // Reset entity count, stats, and timer at start of new crawl
  setEntitiesFound(0);
  setAvgScore(0);
  setStartTime(Date.now());
  setEndTime(null);
  localStorage.setItem("penguin:lastRunStats", "{}");
  localStorage.setItem("penguin:crawlDone", "0");

    // If the previous step already finished, don't fake-run forever.
    const alreadyDone = localStorage.getItem("penguin:crawlDone") === "1";

    const checkResults = async () => {
      try {
        const results = await api.getResults();
        const count = Array.isArray(results) ? results.length : 0;

        // Update metrics
        setEntitiesFound(count);
        if (count > 0) {
          const totalScore = results.reduce((sum: number, entity: any) => {
            return sum + (entity.score || entity.confidence || 0);
          }, 0);
          setAvgScore(totalScore / count);
        }

        // Stop running regardless of count (so 0-entity runs don't hang)
        if (alreadyDone) {
          setProgress(100);
          setIsRunning(false);
          setEndTime(Date.now());
          setLogMessages(prev => [...prev, count > 0
            ? "✅ Extraction complete! Entities have been processed."
            : "ℹ️ Extraction finished. No entities were found for the given settings."
          ]);

          // Go to results after a short moment
          setTimeout(() => navigate("/results", { replace: true }), 1200);
        }
      } catch (error) {
        console.error("Error fetching results:", error);
        toast.error("Failed to read results.");
        setIsRunning(false);
      }
    };

    if (logMessages.length === 0) {
      setLogMessages([
        "🔍 Starting entity extraction process...",
        "📊 Initializing NLP pipeline...",
        "🧠 Loading language models...",
      ]);
    }

    // Progress & polling
    const interval = setInterval(() => {
      setProgress(prev => (prev >= 95 ? 95 : prev + 2));
      checkResults();
    }, 2000);

    // Kick one immediate check
    checkResults();

    return () => clearInterval(interval);
  }, [navigate, logMessages.length, totalPages]);

  const handleEndNow = () => {
    // Let the user jump to results at any time
    setIsRunning(false);
    setProgress(100);
    navigate("/results");
  };

  return (
    <div className="container mx-auto px-6 py-12 max-w-6xl">
      <div className="mb-8 animate-fade-in">
        <h1 className="text-4xl font-bold mb-3 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
          AI Entity Extraction
        </h1>
        <p className="text-muted-foreground">
          Local AI models are processing your crawled data to extract structured entities.
        </p>
        <p className="text-muted-foreground">Website crawled: {domain || "—"}</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <StatCard
          title="Entities Found"
          value={entitiesFound}
          icon={Database}
          trend="Real-time updates"
          glowColor="cyan"
        />
        <StatCard
          title="Average Confidence"
          value={`${(avgScore * 100).toFixed(1)}%`}
          icon={Target}
          trend="AI certainty score"
          glowColor="purple"
        />
        <StatCard
          title="Processing Time"
          value={
            startTime && endTime
              ? `${((endTime - startTime) / 1000).toFixed(1)}s`
              : isRunning && startTime
                ? `${(((Date.now() - startTime) / 1000).toFixed(1))}s`
                : "0.0s"
          }
          icon={Clock}
          trend="Actual duration"
          glowColor="blue"
        />
      </div>

      <Card className="glass-card p-8 mb-6 animate-slide-in">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Brain className={`w-6 h-6 text-primary ${isRunning ? "animate-pulse-glow" : ""}`} />
            <h2 className="text-2xl font-semibold">
              {isRunning ? "Processing..." : "Extraction Finished"}
            </h2>
          </div>
          {isRunning ? (
            <Loader2 className="w-6 h-6 text-primary animate-spin" />
          ) : (
            <CheckCircle2 className="w-6 h-6 text-primary" />
          )}
        </div>

        <Progress value={progress} className="mb-4 h-3" />

        <p className="text-muted-foreground mb-6">
          {isRunning
            ? `Analyzing page ${Math.max(1, Math.round((progress / 100) * totalPages))}/${totalPages} using AI models...`
            : "All entities have been extracted and scored (if any were found)."}
        </p>

        <div className="glass-card bg-muted/30 p-4 rounded-lg mb-6 max-h-64 overflow-y-auto font-mono text-sm">
          <div className="space-y-1">
            {logMessages.map((msg, i) => (
              <div key={i}>{msg}</div>
            ))}
          </div>
        </div>

        <div className="flex gap-3">
          <Button variant="secondary" className="rounded-2xl" onClick={handleEndNow}>
            <StopCircle className="mr-2 h-4 w-4" />
            End Extraction
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default Extraction;
