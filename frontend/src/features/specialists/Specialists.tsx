import { Star } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import useFadeIn from "@/hooks/useFadeIn";

const doctors = [
  { name: "Dr. Ivan Petrov", specialty: "Cardiologist", years: 15, price: 100, nhif: true, rating: 4.7, initials: "ИП" },
  { name: "Dr. Elena Nikolova", specialty: "Neurologist", years: 22, price: 120, nhif: false, rating: 4.9, initials: "ЕН" },
  { name: "Dr. Stefan Dimitrov", specialty: "Neurologist", years: 11, price: 90, nhif: true, rating: 4.6, initials: "СД" },
  { name: "Dr. Maria Georgieva", specialty: "Orthopedist", years: 18, price: 110, nhif: true, rating: 4.8, initials: "МГ" },
  { name: "Dr. Petar Ivanov", specialty: "Dermatologist", years: 9, price: 85, nhif: false, rating: 4.5, initials: "ПИ" },
  { name: "Dr. Anna Todorova", specialty: "Gastroenterologist", years: 14, price: 95, nhif: true, rating: 4.7, initials: "АТ" },
  { name: "Dr. Georgi Stoyanov", specialty: "Endocrinologist", years: 20, price: 105, nhif: false, rating: 4.8, initials: "ГС" },
];

const Specialists = () => {
  const ref = useFadeIn();

  return (
    <section id="specialists" className="py-20" ref={ref}>
      <div className="container mx-auto px-4 section-fade-in">
        <h2 className="text-3xl sm:text-4xl font-display font-bold text-center mb-4">Our Specialists</h2>
        <p className="text-muted-foreground text-center max-w-xl mx-auto mb-12">
          Meet our team of experienced medical professionals dedicated to your well-being.
        </p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {doctors.map((doc) => (
            <Card key={doc.name} className="group hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
              <CardContent className="pt-6 flex flex-col items-center text-center">
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center text-primary font-display font-bold text-xl mb-4">
                  {doc.initials}
                </div>
                <h3 className="font-semibold text-lg">{doc.name}</h3>
                <p className="text-sm text-muted-foreground mb-2">{doc.specialty}</p>
                <div className="flex items-center gap-1 text-sm text-muted-foreground mb-2">
                  <Star size={14} className="fill-yellow-500 text-yellow-500" />
                  <span className="font-medium text-foreground">{doc.rating}</span>
                  <span>· {doc.years} years exp.</span>
                </div>
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-lg font-bold text-primary">€{doc.price}</span>
                  {doc.nhif && (
                    <Badge className="bg-online text-accent-foreground text-xs">NHIF</Badge>
                  )}
                </div>
                <Button size="sm" className="w-full">Book</Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Specialists;
