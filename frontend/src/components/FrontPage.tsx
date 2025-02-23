import Link from "next/link";
import Section1 from "./Section1";

export default function FrontPage() {
  return (
    <>

      <Section1/>

      <div className="mb-14 mt-12 flex justify-center">
        <div className="w-[421px]">
          <h2 className="text-[28px] text-center">
            How Noha Enhances Efficiency in Interview Process
          </h2>
        </div>
      </div>

      <section className=" bg-white text-gray-900 lg:px-20 py-12">

        {/* Content */}
        <div className="mx-[15%] flex flex-col lg:flex-row items-center lg:items-center justify-between gap-10">
          {/* Text Content */}
          <div className="lg:w-1/2">
            <h3 className="text-[22px] mb-4">
              Quality - Set your bar & we do the rest
            </h3>
            <p className="text-gray-600 text-[16px]">
              Noha.ai evaluates candidates according to the company’s established
              standards, with depth levels adjustable to meet specific requirements.
            </p>
          </div>
          {/* Placeholder for Image/Content */}
          <img src="image (10).webp" alt="Your image description" className="lg:w-1/2 w-full h-64 lg:h-96 object-cover rounded-lg" />
        </div>

      </section>

      <section className="bg-[#EEF8FF] text-gray-900 px-6 lg:px-20 py-12">
        {/* Content */}
        <div className="mx-[15%] flex flex-col lg:flex-row items-center lg:items-center justify-between gap-10">

          {/* Text Content */}
          <div className="lg:w-1/2">
            <h3 className="text-[22px] mb-4">
              Quality - Set your bar & we do the rest
            </h3>
            <p className="text-gray-600 text-[16px]">
              Noha.ai evaluates candidates according to the company’s established
              standards, with depth levels adjustable to meet specific requirements.
            </p>
          </div>
          {/* Placeholder for Image/Content */}
          <img src="image (10).webp" alt="Your image description" className="lg:w-1/2 w-full h-64 lg:h-96 object-cover rounded-lg" />

        </div>
      </section>
      <section className="bg-white text-gray-900 px-6 lg:px-20 py-12">
        {/* Content */}
        <div className="mx-[15%] flex flex-col lg:flex-row items-center lg:items-center justify-between gap-10">
          {/* Placeholder for Image/Content */}
          <img src="image (10).webp" alt="Your image description" className="lg:w-1/2 w-full h-64 lg:h-96 object-cover rounded-lg" />

          {/* Text Content */}
          <div className="lg:w-1/2">
            <h3 className="text-[22px] mb-4">
              Quality - Set your bar & we do the rest
            </h3>
            <p className="text-gray-600 text-[16px]">
              Noha.ai evaluates candidates according to the company’s established
              standards, with depth levels adjustable to meet specific requirements.
            </p>
          </div>
        </div>
      </section>

      <section className="">
        <div className="relative lg:px-[20%] bg-[#1C0860] text-white py-16 px-8 rounded-tr-[60px] rounded-tl-[60px]">
          <div className="max-w-7xl mx-auto flex flex-col lg:flex-row items-center gap-4">
          <img src="curve3.png" alt="" className="absolute left-0" />
            {/* Left Section */}
            <div className="flex-1">
              <h1 className="text-4xl font-semibold leading-tight">
                Experience the power <br /> of Noha
              </h1>
              <p className="text-gray-400 mt-4">
                An AI technical interviewer that conducts deep-dive, human-like
                conversational interviews as per the company set bar & competency.
              </p>
              <button className="mt-6 px-6 py-3 text-sm font-medium text-white border border-[#0D99FF] rounded-full text-[14px]">
                Try AI Interview
              </button>
            </div>

            {/* Right Section */}
            <div className="flex-1 flex justify-center items-center">
              <div className="w-full max-w-[400px] h-[250px] bg-gray-300 rounded-[30px]"></div>
            </div>
          </div>
        </div>
      </section>

      <div className="mb-14 mt-12 flex justify-center">
        <div className="w-[421px]">
          <h2 className="text-[28px] text-center">
            How Noha Enhances Efficiency in Interview Process    </h2>
        </div>
      </div>

      <section>
        <div className=" mx-[20%] flex flex-row flex-wrap justify-center gap-5">
          <div className="relative px-4 w-[225px] h-[200px] bg-[#A78CFF] rounded-[40px] flex items-center justify-center text-center font-[500] text-[28px]">
            5X hiring speed
            <img src="curve4.png" className="absolute right-0 bottom-0"/>
          </div>
          <div className="relative w-[225px] h-[200px] bg-[#F1EDFF] rounded-[40px] flex items-center justify-center text-center font-[500] text-[28px]">
  80% interview efficiency
  <img src="curve5.png" className="absolute left-0 top-0"/>

</div>
          <div className="relative w-[225px] h-[200px] bg-[#A78CFF] rounded-[40px] flex items-center justify-center text-center font-[500] text-[28px]">75% cost reduction
          <img src="curve6.png" className="absolute right-0 top-0"/>
          </div>
          <div className="relative w-[225px] h-[200px] bg-[#F1EDFF] rounded-[40px] flex items-center justify-center text-center font-[500] text-[28px]">100% conversational
          <img src="curve7.png" className="absolute left-0 top-[20%]"/>
          </div>
          <div className="relative w-[225px] h-[200px] bg-[#A78CFF] rounded-[40px] flex items-center justify-center text-center font-[500] text-[28px]">95% candidate experience
          <img src="curve8.png" className="absolute left-0 bottom-0"/>
          </div>
          <div className="relative px-2 w-[225px] h-[200px] bg-[#F1EDFF] rounded-[40px] flex items-center justify-center text-center font-[500] text-[28px]">100% unbaisness
          <img src="curve9.png" className="absolute right-0 bottom-0"/>
          </div>
        </div>
      </section>

      <div className="mb-14 mt-12 flex justify-center">
        <div className="w-full">
          <h2 className="text-[28px] text-center">
            About Noha.ai
          </h2>
        </div>
      </div>

      <section>
        <div className="w-full h-auto bg-[#0D1F2B] rounded-bl-[60px] rounded-br-[60px] mb-10">

          <div className="flex flex-row flex-wrap justify-center gap-10 py-20">

            <div className="w-[225px] flex flex-col items-start">
              <img src="image (10).webp" alt="Our Story" className="w-[78px] h-[78px] rounded-full object-cover" />

              <h2 className="text-[24px] text-white font-normal mt-3">Our Story</h2>

              <p className="w-[225px] h-[144px] text-white mt-2 overflow-hidden">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                Vivamus lacinia odio vitae vestibulum vestibulum. Cras venenatis euismod malesuada.
              </p>
            </div>

            <div className="w-[225px] flex flex-col items-start">
              <img src="image (10).webp" alt="Our Story" className="w-[78px] h-[78px] rounded-full object-cover" />

              <h2 className="text-[24px] text-white font-normal mt-3">Our Story</h2>

              <p className="w-[225px] h-[144px] text-white mt-2 overflow-hidden">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                Vivamus lacinia odio vitae vestibulum vestibulum. Cras venenatis euismod malesuada.
              </p>
            </div>

            <div className="w-[225px] flex flex-col items-start">
              <img src="image (10).webp" alt="Our Story" className="w-[78px] h-[78px] rounded-full object-cover" />

              <h2 className="text-[24px] text-white font-normal mt-3">Our Story</h2>

              <p className="w-[225px] h-[144px] text-white mt-2 overflow-hidden">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                Vivamus lacinia odio vitae vestibulum vestibulum. Cras venenatis euismod malesuada.
              </p>
            </div>

          </div>

        </div>
      </section>

      <div className="mb-14 mt-12 flex justify-center">
        <div className="w-[421px]">
          <h2 className="text-[28px] text-center">
            Use Case
          </h2>
        </div>
      </div>

      <section>

        <div className="flex justify-center my-10">
          <div className="flex flex-col lg:flex-row gap-10 items-center justify-center lg:items-center bg-blue-50 p-6 lg:p-12 rounded-3xl w-full lg:w-[900px] h-auto lg:h-[400px]">
            {/* Left Section */}
            <div className="lg:w-1/2 mt-6 lg:mt-0 flex justify-end">
              <div className="bg-white w-[300px] h-[250px] lg:w-[350px] lg:h-[300px] rounded-3xl"></div>
            </div>
           
            {/* Right Section */}
            <div className="lg:w-[305px] flex flex-col justify-center">
              <h2 className="text-[22px]  text-black mb-4">
                How Noha helps to conduct interview drives for technology product organizations?
              </h2>
              <button className="w-[132px] h-[50px] px-3 text-center bg-gradient-to-r from-[#0D99FF] to-[#0A5992] text-white text-[14px] rounded-full">
                Watch a demo
              </button>
            </div>

          
          </div>
        </div>

        <div className="flex justify-center my-10">
          <div className="flex flex-col lg:flex-row gap-10 items-center justify-center lg:items-center bg-blue-50 p-6 lg:p-12 rounded-3xl w-full lg:w-[900px] h-auto lg:h-[400px]">
            {/* Left Section */}
            <div className="lg:w-[305px] flex flex-col justify-center">
              <h2 className="text-[22px]  text-black mb-4">
                How Noha helps to conduct interview drives for technology product organizations?
              </h2>
              <button className="w-[132px] h-[50px] px-3 text-center bg-gradient-to-r from-[#0D99FF] to-[#0A5992] text-white text-[14px] rounded-full">
                Watch a demo
              </button>
            </div>
           
            {/* Right Section */}
            <div className="lg:w-1/2 mt-6 lg:mt-0 flex justify-end">
              <div className="bg-white w-[300px] h-[250px] lg:w-[350px] lg:h-[300px] rounded-3xl"></div>
            </div>
          
          </div>
        </div>

        <div className="flex justify-center my-10">
          <div className="flex flex-col lg:flex-row gap-10 items-center justify-center lg:items-center bg-blue-50 p-6 lg:p-12 rounded-3xl w-full lg:w-[900px] h-auto lg:h-[400px]">
            {/* Left Section */}
            <div className="lg:w-1/2 mt-6 lg:mt-0 flex justify-end">
              <div className="bg-white w-[300px] h-[250px] lg:w-[350px] lg:h-[300px] rounded-3xl"></div>
            </div>
           
            {/* Right Section */}
            <div className="lg:w-[305px] flex flex-col justify-center">
              <h2 className="text-[22px]  text-black mb-4">
                How Noha helps to conduct interview drives for technology product organizations?
              </h2>
              <button className="w-[132px] h-[50px] px-3 text-center bg-gradient-to-r from-[#0D99FF] to-[#0A5992] text-white text-[14px] rounded-full">
                Watch a demo
              </button>
            </div>

          
          </div>
        </div>

        <div className="flex justify-center my-10">
          <div className="flex flex-col lg:flex-row gap-10 items-center justify-center lg:items-center bg-blue-50 p-6 lg:p-12 rounded-3xl w-full lg:w-[900px] h-auto lg:h-[400px]">
            {/* Left Section */}
            <div className="lg:w-[305px] flex flex-col justify-center">
              <h2 className="text-[22px]  text-black mb-4">
                How Noha helps to conduct interview drives for technology product organizations?
              </h2>
              <button className="w-[132px] h-[50px] px-3 text-center bg-gradient-to-r from-[#0D99FF] to-[#0A5992] text-white text-[14px] rounded-full">
                Watch a demo
              </button>
            </div>
           
            {/* Right Section */}
            <div className="lg:w-1/2 mt-6 lg:mt-0 flex justify-end">
              <div className="bg-white w-[300px] h-[250px] lg:w-[350px] lg:h-[300px] rounded-3xl"></div>
            </div>
          
          </div>
        </div>

        <div className="flex justify-center my-10">
          <div className="flex flex-col lg:flex-row gap-10 items-center justify-center lg:items-center bg-blue-50 p-6 lg:p-12 rounded-3xl w-full lg:w-[900px] h-auto lg:h-[400px]">
            {/* Left Section */}
            <div className="lg:w-1/2 mt-6 lg:mt-0 flex justify-end">
              <div className="bg-white w-[300px] h-[250px] lg:w-[350px] lg:h-[300px] rounded-3xl"></div>
            </div>
           
            {/* Right Section */}
            <div className="lg:w-[305px] flex flex-col justify-center">
              <h2 className="text-[22px]  text-black mb-4">
                How Noha helps to conduct interview drives for technology product organizations?
              </h2>
              <button className="w-[132px] h-[50px] px-3 text-center bg-gradient-to-r from-[#0D99FF] to-[#0A5992] text-white text-[14px] rounded-full">
                Watch a demo
              </button>
            </div>

          
          </div>
        </div>

        <div className="flex justify-center my-10">
          <div className="flex flex-col lg:flex-row gap-10 items-center justify-center lg:items-center bg-blue-50 p-6 lg:p-12 rounded-3xl w-full lg:w-[900px] h-auto lg:h-[400px]">
            {/* Left Section */}
            <div className="lg:w-[305px] flex flex-col justify-center">
              <h2 className="text-[22px]  text-black mb-4">
                How Noha helps to conduct interview drives for technology product organizations?
              </h2>
              <button className="w-[132px] h-[50px] px-3 text-center bg-gradient-to-r from-[#0D99FF] to-[#0A5992] text-white text-[14px] rounded-full">
                Watch a demo
              </button>
            </div>
           
            {/* Right Section */}
            <div className="lg:w-1/2 mt-6 lg:mt-0 flex justify-end">
              <div className="bg-white w-[300px] h-[250px] lg:w-[350px] lg:h-[300px] rounded-3xl"></div>
            </div>
          
          </div>
        </div>

      </section>

      <footer className="bg-[#0C1B2E] text-white py-8 px-4">
      {/* Top divider with circle */}
      <div className="flex justify-center items-center">
        <div className="border-t border-gray-500 w-full max-w-[300px]"></div>
        <div className="w-4 h-4 bg-gray-300 rounded-full mx-4"></div>
        <div className="border-t border-gray-500 w-full max-w-[300px]"></div>
      </div>

      {/* Text Content */}
      <div className="text-center mt-6">
        <p className="text-sm text-white">
          © Copyright 2025. All rights reserved. • Terms & conditions • Privacy
          policy
        </p>
      </div>

      {/* Social Icons */}
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

    </>
  );
}
