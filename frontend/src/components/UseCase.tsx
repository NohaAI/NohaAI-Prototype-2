import { Briefcase, Users, Code2, Globe, UserCheck } from "lucide-react";

const UseCase = () => {
  return (
    <section className="px-6 py-16 bg-white">
      {/* Heading */}
      <div className="flex flex-col items-center mb-12">
        <div className="flex flex-row gap-4">
            <h2 className="text-3xl font-bold text-black mb-2">Use Cases</h2>
            <UserCheck size={36} className="text-[#361899] mb-4"/>
        </div>
        <p className="text-gray-700 text-center max-w-xl">
          Noha.ai adapts to a variety of technical hiring needs across industries.
        </p>
      </div>

      <div className="flex justify-center my-10">
          <div className="flex flex-col lg:flex-row gap-10 items-center justify-center lg:items-center bg-blue-50 p-6 lg:p-12 rounded-3xl w-full lg:w-[900px] h-auto lg:h-[400px]">
            <div className="lg:w-1/2 mt-6 lg:mt-0 flex justify-end">
              <div className="bg-white w-[300px] h-[250px] lg:w-[350px] lg:h-[300px] rounded-3xl"></div>
            </div>
           
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
            <div className="lg:w-[305px] flex flex-col justify-center">
              <h2 className="text-[22px]  text-black mb-4">
                How Noha helps to conduct interview drives for technology product organizations?
              </h2>
              <button className="w-[132px] h-[50px] px-3 text-center bg-gradient-to-r from-[#0D99FF] to-[#0A5992] text-white text-[14px] rounded-full">
                Watch a demo
              </button>
            </div>
           
            <div className="lg:w-1/2 mt-6 lg:mt-0 flex justify-end">
              <div className="bg-white w-[300px] h-[250px] lg:w-[350px] lg:h-[300px] rounded-3xl"></div>
            </div>
          
          </div>
        </div>

        <div className="flex justify-center my-10">
          <div className="flex flex-col lg:flex-row gap-10 items-center justify-center lg:items-center bg-blue-50 p-6 lg:p-12 rounded-3xl w-full lg:w-[900px] h-auto lg:h-[400px]">
            <div className="lg:w-1/2 mt-6 lg:mt-0 flex justify-end">
              <div className="bg-white w-[300px] h-[250px] lg:w-[350px] lg:h-[300px] rounded-3xl"></div>
            </div>
           
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

     
    </section>
  );
};

export default UseCase;
