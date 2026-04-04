import { MapPin, Phone, Mail, Clock } from "lucide-react";
import useFadeIn from "@/hooks/useFadeIn";

const Contact = () => {
  const ref = useFadeIn();

  return (
    <section id="contact" className="py-20 bg-secondary/30" ref={ref}>
      <div className="container mx-auto px-4 section-fade-in">
        <h2 className="text-3xl sm:text-4xl font-display font-bold text-center mb-12">Contact Us</h2>
        <div className="grid md:grid-cols-2 gap-10 max-w-5xl mx-auto">
          <div className="space-y-6">
            {[
              { icon: MapPin, label: "Address", value: "bul. Vasil Levski 47, Sofia, Bulgaria" },
              { icon: Phone, label: "Phone", value: "02 800 12 34" },
              { icon: Mail, label: "Email", value: "info@zdraveplus.bg" },
              { icon: Clock, label: "Working Hours", value: "Mon–Fri 08:00–19:00 · Sat 09:00–14:00" },
            ].map((item) => (
              <div key={item.label} className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                  <item.icon size={18} className="text-primary" />
                </div>
                <div>
                  <p className="font-medium text-sm">{item.label}</p>
                  <p className="text-sm text-muted-foreground">{item.value}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="bg-muted rounded-lg flex items-center justify-center min-h-[280px] text-muted-foreground text-sm">
            Google Maps placeholder
          </div>
        </div>
      </div>
    </section>
  );
};

export default Contact;
