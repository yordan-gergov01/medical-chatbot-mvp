import { Star } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import useFadeIn from "@/hooks/useFadeIn";
import { useDoctors } from "@/hooks/useApi";
import { getInitials } from "@/lib/utils";

const Specialists = () => {
  const ref = useFadeIn();
  const { data: doctors, loading, error } = useDoctors();

  return (
    <section id="specialists" className="py-20" ref={ref}>
      <div className="container mx-auto px-4 section-fade-in">
        <h2 className="text-3xl sm:text-4xl font-display font-bold text-center mb-4">
          Нашите специалисти
        </h2>
        <p className="text-muted-foreground text-center max-w-xl mx-auto mb-12">
          Запознайте се с нашия екип от опитни професионалисти, посветени на вашето здраве.  
        </p>

        {loading && (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {Array.from({ length: 8 }).map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="pt-6 flex flex-col items-center">
                  <div className="w-16 h-16 rounded-full bg-muted mb-4" />
                  <div className="h-4 bg-muted rounded w-3/4 mb-2" />
                  <div className="h-3 bg-muted rounded w-1/2 mb-4" />
                  <div className="h-8 bg-muted rounded w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {error && (
          <p className="text-center text-destructive">
            Неуспешно зареждане на специалисти. Моля опитайте отново по-късно!
          </p>
        )}

        {doctors && (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {doctors.map((doc) => (
              <Card
                key={doc.id}
                className="group hover:shadow-xl hover:-translate-y-1 transition-all duration-300"
              >
                <CardContent className="pt-6 flex flex-col items-center text-center">
                  <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center text-primary font-display font-bold text-xl mb-4">
                    {getInitials(doc.name)}
                  </div>
                  <h3 className="font-semibold text-lg">{doc.name}</h3>
                  {doc.academic_title && (
                    <span className="text-xs text-muted-foreground">{doc.academic_title}</span>
                  )}
                  <p className="text-sm text-muted-foreground mb-2">{doc.specialty}</p>
                  <div className="flex items-center gap-1 text-sm text-muted-foreground mb-2">
                    <Star size={14} className="fill-yellow-500 text-yellow-500" />
                    <span className="font-medium text-foreground">{doc.rating}</span>
                    <span>· {doc.years_experience} години опит</span>
                  </div>
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-lg font-bold text-primary">{doc.price} EUR</span>
                    {doc.accepts_nhif && (
                      <Badge className="bg-online text-accent-foreground text-xs">НЗОК</Badge>
                    )}
                  </div>
                  <Button size="sm" className="w-full">
                    Запази
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </section>
  );
};

export default Specialists;