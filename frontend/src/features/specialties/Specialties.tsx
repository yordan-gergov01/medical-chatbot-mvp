import {
  Heart, Brain, Bone, Droplets, Stethoscope, Activity,
  Wind, Ear, Baby, Eye, CircleDot, SmilePlus, HelpCircle,
} from "lucide-react";
import useFadeIn from "@/hooks/useFadeIn";
import { useSpecialties } from "@/hooks/useApi";

const ICON_MAP: Record<string, React.ElementType> = {
  cardiology: Heart,
  neurology: Brain,
  orthopedics: Bone,
  dermatology: Droplets,
  gastroenterology: Stethoscope,
  endocrinology: Activity,
  pulmonology: Wind,
  ent: Ear,
  gynecology: Baby,
  ophthalmology: Eye,
  urology: CircleDot,
  psychiatry: SmilePlus,
};

const Specialties = () => {
  const ref = useFadeIn();
  const { data: specialties, loading, error } = useSpecialties();

  return (
    <section id="specialties" className="py-20 bg-secondary/30" ref={ref}>
      <div className="container mx-auto px-4 section-fade-in">
        <h2 className="text-3xl sm:text-4xl font-display font-bold text-center mb-4">
          Специалности
        </h2>
        <p className="text-muted-foreground text-center max-w-xl mx-auto mb-12">
          Комплексна медицинска грижа чрез {specialties?.length ?? 12} специализирани направления.
        </p>

        {loading && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {Array.from({ length: 12 }).map((_, i) => (
              <div key={i} className="bg-card rounded-lg p-5 animate-pulse">
                <div className="w-12 h-12 mx-auto rounded-full bg-muted mb-3" />
                <div className="h-3 bg-muted rounded w-2/3 mx-auto mb-2" />
                <div className="h-2 bg-muted rounded w-1/2 mx-auto" />
              </div>
            ))}
          </div>
        )}

        {error && (
          <p className="text-center text-destructive">
            Неуспешно зареждане на специалности.
          </p>
        )}

        {specialties && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {specialties.map((s) => {
              const Icon = ICON_MAP[s.id] ?? HelpCircle;
              return (
                <div
                  key={s.id}
                  className="bg-card rounded-lg p-5 text-center hover:shadow-md transition-shadow group cursor-default"
                  title={s.symptoms.slice(0, 4).join(", ")}
                >
                  <div className="w-12 h-12 mx-auto rounded-full bg-primary/10 flex items-center justify-center mb-3 group-hover:bg-primary/20 transition-colors">
                    <Icon size={22} className="text-primary" />
                  </div>
                  <h3 className="font-semibold text-sm mb-1">{s.name}</h3>
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {s.description}
                  </p>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
};

export default Specialties;