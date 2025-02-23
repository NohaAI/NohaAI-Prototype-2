'use client'
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const words = [
  "AI Interviewer Bot",
  "cutting edge technology",
  "first of its kind",
  "boosts efficiency",
];

export default function AnimatedText() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prevIndex) => (prevIndex + 1) % words.length);
    }, 2000); // Change word every 2 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col justify-center items-center h-screen bg-gradient-to-br from-gray-100 to-white">

      <div className="text-3xl font-medium text-gray-800 flex items-center">
        Noha is a
        <div className="relative h-14 overflow-hidden w-96 pl-2">
          <AnimatePresence mode="sync">
            <motion.div
              key={index}
              initial={{ y: "100%" }}
              animate={{ y: "0%" }}
              exit={{ y: "-100%" }}
              transition={{ duration: 0.7, ease: "easeInOut" }}
              className="absolute mt-2 w-full text-indigo-600 font-bold  whitespace-nowrap"
            >
              {words[index]}
            </motion.div>
          </AnimatePresence>
          <div className="mt-10">
            <img
              src="vector-6.png"
              alt="Mail Icon"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
