import { MapPin, Phone, Clock } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import useFadeIn from "@/hooks/useFadeIn";

const items = [
  { icon: MapPin, label: "Address", value: "bul. Vasil Levski 47, Sofia" },
  { icon: Phone, label: "Phone", value: "02 800 12 34" },
  { icon: Clock, label: "Working Hours", value: "Mon–Fri 08:00–19:00\nSat 09:00–14:00" },
];

const About = () => {
  const ref = useFadeIn();

  return (
    <section id="about" className="py-20 bg-secondary/30" ref={ref}>
      <div className="container mx-auto px-4 section-fade-in">
        <h2 className="text-3xl sm:text-4xl font-display font-bold text-center mb-4">About Our Center</h2>
        <p className="text-muted-foreground text-center max-w-2xl mx-auto mb-12">
          Founded in 2010, Zdrave Plus Medical Center has been providing high-quality healthcare services in Sofia. Our team of experienced doctors is committed to delivering personalized, compassionate care using the latest medical technologies.
        </p>
        <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {items.map((item) => (
            <Card key={item.label} className="hover:shadow-lg transition-shadow">
              <CardContent className="flex flex-col items-center text-center pt-6">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <item.icon size={22} className="text-primary" />
                </div>
                <h3 className="font-semibold mb-1">{item.label}</h3>
                <p className="text-sm text-muted-foreground whitespace-pre-line">{item.value}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default About;
