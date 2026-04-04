import { Heart, Brain, Bone, Droplets, Stethoscope, Activity, Wind, Ear, Baby, Eye, CircleDot, SmilePlus } from "lucide-react";
import useFadeIn from "@/hooks/useFadeIn";

const specialties = [
  { name: "Cardiology", icon: Heart, desc: "Heart and cardiovascular system" },
  { name: "Neurology", icon: Brain, desc: "Brain and nervous system" },
  { name: "Orthopedics", icon: Bone, desc: "Bones, joints and muscles" },
  { name: "Dermatology", icon: Droplets, desc: "Skin, hair and nail conditions" },
  { name: "Gastroenterology", icon: Stethoscope, desc: "Digestive system disorders" },
  { name: "Endocrinology", icon: Activity, desc: "Hormones and metabolism" },
  { name: "Pulmonology", icon: Wind, desc: "Respiratory and lung health" },
  { name: "ENT", icon: Ear, desc: "Ear, nose and throat" },
  { name: "Gynecology", icon: Baby, desc: "Women's reproductive health" },
  { name: "Ophthalmology", icon: Eye, desc: "Eye care and vision" },
  { name: "Urology", icon: CircleDot, desc: "Urinary tract and kidneys" },
  { name: "Psychiatry", icon: SmilePlus, desc: "Mental health and well-being" },
];

const Specialties = () => {
  const ref = useFadeIn();

  return (
    <section id="specialties" className="py-20 bg-secondary/30" ref={ref}>
      <div className="container mx-auto px-4 section-fade-in">
        <h2 className="text-3xl sm:text-4xl font-display font-bold text-center mb-4">Our Specialties</h2>
        <p className="text-muted-foreground text-center max-w-xl mx-auto mb-12">
          Comprehensive medical care across 12 specialized departments.
        </p>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {specialties.map((s) => (
            <div key={s.name} className="bg-card rounded-lg p-5 text-center hover:shadow-md transition-shadow group cursor-default">
              <div className="w-12 h-12 mx-auto rounded-full bg-primary/10 flex items-center justify-center mb-3 group-hover:bg-primary/20 transition-colors">
                <s.icon size={22} className="text-primary" />
              </div>
              <h3 className="font-semibold text-sm mb-1">{s.name}</h3>
              <p className="text-xs text-muted-foreground">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Specialties;
