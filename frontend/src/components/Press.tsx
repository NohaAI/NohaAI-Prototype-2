import { Newspaper } from "lucide-react";

const Press = () => {
  return (
    <section className="px-6 py-16 bg-[#f9f9ff]">
      {/* Heading + Icon */}
      <div className="flex flex-col items-center mb-8">
       <div className="flex flex-row gap-4">
            <h2 className="text-3xl font-bold text-black mb-2">Press</h2>
            <Newspaper className="text-[#361899]" size={32} />
       </div>
        <p className="text-gray-700 text-center max-w-xl mt-4">
          Featured on Major Starups Programms
        </p>
      </div>

      {/* YouTube Video */}
      <div className="flex justify-center">
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
    </section>
  );
};

export default Press;
