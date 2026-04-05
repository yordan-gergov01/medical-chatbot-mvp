import { Button } from "@/components/ui/button";
import { MessageCircle } from "lucide-react";

interface HeroProps {
  onOpenChat: () => void;
}

const Hero = ({ onOpenChat }: HeroProps) => {
  return (
    <section className="relative min-h-[85vh] flex items-center justify-center bg-gradient-to-br from-primary/5 via-background to-accent/5 overflow-hidden">
      {/* Decorative circles */}
      <div className="absolute top-20 right-10 w-72 h-72 rounded-full bg-primary/5 blur-3xl" />
      <div className="absolute bottom-10 left-10 w-96 h-96 rounded-full bg-accent/5 blur-3xl" />

      <div className="container mx-auto px-4 text-center relative z-10">
        <div className="inline-block mb-6 px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium animate-fade-in-up">
          Повече от 10 000+ пациенти ни се доверяват от 2010 г.
        </div>
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-display font-bold text-foreground mb-6 animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
          Здраве Плюс
        </h1>
        <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
          Вашето здраве е наш приоритет. Експертна медицинска помощ в сърцето на София с екип от над 20 опитни специалисти.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up" style={{ animationDelay: "0.3s" }}>
          <Button size="lg" onClick={() => document.querySelector("#specialists")?.scrollIntoView({ behavior: "smooth" })}>
            Запази среща
          </Button>
          <Button size="lg" variant="outline" onClick={onOpenChat} className="gap-2">
            <MessageCircle size={18} />
            Попитай нашия AI асистент
          </Button>
        </div>
      </div>
    </section>
  );
};

export default Hero;
