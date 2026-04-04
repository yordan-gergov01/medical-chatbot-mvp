import { useState } from "react";
import { Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";

const navLinks = [
  { label: "За нас", href: "#about" },
  { label: "Специалисти", href: "#specialists" },
  { label: "Специалности", href: "#specialties" },
  { label: "FAQ", href: "#faq" },
  { label: "Контакти", href: "#contact" },
];

const Navbar = () => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const scrollTo = (href: string) => {
    setMobileOpen(false);
    const el = document.querySelector(href);
    el?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-card/95 backdrop-blur-md border-b border-border">
      <div className="container mx-auto flex items-center justify-between h-16 px-2">
        <a href="#" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })} className="flex items-center gap-2 text-xl font-display font-bold text-primary">
          🏥 Здраве Плюс
        </a>

        {/* Desktop */}
        <div className="hidden md:flex items-center gap-6">
          {navLinks.map((l) => (
            <button key={l.href} onClick={() => scrollTo(l.href)} className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
              {l.label}
            </button>
          ))}
          <Button size="sm" onClick={() => scrollTo("#specialists")}>
            Запази час
          </Button>
        </div>

        {/* Mobile toggle */}
        <button className="md:hidden text-foreground" onClick={() => setMobileOpen(!mobileOpen)}>
          {mobileOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden bg-card border-b border-border px-4 pb-4 animate-fade-in-up">
          {navLinks.map((l) => (
            <button key={l.href} onClick={() => scrollTo(l.href)} className="block w-full text-left py-2 text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
              {l.label}
            </button>
          ))}
          <Button size="sm" className="mt-2 w-full" onClick={() => scrollTo("#specialists")}>
            Запази час
          </Button>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
