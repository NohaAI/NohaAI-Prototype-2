'use client'
import { useRouter } from 'next/navigation';
import { useState } from "react";
import { X } from "lucide-react";

interface InterviewDetailsProps {
    onSubmit: (data: { name: string; email: string; live_code: string }) => void;
}

const InterviewDetails: React.FC<InterviewDetailsProps> = ({ onSubmit }) => {
    const router = useRouter();
    const [formData, setFormData] = useState({ name: "", email: "", live_code: "" });
    const [loading, setLoading] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault(); // Prevent default form submission behavior
        
        if (!formData.name || !formData.email || !formData.live_code) return;

        try {
            console.log(formData);
            setLoading(true);
            await onSubmit({ ...formData });
            setLoading(false);
        } catch (error) {
            setLoading(false);
        }
    };

    return (
        <>
            <div className="fixed inset-0 flex justify-center bg-gradient-to-br from-[#3600FF] to-[#361899] p-6">
                {/* Close Button */}
                <button onClick={() => router.back()} className="absolute right-4 top-4 text-white">
                    <X size={24} />
                </button>

                <div className="relative w-full max-w-lg bg-transparent rounded-2xl p-8">
                    <h2 className="text-2xl md:text-3xl font-semibold text-white text-center">
                        Meet Noha: Your intelligent conversational interviewer
                    </h2>
                    <p className="text-gray-300 text-center mt-2">
                        Begin by providing your interview details.
                    </p>

                    {/* Form Section */}
                    <form onSubmit={handleSubmit} className="mt-10 space-y-6">
                        {/* Name Field */}
                        <div className="flex flex-col">
                            <label className="text-white text-lg font-bold mb-2">Name</label>
                            <input
                                autoFocus
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                placeholder="Enter your name"
                                className="w-full px-5 py-3 rounded-full bg-white text-gray-900 shadow-md outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                        </div>

                        {/* Email Field */}
                        <div className="flex flex-col">
                            <label className="text-white text-lg font-bold mb-2">Email</label>
                            <input
                                type="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                placeholder="Enter your email"
                                className="w-full px-5 py-3 rounded-full bg-white text-gray-900 shadow-md outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                        </div>

                        {/* Live Code Field */}
                        <div className="flex flex-col">
                            <label className="text-white text-lg font-bold mb-2">Access Code</label>
                            <input
                                type="text"
                                name="live_code"
                                value={formData.live_code}
                                onChange={handleChange}
                                placeholder="Enter live code"
                                className="w-full px-5 py-3 rounded-full bg-white text-gray-900 shadow-md outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                        </div>

                        {/* Submit Button */}
                        <div className="text-center">
                            <button
                                type="submit"
                                disabled={loading}
                                className="mt-6 px-14 py-2 bg-gradient-to-r from-[#0D99FF] to-[#0A5992] text-white font-medium text-lg rounded-full shadow-md"
                            >
                                {loading ? "Joining..." : "Join"}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </>
    );
};

export default InterviewDetails;
