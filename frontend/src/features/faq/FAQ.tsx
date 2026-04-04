import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import useFadeIn from "@/hooks/useFadeIn";

const faqs = [
  { q: "What should I bring to my appointment?", a: "Please bring your ID card, health insurance booklet (if applicable), any recent test results, and a list of current medications." },
  { q: "Which doctors accept NHIF?", a: "Dr. Ivan Petrov (Cardiologist), Dr. Stefan Dimitrov (Neurologist), Dr. Maria Georgieva (Orthopedist), and Dr. Anna Todorova (Gastroenterologist) accept NHIF." },
  { q: "How do I book an appointment?", a: "You can book online through our AI assistant, call us at 02 800 12 34, or visit us at bul. Vasil Levski 47, Sofia." },
  { q: "Can I cancel or reschedule?", a: "Yes, you can cancel or reschedule up to 24 hours before your appointment without any fees. Contact us by phone or use our chat assistant." },
  { q: "Is there parking available?", a: "Yes, we have a private parking lot for patients with 30 spaces available on a first-come, first-served basis." },
  { q: "Do you offer online consultations?", a: "Yes, many of our specialists offer video consultations. Ask our AI assistant or call to check availability for your preferred doctor." },
];

const FAQ = () => {
  const ref = useFadeIn();

  return (
    <section id="faq" className="py-20" ref={ref}>
      <div className="container mx-auto px-4 max-w-3xl section-fade-in">
        <h2 className="text-3xl sm:text-4xl font-display font-bold text-center mb-12">Frequently Asked Questions</h2>
        <Accordion type="single" collapsible className="space-y-2">
          {faqs.map((faq, i) => (
            <AccordionItem key={i} value={`item-${i}`} className="bg-card rounded-lg px-4 border">
              <AccordionTrigger className="text-left font-medium">{faq.q}</AccordionTrigger>
              <AccordionContent className="text-muted-foreground">{faq.a}</AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  );
};

export default FAQ;
