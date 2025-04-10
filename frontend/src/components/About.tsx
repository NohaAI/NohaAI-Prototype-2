const About = () => {
    return (
      <section className="px-6 py-16 bg-white">
        <h2 className="text-3xl font-bold text-center text-black mb-6">About Us</h2>
        <p className="text-center text-gray-700 max-w-2xl mx-auto mb-12">
          We're building AI that conducts technical interviews to help companies hire smarter and faster.
        </p>
  
        <div className="flex flex-col md:flex-row items-center justify-center gap-10">
          {/* Founder 1 */}
          <div className="flex flex-col items-center">
            <img
              src="/arun.png"
              alt="Founder 1"
              className="w-40 h-40 object-cover rounded-full shadow-md mb-4"
            />
            <p className="text-black text-lg font-semibold">Arun Panayappan</p> 
            <p className="text-gray-500"> Co-Founder & CEO </p>
         </div>
  
          {/* Founder 2 */}
          <div className="flex flex-col items-center">
            <img
              src="/ram.png"
              alt="Founder 2"
              className="w-40 h-40 object-cover rounded-full shadow-md mb-4"
            />
            <p className="text-black text-lg font-semibold">Rama Krishnan</p>
            <p> Co-Founder & COO </p>
          </div>
        </div>
      </section>
    );
  };
  
  export default About;
  