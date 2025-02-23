"use client";

import Link from "next/link";
import React, { useState } from "react";
import { motion } from "framer-motion";
import { Menu, X } from "lucide-react";

const Section1: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
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

        {/* Desktop Menu */}
        <div className="hidden md:flex space-x-8 text-white">
          <a href="#" className="hover:text-gray-300">Home</a>
          <a href="#" className="hover:text-gray-300">Product</a>
          <a href="#" className="hover:text-gray-300">About</a>
          <a href="#" className="hover:text-gray-300">Use cases</a>
        </div>

        {/* Login & Try Noha Buttons (Desktop) */}
        <div className="hidden md:flex space-x-4 pr-6">
          <button className="px-8 py-3 text-black font-semibold rounded-full bg-gradient-to-r from-[#77FFF1] to-[#0B9284] ">
            Try Noha
          </button>
          <button className="px-5 py-2 border border-[#77FFF1] text-white rounded-full shadow-md">
            Login
          </button>
        </div>

        {/* Mobile Menu Button */}
        <button onClick={() => setIsOpen(!isOpen)} className="md:hidden text-white">
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </motion.nav>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden w-full max-w-6xl bg-[#3224A2] rounded-lg mt-3 p-4 text-center">
          <ul className="space-y-4 text-white">
            <li><a href="#" className="hover:text-gray-300">Home</a></li>
            <li><a href="#" className="hover:text-gray-300">Product</a></li>
            <li><a href="#" className="hover:text-gray-300">About</a></li>
            <li><a href="#" className="hover:text-gray-300">Use cases</a></li>
            <li>
              <button className="w-full px-8 py-3 text-black font-semibold rounded-full bg-gradient-to-r from-[#77FFF1] to-[#0B9284] mt-2">
                Try Noha
              </button>
            </li>
            <li>
              <button className="w-full px-5 py-2 border border-[#77FFF1] text-white rounded-full shadow-md mt-2">
                Login
              </button>
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
            <button className="px-6 py-3 border border-[#77FFF1] text-white rounded-full">
              Watch a demo
            </button>
          </div>
        </div>
        <div className="hidden md:block w-72 h-72 bg-[#16073D] rounded-full"></div>
      </div>
    </div>
  );
};

export default Section1;
