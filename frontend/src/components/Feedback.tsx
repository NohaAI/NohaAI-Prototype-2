'use client'
import { useState } from "react";
import { Star } from "lucide-react";

const Feedback = ({ sendFeedback } : any) => {
  const [rating, setRating] = useState<number>(0);

  const handleRating = (selectedRating: number) => {
    setRating(selectedRating);
  };

  const handleSubmit = async() => {
    sendFeedback(rating)
  };

  return (
    <div className="
    bg-[url('/curve2.png')] bg-no-repeat bg-cover bg-center w-full
    flex flex-col justify-center items-center min-h-screen 
    bg-[#F6F5FF]
  ">      <div className="  text-center max-w-md w-full relative">
        <h2 className="text-xl font-semibold text-gray-900">
          The interview with Noha has been completed.
        </h2>
        <p className="text-gray-500 mt-2">
          Kindly check your email for the report.
        </p>

        {/* Feedback Section */}
        <div className="mt-6">
          <p className="text-gray-700 font-medium mb-2">Submit feedback</p>
          <div className="flex justify-center space-x-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <Star
                key={star}
                className={`h-8 w-8 cursor-pointer transition-all ${
                  star <= rating ? "fill-yellow-400 text-yellow-400" : "text-gray-300"
                }`}
                onClick={() => handleRating(star)}
              />
            ))}
          </div>
        </div>

        {/* Submit Button */}
        {rating > 0 && (
          <button
            onClick={handleSubmit}
            className="mt-6 px-6 py-2   text-white font-medium rounded-full shadow-md bg-gradient-to-r from-[#77FFF1] to-[#0B9284] "
          >
            Submit Feedback
          </button>
        )}
      </div>
    </div>
  );
};

export default Feedback;
