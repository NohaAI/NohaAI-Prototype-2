'use client';
import { useState, useRef } from "react";
import { Mic, MicOff, Video, VideoOff, Phone, Pause } from "lucide-react";

const LiveInterview = ({ name, onCancelCall, userSocket, isRecording, stopRecording, startRecording, isMicOn, chats }: any) => {
  console.log('isRecording', isRecording);
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [isMicActive, setIsMicActive] = useState(isMicOn);
  const videoRef = useRef<any>(null);
  const videoStreamRef = useRef<any>(null);

  const toggleCamera = async () => {
    if (isCameraOn) {
      videoStreamRef.current?.getTracks().forEach((track: any) => track.stop());
      if (videoRef.current) videoRef.current.srcObject = null;
      videoStreamRef.current = null;
      setIsCameraOn(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
        videoStreamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
        }
        setIsCameraOn(true);
      } catch (error) {
        console.error("Error accessing the camera:", error);
      }
    }
  };

  const toggleMic = async () => {
    console.log('toggleMic');
    if (isRecording) {
      stopRecording();
      setIsMicActive(false);
    } else {
      startRecording();
      setIsMicActive(true);
    }
  };

  return (
    <div className="min-h-screen bg-black px-4 flex flex-row justify-center items-center gap-4">
      {/* User Video */}
      <div className="relative bg-[#1F1F1F] rounded-lg p-4 flex flex-col justify-center items-center w-full md:w-[474px] md:h-[458px]">
        <video ref={videoRef} autoPlay playsInline muted className="w-full h-[90%] object-cover rounded-lg" />
        {!isCameraOn && <img src="user.png" alt="User" className="w-[226px] h-[226px] object-cover mb-[45%]" />}
        <p className="text-white mt-2 absolute left-3 bottom-2">{name}</p>
      </div>
      
      {/* Chat Section */}
      <div className="bg-[#1F1F1F] rounded-lg p-4 w-full md:w-[600px] h-[600px] overflow-y-auto border border-gray-700 mt-4">
        <div className="flex flex-col gap-4">
          {chats.map((chat: { name: string, message: string }, index: number) => (
            <div key={index} className={`p-3 rounded-lg text-sm ${chat.name === 'Noha AI' ? 'bg-blue-800 text-white' : 'bg-gray-800 text-white'}` }>
              <p className="font-bold">{chat.name}</p>
              <p>{chat.message}</p>
            </div>
          ))}
        </div>
      </div>
      
      {/* Call Controls */}
      <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 flex space-x-4 p-3 bg-black/50 rounded-full">
        <button onClick={toggleMic} className="p-3 rounded-full bg-gray-700 hover:bg-gray-600 transition">
          {isMicActive ? <Pause className="text-white w-6 h-6" /> : <Mic className="text-white w-6 h-6" />}
        </button>
        <button onClick={toggleCamera} className="p-3 rounded-full bg-gray-700 hover:bg-gray-600 transition">
          {isCameraOn ? <Video className="text-white w-6 h-6" /> : <VideoOff className="text-white w-6 h-6" />}
        </button>
        <button onClick={onCancelCall} className="p-3 rounded-full bg-red-600 hover:bg-red-500 transition">
          <Phone className="text-white w-6 h-6" />
        </button>
      </div>
    </div>
  );
};

export default LiveInterview;