
const Footer = () => {

    return (
        <footer className="bg-[#0C1B2E] text-white py-8 px-4">
            <div className="flex justify-center items-center">
                <div className="border-t border-gray-500 w-full max-w-[300px]"></div>
                <div className="w-4 h-4 bg-gray-300 rounded-full mx-4"></div>
                <div className="border-t border-gray-500 w-full max-w-[300px]"></div>
            </div>

            <div className="text-center mt-6">
                <p className="text-sm text-white">
                    © Copyright 2025. All rights reserved. • Terms & conditions • Privacy
                    policy
                </p>
            </div>

            <div className="flex justify-center mt-4 gap-6">
                <img
                    src="mail.png"
                    alt="Mail Icon"
                    className="w-6 h-6 cursor-pointer hover:opacity-80 transition"
                />
                <img
                    src="linkedin.png"
                    alt="LinkedIn Icon"
                    className="w-6 h-6 cursor-pointer hover:opacity-80 transition"
                />
                <img
                    src="x.png"
                    alt="X Icon"
                    className="w-6 h-6 cursor-pointer hover:opacity-80 transition"
                />
            </div>
        </footer>
    )
}

export default Footer