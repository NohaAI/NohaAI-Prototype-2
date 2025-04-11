const About = () => {
    return (
        <section className="px-6 py-16 bg-white">
            <h2 className="text-3xl font-bold text-center text-black mb-6 underline decoration-green-400 underline-offset-4">The Founders</h2>

            <div className="flex flex-col md:flex-row items-start justify-center gap-16 md:gap-24 px-6 mt-4">
                {/* Founder 1 */}
                <div className="w-full md:w-80 flex flex-col items-center text-center">
                    <img
                        src="/arun.png"
                        alt="Arun Panayappan"
                        className="w-40 h-40 object-cover rounded-full shadow-md mb-4"
                    />
                    <p className="text-[#361899] text-xl font-semibold">Arun Panayappan</p>
                    <p className="text-lg text-gray-800 mb-2">Co-Founder & CEO</p>
                    <p className="text-md text-gray-600">
                        Over 25 years of IT experience building products for companies like Google and Amazon.
                        Holds 3 papers and 4 patents in artificial intelligence and expert systems.
                    </p>
                </div>

                {/* Founder 2 */}
                <div className="w-full md:w-80 flex flex-col items-center text-center">
                    <img
                        src="/ram.png"
                        alt="Rama Krishnan"
                        className="w-40 h-40 object-cover rounded-full shadow-md mb-4"
                    />
                    <p className="text-[#361899] text-xl font-semibold">Rama Krishnan</p>
                    <p className="text-lg text-gray-800 mb-2">Co-Founder & COO</p>
                    <p className="text-md text-gray-600">
                        An IIM alumnus with over 18 years of experience in talent acquisition. Most recently served
                        as the HR Head at Yellow.ai, scaling the company from 10 to 1,000+ employees globally.
                        Previously worked with Amazon, VMware, and Yahoo.
                    </p>
                </div>
            </div>

        </section>
    );
};

export default About;
