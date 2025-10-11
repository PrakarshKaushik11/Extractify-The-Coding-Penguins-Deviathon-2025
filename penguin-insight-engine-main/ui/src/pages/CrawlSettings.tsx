import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Card } from "@/components/ui/card";
import { Loader2, Play, Settings2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { api } from "@/lib/api";

const CrawlSettings = () => {
  const navigate = useNavigate();
  // Start EMPTY as requested (change if you want defaults)
  const [domain, setDomain] = useState("");
  const [keywords, setKeywords] = useState("");
  const [maxPages, setMaxPages] = useState<number[]>([150]);
  const [maxDepth, setMaxDepth] = useState<number[]>([3]);
  const [isLoading, setIsLoading] = useState(false);

  const handleStartCrawl = async () => {
    if (!domain.trim()) {
      toast.error("Please enter a Target Domain before starting.");
      return;
    }

    try {
      setIsLoading(true);

      const payload = {
        domain: domain.trim(),
        keywords: keywords.split(",").map((k) => k.trim()).filter(Boolean),
        max_pages: maxPages[0],
        max_depth: maxDepth[0],
      };

      // Run the full pipeline synchronously (your backend does crawl -> extract)
      const result = await api.crawlAndExtract(payload);

      // Persist config + stats for Extraction/Results screens
      localStorage.setItem("penguin:crawlConfig", JSON.stringify(payload));
      localStorage.setItem("penguin:lastRunStats", JSON.stringify(result?.extract || {}));
      localStorage.setItem("penguin:crawlDone", "1");

      toast.success("Crawl and extraction completed successfully!");
      navigate("/extraction");
    } catch (error) {
      console.error("Crawl error:", error);
      toast.error(error instanceof Error ? error.message : "Failed to start crawl");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setDomain("");
    setKeywords("");
    setMaxPages([150]);
    setMaxDepth([3]);
    toast.info("Settings cleared");
  };

  return (
    <div className="container mx-auto px-6 py-12 max-w-4xl">
      <div className="mb-8 animate-fade-in">
        <h1 className="text-4xl font-bold mb-3 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
          Crawl Configuration
        </h1>
        <p className="text-muted-foreground">
          Set up your web crawling parameters to extract entities from any domain.
        </p>
      </div>

      <Card className="glass-card p-8 mb-6 animate-slide-in">
        <div className="flex items-center gap-3 mb-6">
          <Settings2 className="w-6 h-6 text-primary" />
          <h2 className="text-2xl font-semibold">Crawl Parameters</h2>
        </div>

        <div className="space-y-6">
          <div>
            <Label htmlFor="domain" className="text-base mb-2 block">Target Domain</Label>
            <Input
              id="domain"
              placeholder="https://example.com"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="bg-slate-900/60 border-slate-700"
            />
          </div>

          <div>
            <Label htmlFor="keywords" className="text-base mb-2 block">Keywords (comma-separated)</Label>
            <Input
              id="keywords"
              placeholder="minister, judge, official, professor"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              className="bg-slate-900/60 border-slate-700"
            />
            <p className="text-sm text-muted-foreground mt-2">
              Specify keywords to help identify relevant entities
            </p>
          </div>

          <div>
            <Label className="text-base mb-3 block">Maximum Pages: {maxPages[0]}</Label>
            <Slider
              value={maxPages}
              onValueChange={setMaxPages}
              max={500}
              min={10}
              step={10}
              className="mb-2"
            />
            <p className="text-sm text-muted-foreground">
              Limit the number of pages to crawl (10-500)
            </p>
          </div>

          <div>
            <Label className="text-base mb-3 block">Maximum Depth: {maxDepth[0]}</Label>
            <Slider
              value={maxDepth}
              onValueChange={setMaxDepth}
              max={5}
              min={1}
              step={1}
              className="mb-2"
            />
            <p className="text-sm text-muted-foreground">
              How many levels deep to crawl from the root URL (1-5)
            </p>
          </div>
        </div>
      </Card>

      <div className="flex items-center gap-4">
        <Button onClick={handleStartCrawl} disabled={isLoading} className="rounded-2xl">
          {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
          Start Crawl
        </Button>

        {/* Make Reset visible and non-blended */}
        <Button
          variant="secondary"
          className="rounded-2xl border border-indigo-300/60 bg-indigo-500/10 hover:bg-indigo-500/20"
          onClick={handleReset}
          disabled={isLoading}
        >
          Reset
        </Button>

        <Button variant="ghost" className="rounded-2xl" onClick={() => navigate("/")}>
          Cancel
        </Button>
      </div>
    </div>
  );
};

export default CrawlSettings;
