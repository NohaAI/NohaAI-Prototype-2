import { X } from "lucide-react";
import { useState } from "react";

const BookDemoModal = ({ onClose, handleSubmit }: any) => {

     const [formData, setFormData] = useState({
        name: "",
        email: "",
        contact: "",
      });
    
      const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
      };

      const handleFormSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        handleSubmit(formData);
    }
      
    return (
      <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50">
        <div className="relative bg-white rounded-xl p-6 w-full max-w-md shadow-lg">
          <h2 className="text-xl text-center font-semibold mb-4 underline decoration-green-400">Book a Demo</h2>
          <form onSubmit={handleFormSubmit} className="space-y-6">
          <div>
            <label className="block text-sm text-gray-700 font-bold">Name</label>
            <input
              autoFocus
              type="text"
              name="name"
              required
              value={formData.name}
              onChange={handleChange}
              className="mt-1 w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-[#361899] focus:border-[#361899]"
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-gray-700">Email</label>
            <input
              type="email"
              name="email"
              required
              value={formData.email}
              onChange={handleChange}
              className="mt-1 w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-[#361899] focus:border-[#361899]"
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-gray-700">Contact Number</label>
            <input
              type="tel"
              name="contact"
              required
              value={formData.contact}
              onChange={handleChange}
              className="mt-1 w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-[#361899] focus:border-[#361899]"
            />
          </div>

          <button
            type="submit"
            className="w-full py-3 text-white font-semibold rounded-md bg-gradient-to-r from-[#77FFF1] to-[#0B9284]"
          >
            Submit
          </button>
        </form>
          <button onClick={onClose} className="absolute top-4 right-4 text-black hover:text-black">
            <X size={24} />
          </button>
        </div>
      </div>
    );
  };
  
  export default BookDemoModal;
  