"use client";

import AnimatedText from "@/components/AnimatedText";
import FrontPage from "@/components/FrontPage";
import { motion } from "framer-motion";
import { useState, useEffect } from "react";

export default function Home() {
  const [screen, setScreen] = useState(0);

  useEffect(() => {
    const timer1 = setTimeout(() => setScreen(1), 4000); // Show blue screen after 4s
    const timer2 = setTimeout(() => setScreen(2), 4300); // Show white screen after 6s
    const timer3 = setTimeout(() => setScreen(3), 4400); // Show FrontPage after 8s

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, []);

  return (
    <div className="h-screen w-screen">
      {screen === 0 && <AnimatedText />}
      {screen === 1 && <motion.div
            initial={{ y: "-100%" }}
            animate={{ y: "0%" }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="absolute inset-0 bg-[#361899]"
          />

}
      {screen === 2 && <motion.div
            initial={{ y: "-100%" }}
            animate={{ y: "0%" }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="absolute inset-0 bg-white"
          />

        }
      {screen === 3 && <FrontPage />}
    </div>
  );
}
