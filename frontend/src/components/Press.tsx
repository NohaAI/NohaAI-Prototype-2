import { Newspaper } from "lucide-react";

const Press = () => {
  return (
    <section className="px-6 py-16 bg-[#f9f9ff]">
      {/* Heading + Icon */}
      <div className="flex flex-col items-center mb-8">
        <div className="flex flex-row items-center gap-4">
          <h2 className="text-3xl font-bold text-black mb-2 underline decoration-green-400">Press</h2>
        </div>
        <p className="text-gray-700 text-center max-w-xl mt-4">
          Featured on Major Startup Programs
        </p>
      </div>

      {/* YouTube Video */}
      <div className="flex justify-center mb-12">
        <div className="w-full max-w-3xl aspect-video rounded-lg overflow-hidden shadow-lg">
          <iframe
            width="100%"
            height="100%"
            src="https://www.youtube.com/embed/D_RWdG1eIAc"
            title="Noha.ai Demo"
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            className="w-full h-full"
          />
        </div>
      </div>

      {/* Event Images Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
          <div className="rounded-lg overflow-hidden shadow-md">
            <img
              src="/press/press1.png"
              className="w-full h-60 object-cover"
            />
          </div>
          <div className="rounded-lg overflow-hidden shadow-md">
            <img
              src="/press/press2.png"
              className="w-full h-60 object-cover"
            />
          </div>
          <div className="rounded-lg overflow-hidden shadow-md">
            <img
              src="/press/press3.png"
              className="w-full h-60 object-cover"
            />
          </div>
          <div className="rounded-lg overflow-hidden shadow-md">
            <img
              src="/press/press4.png"
              className="w-full h-60 object-cover"
            />
          </div>
      </div>
    </section>
  );
};

export default Press;
