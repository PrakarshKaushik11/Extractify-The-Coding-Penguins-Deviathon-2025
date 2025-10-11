import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowRight, Zap, Database, Brain } from "lucide-react";
import heroBg from "@/assets/hero-bg.png";

const Home = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `url(${heroBg})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/50 to-background" />
        
        <div className="relative container mx-auto px-6 py-32">
          <div className="max-w-4xl mx-auto text-center animate-fade-in">
            <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent leading-tight">
              🐧 The Coding Penguins
            </h1>
            <h2 className="text-2xl md:text-3xl font-semibold mb-6 text-foreground/90">
              Automated Entity Extraction System
            </h2>
            <p className="text-xl text-muted-foreground mb-12 max-w-2xl mx-auto">
              Crawl → Extract → Understand any domain with local AI. 
              Transform unstructured web data into intelligent knowledge, fully offline.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/crawl">
                <Button size="lg" className="gradient-cyan-purple text-white font-semibold px-8 glow-cyan">
                  Start Extraction
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </Link>
              <Link to="/results">
                <Button size="lg" variant="outline" className="border-primary/50 hover:bg-primary/10">
                  View Results
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 container mx-auto px-6">
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <div className="glass-card rounded-xl p-8 text-center hover:glow-cyan transition-all duration-300">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/20 flex items-center justify-center">
              <Zap className="w-8 h-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Lightning Fast</h3>
            <p className="text-muted-foreground">
              Crawl hundreds of pages per minute with intelligent depth control and parallel processing.
            </p>
          </div>

          <div className="glass-card rounded-xl p-8 text-center hover:glow-purple transition-all duration-300">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-secondary/20 flex items-center justify-center">
              <Brain className="w-8 h-8 text-secondary" />
            </div>
            <h3 className="text-xl font-semibold mb-3">AI-Powered</h3>
            <p className="text-muted-foreground">
              Advanced NLP models extract entities with context understanding and confidence scoring.
            </p>
          </div>

          <div className="glass-card rounded-xl p-8 text-center hover:glow-blue transition-all duration-300">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-accent/20 flex items-center justify-center">
              <Database className="w-8 h-8 text-accent" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Structured Data</h3>
            <p className="text-muted-foreground">
              Export clean, organized entity data ready for analysis, visualization, or integration.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/50 py-8">
        <div className="container mx-auto px-6 text-center text-muted-foreground">
          <p>Developed by <span className="text-primary font-semibold">The Coding Penguins</span></p>
          <p className="text-sm mt-2">Turning unstructured web data into intelligent knowledge</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;
