'use client';
import { useState, useRef, useEffect } from "react";
import { Mic, MicOff, Video, VideoOff, Phone, Pause } from "lucide-react";
import { BeatLoader, BounceLoader, MoonLoader, ScaleLoader } from "react-spinners";

const LiveInterview = ({ name, onCancelCall, userSocket, isRecording, stopRecording, startRecording, isMicOn, chats, nohaResponseProcessing, isAudioPlaying }: any) => {
  console.log('isRecording', isRecording);
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [isMicActive, setIsMicActive] = useState(isMicOn);
  const videoRef = useRef<any>(null);
  const videoStreamRef = useRef<any>(null);

  const [startSpeakHint, setStartSpeakHint] = useState(false);
  const [stopSpeakHint, setStopSpeakHint] = useState(false);

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
    // stop recording
    if (isRecording) {
      stopRecording();
      setIsMicActive(false);

      setStopSpeakHint(true);

    }
    // start recording
    else {
      startRecording();
      setIsMicActive(true);

      setStartSpeakHint(true);
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

      <div className="relative bg-[#1F1F1F] rounded-lg p-4 flex flex-col justify-center items-center w-full md:w-[474px] md:h-[458px]">
        {isAudioPlaying && <ScaleLoader color="white" className="absolute right-4 top-4" />}

        <img src="noha.png" alt="User" className="w-[226px] h-[226px] object-cover " />

        {isAudioPlaying && <p className="mt-1 text-white">{chats[0].name === 'Noha AI' && chats[0].message}</p>}

        {nohaResponseProcessing && <BeatLoader color="white" className="mt-4" />}

        <p className="text-white mt-2 absolute left-3 bottom-2">Noha</p>
      </div>


      {/* Chat Section */}
      {/* <div className="bg-[#1F1F1F] rounded-lg p-4 w-full md:w-[600px] h-[600px] overflow-y-auto border border-gray-700 mt-4">
          {nohaResponseProcessing && <div className="p-3 mb-4 rounded-lg text-sm bg-blue-800  text-white">
            <p className="font-bold">Noha AI</p>
            <BeatLoader color="#FFFFFF" className="my-3"/>
          </div>}
        <div className="flex flex-col gap-4">
          {chats.map((chat: { name: string, message: string }, index: number) => (
            <div key={index} className={`p-3 rounded-lg text-sm ${chat.name === 'Noha AI' ? 'bg-blue-800 text-white' : 'bg-gray-800 text-white'}` }>
              <p className="font-bold">{chat.name}</p>
              <p>{chat.message}</p>
            </div>
          ))}
        </div>
      </div> */}

      {/* Call Controls */}
      <div className="w-full fixed bottom-6 left-1/2 transform -translate-x-1/2 flex items-center justify-center space-x-10 p-3 rounded-full">

        {/* Camera Button */}
        <button onClick={toggleCamera} className="w-14 h-14 flex items-center justify-center rounded-full bg-gray-700 hover:bg-gray-600 transition">
          {isCameraOn ? <Video className="text-white w-7 h-7" /> : <VideoOff className="text-white w-7 h-7" />}
        </button>

        {/* Mic Button with Tooltip */}
        <div className="relative flex flex-col items-center group">
          {/* Tooltip with Arrow */}
          {!isAudioPlaying && (!startSpeakHint || !stopSpeakHint) && <div className="absolute bottom-24 bg-gray-700 text-white text-sm px-3 py-1 rounded-md opacity-90 group-hover:opacity-100 transition w-max">
            {!startSpeakHint ? <p> Click to answer </p> : <p> Click to stop </p>}
            {/* {!stopSpeakHint && <p> Click here is stop </p>} */}
            {/* Tooltip Arrow */}
            <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-8 border-l-transparent border-r-8 border-r-transparent border-t-8 border-t-gray-700 "></div>
          </div>}

          {/* Mic Button */}
          {nohaResponseProcessing ? (
            <BounceLoader size={80} color="white" className="border-red-400" />
          ) : (
            <button
              disabled={isAudioPlaying}
              onClick={toggleMic}
              className={`w-20 h-20 flex items-center justify-center rounded-full bg-green-500 hover:bg-gray-600 transition disabled:bg-gray-400 ${!isAudioPlaying ? "animate-pulse" : ""}`}
            >
              {isMicActive ? <Pause className="text-white w-10 h-10" /> : <Mic className="text-white w-10 h-10" />}
            </button>
          )}
        </div>

        {/* Call Button */}
        <button onClick={onCancelCall} className="w-14 h-14 flex items-center justify-center rounded-full bg-red-600 hover:bg-red-500 transition">
          <Phone className="text-white w-7 h-7" />
        </button>
      </div>

    </div>
  );
};

export default LiveInterview;