import { MapPin, Phone, Clock, Mail } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import useFadeIn from "@/hooks/useFadeIn";

const items = [
  { icon: MapPin, label: "Адрес", value: "бул. Васил Левски 47, София 1000" },
  { icon: Phone, label: "Телефон за връзка", value: "02 800 12 34" },
  { icon: Mail, label: "Имейл", value: "info@zdraveplus.bg" },
  { icon: Clock, label: "Работно време", value: "Понеделник - Петък: 08:00 - 19:00\nСъбота: 09:00 - 14:00 (само със запазен час)\nНеделя: затворено" },
];

const About = () => {
  const ref = useFadeIn();

  return (
    <section id="about" className="py-20 bg-secondary/30" ref={ref}>
      <div className="container mx-auto px-4 section-fade-in">
        <h2 className="text-3xl sm:text-4xl font-display font-bold text-center mb-4">За Нас</h2>
        <p className="text-muted-foreground text-center max-w-2xl mx-auto mb-12">
        Основан през 2010г., Медицински център „Здраве Плюс" предоставя висококачествени медицински услуги в София. Нашият екип от опитни лекари се стреми да осигурява индивидуално и грижовно обслужване, като използва най-новите медицински технологии.
        </p>
        <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {items.map((item) => (
            <Card
              key={item.label}
              className={`hover:shadow-lg transition-shadow ${item.label === "Работно време" ? "md:col-span-3" : ""}`}
            >
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