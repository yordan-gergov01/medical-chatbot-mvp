import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import useFadeIn from "@/hooks/useFadeIn";

// Since the FAQs are fixed for this demo project, they are hardcoded here, there is no need for an API endpoint for them
const faqs = [
  { q: "Трябва ли ми направление за специалист?", a: "Не е задължително. Можете да запишете час директно при специалист без направление срещу заплащане. Ако имате направление от личен лекар и специалистът работи с НЗОК, прегледът е безплатен или с минимална доплата." },
  { q: "Колко струва прегледът?", a: "Цените варират от 35 до 120 евро в зависимост от специалиста. Допълнителните изследвания (ЕКГ, ехография, ЕЕГ) се заплащат отделно. Точната цена е посочена в профила на всеки лекар." },
  { q: "Мога ли да отменя или преместя часа си?", a: "Да. Молим да го направите поне 24 часа предварително. Свържете се с нас по телефон или чрез чатбота. При неявяване без предупреждение може да бъдете таксувани с 10 евро." },
  { q: "Колко трае един преглед?", a: "Стандартен преглед е 20-50 минути в зависимост от специалиста. При първо посещение е препоръчително да дойдете 10 минути по-рано за регистрация." },
  { q: "Мога ли да получа резултатите си онлайн?", a: "Да. Резултатите от изследвания се изпращат на имейл в рамките на 24-48 часа след готовността им." },
  { q: "Правите ли изследвания на кръв и урина?", a: "Да, разполагаме с клинична лаборатория. Вземането на кръв е от 07:30 до 10:00 без предварителен час (на гладно за повечето изследвания)." },
  { q: "Мога ли да дойда без предварителен час?", a: "Не препоръчваме. Всички прегледи са по предварително записване. При неотложни случаи се свържете по телефон и ще се опитаме да ви наредим в същия ден." },
];

const FAQ = () => {
  const ref = useFadeIn();

  return (
    <section id="faq" className="py-20" ref={ref}>
      <div className="container mx-auto px-4 max-w-3xl section-fade-in">
        <h2 className="text-3xl sm:text-4xl font-display font-bold text-center mb-12">Често задавани въпроси</h2>
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
