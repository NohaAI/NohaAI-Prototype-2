import { motion } from "framer-motion";
import { X, Menu } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

const NavBar = () => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <>
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
        </>
    )
}

export default NavBar;

