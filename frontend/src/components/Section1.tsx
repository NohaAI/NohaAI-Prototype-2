"use client";

import Link from "next/link";
import React, { useState } from "react";
import { motion } from "framer-motion";
import { Menu, X } from "lucide-react";
import UseCase from "./UseCase";
import Press from "./Press";
import About from "./About";
import Contact from "./Contact";
import Footer from "./Footer";

const Section1: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <div
        className="relative h-screen bg-[#361899] flex flex-col items-center 
                  bg-[url('/curve.png')] bg-no-repeat bg-contain bg-center"
      >
        {/* Navbar */}
        <motion.nav
          initial={{ y: -100, opacity: 0 }} // Start position (above screen)
          animate={{ y: 0, opacity: 1 }} // End position (normal)
          transition={{ duration: 0.6, ease: "easeOut" }} // Smooth transition
          className="w-full max-w-6xl mt-6 px-6 py-3 flex justify-between items-center bg-[#3224A2] rounded-full shadow-lg"
        >
          <div className="text-white text-lg font-semibold px-6">Noha.ai</div>

          <div className="hidden md:flex space-x-8 text-white">
            {/* <a href="#" className="hover:text-gray-300">Home</a> */}
            {/* <a href="#" className="hover:text-gray-300">Product</a> */}
            <a href="#use-case" className="hover:text-gray-300">Use cases</a>
            <a href="#press" className="hover:text-gray-300">Press</a>
            <a href="#contact" className="hover:text-gray-300">Contact</a>
            <a href="#about" className="hover:text-gray-300">About</a>
          </div>

          <div className="hidden md:flex space-x-4 pr-6">
            {/* <button className="px-8 py-3 text-black font-semibold rounded-full bg-gradient-to-r from-[#77FFF1] to-[#0B9284] ">
              Try Noha
            </button> */}
            <Link href={"/book-demo"}>
              <button className="px-5 py-2 border border-[#77FFF1] text-white rounded-full shadow-md">
                Book a demo
              </button>
            </Link>
          </div>

          <button onClick={() => setIsOpen(!isOpen)} className="md:hidden text-white">
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </motion.nav>

        {isOpen && (
          <div className="md:hidden w-full max-w-6xl bg-[#3224A2] rounded-lg mt-3 p-4 text-center">
            <ul className="space-y-4 text-white">
              {/* <li><a href="#" className="hover:text-gray-300">Home</a></li>
              <li><a href="#" className="hover:text-gray-300">Product</a></li> */}
              <li><a href="#use-case" className="hover:text-gray-300">Use cases</a></li>
              <li><a href="#press" className="hover:text-gray-300">Press</a></li>
              <li><a href="#about" className="hover:text-gray-300">About</a></li>
              {/* <li>
                <button className="w-full px-8 py-3 text-black font-semibold rounded-full bg-gradient-to-r from-[#77FFF1] to-[#0B9284] mt-2">
                  Try Noha
                </button>
              </li> */}
              <li>
                <Link href={"/book-demo"}>
                  <button className="w-full px-5 py-2 border border-[#77FFF1] text-white rounded-full shadow-md mt-2">
                    Book a demo
                  </button>
                </Link>
              </li>
            </ul>
          </div>
        )}

        {/* Hero Content */}
        <div className="flex flex-col md:flex-row h-screen justify-center gap-10 mt-[10%] px-6">
          <div className="flex flex-col w-full md:w-[50%] text-white max-w-4xl">
            <h1 className="text-4xl font-bold text-center md:text-left">
              Noha.ai : Interview <br /> Smarter, Hire Better.
            </h1>
            <p className="mt-4 text-lg text-gray-300 text-center md:text-left">
              An AI-powered technical interviewer that conducts human-like,
              competency-based interviews to effortlessly identify top talent—no
              more manual interviews.
            </p>
            {/* Buttons */}
            <div className="mt-6 flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4 text-center md:text-left">
              <Link href={"/interview"}>
                <button className="px-8 py-3 text-black font-semibold rounded-full bg-gradient-to-r from-[#77FFF1] to-[#0B9284] ">
                  Try Noha
                </button>
              </Link>
              <Link href={"https://www.youtube.com/watch?v=D_RWdG1eIAc"}>
                <button className="px-6 py-3 border border-[#77FFF1] text-white rounded-full">
                  Watch a demo
                </button>
              </Link>
            </div>
          </div>
          <div className="hidden bg-blue-200 md:block w-72 h-72 rounded-full overflow-hidden">
            <img
              src="/NohaAI High res.png"
              alt="Noha AI"
              className="w-full h-full object-cover"
            />
          </div>
        </div>
      </div>

      <section id="use-case" className="py-16 px-6">
        <UseCase />
      </section>

      <section id="press" className="py-1 px-6">
        <Press />
      </section>

      <section id="about" className="py-1 px-6">
        <About />
      </section>

      {/* <section id="contact" className="py-16 px-6">
        <Contact/>
      </section> */}

      <Footer />

    </>
  );
};

export default Section1;
