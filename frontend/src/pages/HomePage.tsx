import { useRef } from "react";

import Footer from "@/components/layout/Footer";
import Navbar from "@/components/layout/Navbar";

import About from "@/features/about/About";
import ChatWidget from "@/features/chat/ChatWidget";
import FAQ from "@/features/faq/FAQ";
import Hero from "@/features/home/Hero";
import Specialists from "@/features/specialists/Specialists";
import Specialties from "@/features/specialties/Specialties";


const HomePage = () => {
  const chatRef = useRef<{ open: () => void }>(null);

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="pt-16">
        <Hero onOpenChat={() => chatRef.current?.open()} />
        <About />
        <Specialists />
        <Specialties />
        <FAQ />
      </main>
      <Footer />
      <ChatWidget ref={chatRef} />
    </div>
  );
};

export default HomePage;
