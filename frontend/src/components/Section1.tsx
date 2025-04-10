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
import NavBar from "./NavBar";

const Section1: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <section>
        <div
          className="relative h-screen bg-[#361899] flex flex-col items-center 
                  bg-[url('/curve.png')] bg-no-repeat bg-contain bg-center"
        >
          <NavBar />
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
                  <button className="px-8 py-3 text-black font-semibold rounded-full bg-gradient-to-r from-[#77FFF1] to-[#0B9284]">
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
      </section>

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
