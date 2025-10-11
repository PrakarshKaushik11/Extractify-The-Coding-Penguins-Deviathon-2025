import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Cpu, HardDrive, Zap, CheckCircle2 } from "lucide-react";

const SystemInfo = () => {
  return (
    <div className="container mx-auto px-6 py-12 max-w-4xl">
      <div className="mb-8 animate-fade-in">
        <h1 className="text-4xl font-bold mb-3 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
          System Information
        </h1>
        <p className="text-muted-foreground">
          Runtime environment and AI model configuration
        </p>
      </div>

      <div className="space-y-6">
        <Card className="glass-card p-6 animate-slide-in">
          <div className="flex items-center gap-3 mb-4">
            <Cpu className="w-6 h-6 text-primary" />
            <h2 className="text-xl font-semibold">Runtime Device</h2>
            <Badge className="bg-primary/20 text-primary border-primary/50">
              <CheckCircle2 className="w-3 h-3 mr-1" />
              Active
            </Badge>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Processing Unit</span>
              <span className="font-semibold text-primary">GPU (CUDA 11.8)</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Memory Available</span>
              <span className="font-semibold">16 GB VRAM</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Compute Capability</span>
              <span className="font-semibold">8.6 (RTX 3080)</span>
            </div>
          </div>
        </Card>

        <Card className="glass-card p-6 animate-slide-in" style={{ animationDelay: '0.1s' }}>
          <div className="flex items-center gap-3 mb-4">
            <HardDrive className="w-6 h-6 text-secondary" />
            <h2 className="text-xl font-semibold">Embedding Model</h2>
            <Badge className="bg-secondary/20 text-secondary border-secondary/50">
              Loaded
            </Badge>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Model Name</span>
              <span className="font-semibold">sentence-transformers/all-MiniLM-L6-v2</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Embedding Dimension</span>
              <span className="font-semibold">384</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Max Sequence Length</span>
              <span className="font-semibold">256 tokens</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Framework</span>
              <span className="font-semibold">PyTorch 2.0.1</span>
            </div>
          </div>
        </Card>

        <Card className="glass-card p-6 animate-slide-in" style={{ animationDelay: '0.2s' }}>
          <div className="flex items-center gap-3 mb-4">
            <Zap className="w-6 h-6 text-accent" />
            <h2 className="text-xl font-semibold">Zero-Shot Classifier</h2>
            <Badge className="bg-accent/20 text-accent border-accent/50">
              Ready
            </Badge>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Model Name</span>
              <span className="font-semibold">facebook/bart-large-mnli</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Architecture</span>
              <span className="font-semibold">BART (Bidirectional Auto-Regressive Transformer)</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Parameters</span>
              <span className="font-semibold">406M</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Training Dataset</span>
              <span className="font-semibold">MultiNLI</span>
            </div>
          </div>
        </Card>

        <Card className="glass-card p-6 bg-muted/30 animate-slide-in" style={{ animationDelay: '0.3s' }}>
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-primary" />
            Initialization Log
          </h3>
          <div className="font-mono text-sm space-y-1 max-h-48 overflow-y-auto">
            <div className="text-primary">✓ GPU device detected: NVIDIA GeForce RTX 3080</div>
            <div className="text-primary">✓ CUDA 11.8 initialized successfully</div>
            <div className="text-secondary">✓ Loading SentenceTransformer model...</div>
            <div className="text-secondary">✓ Model loaded in 2.3 seconds</div>
            <div className="text-accent">✓ Loading Zero-shot classifier...</div>
            <div className="text-accent">✓ Classifier loaded in 3.7 seconds</div>
            <div className="text-muted-foreground">→ System ready for entity extraction</div>
            <div className="text-primary font-bold">✓ All models initialized successfully</div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default SystemInfo;
