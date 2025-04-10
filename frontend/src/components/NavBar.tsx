import { motion } from "framer-motion";
import { X, Menu } from "lucide-react";
import { useState } from "react";
import BookDemoModal from "@/components/BookDemoModal"; // make sure this path is correct

const NavBar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const handleSubmit = (data: any) => {
    console.log(data);  
    onClose();
  };

  const onClose = () => {
    setShowModal(false);
  }

  return (
    <>
      {/* Navbar */}
      <motion.nav
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-6xl mt-6 px-6 py-3 flex justify-between items-center bg-[#3224A2] rounded-full shadow-lg"
      >
        <div className="text-white text-lg font-semibold px-6">Noha.ai</div>

        <div className="hidden md:flex space-x-8 text-white">
          <a href="#use-case" className="hover:text-gray-300">Use cases</a>
          <a href="#press" className="hover:text-gray-300">Press</a>
          <a href="#contact" className="hover:text-gray-300">Contact</a>
          <a href="#about" className="hover:text-gray-300">About</a>
        </div>

        <div className="hidden md:flex space-x-4 pr-6">
          <button
            onClick={() => setShowModal(true)}
            className="px-5 py-2 border border-[#77FFF1] text-white rounded-full shadow-md"
          >
            Book a demo
          </button>
        </div>

        <button onClick={() => setIsOpen(!isOpen)} className="md:hidden text-white">
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </motion.nav>

      {isOpen && (
        <div className="md:hidden w-full max-w-6xl bg-[#3224A2] rounded-lg mt-3 p-4 text-center">
          <ul className="space-y-4 text-white">
            <li><a href="#use-case" className="hover:text-gray-300">Use cases</a></li>
            <li><a href="#press" className="hover:text-gray-300">Press</a></li>
            <li><a href="#about" className="hover:text-gray-300">About</a></li>
            <li>
              <button
                onClick={() => {
                  setIsOpen(false);
                  setShowModal(true);
                }}
                className="w-full px-5 py-2 border border-[#77FFF1] text-white rounded-full shadow-md mt-2"
              >
                Book a demo
              </button>
            </li>
          </ul>
        </div>
      )}

      {/* Book a Demo Modal */}
      {showModal && <BookDemoModal handleSubmit={handleSubmit} onClose={onClose} />}
    </>
  );
};

export default NavBar;
