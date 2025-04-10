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

      {/* Use Case Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
        {/* Use Case 1 */}
        <div className="flex flex-col items-center text-center p-6 rounded-2xl shadow-md hover:shadow-lg transition bg-[#f5f7ff]">
          <Briefcase size={36} className="text-[#361899] mb-4" />
          <h3 className="text-lg font-semibold text-black mb-2">Enterprise Hiring</h3>
          <p className="text-sm text-gray-600">
            Scale interviews across teams and departments with consistency.
          </p>
        </div>

        {/* Use Case 2 */}
        <div className="flex flex-col items-center text-center p-6 rounded-2xl shadow-md hover:shadow-lg transition bg-[#f5f7ff]">
          <Users size={36} className="text-[#361899] mb-4" />
          <h3 className="text-lg font-semibold text-black mb-2">Recruiting Agencies</h3>
          <p className="text-sm text-gray-600">
            Pre-screen candidates with real-time technical interviews.
          </p>
        </div>

        {/* Use Case 3 */}
        <div className="flex flex-col items-center text-center p-6 rounded-2xl shadow-md hover:shadow-lg transition bg-[#f5f7ff]">
          <Code2 size={36} className="text-[#361899] mb-4" />
          <h3 className="text-lg font-semibold text-black mb-2">Engineering Teams</h3>
          <p className="text-sm text-gray-600">
            Let Noha handle technical screening so you focus on building.
          </p>
        </div>

        {/* Use Case 4 */}
        <div className="flex flex-col items-center text-center p-6 rounded-2xl shadow-md hover:shadow-lg transition bg-[#f5f7ff]">
          <Globe size={36} className="text-[#361899] mb-4" />
          <h3 className="text-lg font-semibold text-black mb-2">Remote Hiring</h3>
          <p className="text-sm text-gray-600">
            Assess global talent efficiently with automated, unbiased interviews.
          </p>
        </div>
      </div>
    </section>
  );
};

export default UseCase;
