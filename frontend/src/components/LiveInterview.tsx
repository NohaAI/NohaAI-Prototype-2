'use client';
import { useState, useRef, useEffect } from "react";
import { Mic, MicOff, Video, VideoOff, Phone, Pause, PhoneOff, Monitor } from "lucide-react";
import { ScaleLoader, BeatLoader } from "react-spinners";

const LiveInterview = ({ name, onCancelCall, userSocket, isRecording, stopRecording, startRecording, isMicOn, chats, nohaResponseProcessing, isAudioPlaying }: any) => {
  console.log('isAudioPlaying', isAudioPlaying);

  const [isCameraOn, setIsCameraOn] = useState(true);
  const [isMicActive, setIsMicActive] = useState(isMicOn);
  const videoRef = useRef<any>(null);
  const videoStreamRef = useRef<any>(null);

  const [startSpeakHint, setStartSpeakHint] = useState(false);
  const [stopSpeakHint, setStopSpeakHint] = useState(false);

  useEffect(()=>{
  }, []);

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

  return (
    <div className="min-h-screen bg-black px-4 flex flex-row justify-center items-center gap-4">

      {/* User Video */}
      <div className="relative bg-[#1F1F1F] rounded-lg p-4 flex flex-col justify-center items-center w-full md:w-[474px] md:h-[458px]">
        <video ref={videoRef} autoPlay playsInline muted className="w-full h-[90%] object-cover rounded-lg" />
        {/* {!isCameraOn && <img src="user.png" alt="User" className="w-[226px] h-[226px] object-cover mb-[45%]" />} */}
        <p className="text-white mt-2 absolute left-3 bottom-2">{name}</p>
      </div>

      <div className="relative bg-[#1F1F1F] rounded-lg p-4 flex flex-col justify-center items-center w-full md:w-[474px] md:h-[458px]">
        {isAudioPlaying && <ScaleLoader color="white" className="absolute right-4 top-4" />}

        <img src="noha.png" alt="User" className="w-[226px] h-[226px] object-cover " />

        {isAudioPlaying && <p className="mt-1 text-white">{chats[0].name === 'Noha AI' && chats[0].message}</p>}

        {nohaResponseProcessing && <BeatLoader color="white" className="mt-4" />}

        <p className="text-white mt-2 absolute left-3 bottom-2">Noha</p>
      </div>

      {/* Call Controls */}
      <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 w-[326px]">

      {!isAudioPlaying && (!startSpeakHint || !stopSpeakHint) && <div className="absolute bottom-[48px] left-20 bg-gray-700 text-white text-sm px-3 py-1 
      rounded-md opacity-90 group-hover:opacity-100 transition w-max">
            {!startSpeakHint ? <p> Press space bar to talk </p> : <p> Release space bar to mute </p>}
            {/* Tooltip Arrow */}
            <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-8 border-l-transparent border-r-8 border-r-transparent border-t-8 border-t-gray-700 "></div>
          </div>}

        {isMicActive ?

          <button
            onClick={toggleMic}
            className="flex items-center w-full bg-[#2D2D2D] text-white px-6 py-3 rounded-full border-[2px] border-[#0D99FF] h-[40px]"
          >
            <div className="flex flex-1 items-center justify-center">
              <Mic className="w-6 h-6" />
              <span className="font-semibold text-lg ml-2">Talking</span>
            </div>

            <div className="ml-auto flex items-center">
              <ScaleLoader color="white" height={"12px"} />
            </div>

          </button>
            :
          <button
            disabled={isAudioPlaying}
            onClick={toggleMic}
            className="flex items-center w-full 
          bg-gradient-to-b from-[#0D99FF] to-[#0A5992] text-white 
          px-6 py-3 rounded-full shadow-lg 
          hover:from-[#0A5992] hover:to-[#0D99FF] transition h-[40px]">

            <div className="flex flex-1 items-center justify-center space-x-2">
              <MicOff className="w-6 h-6" />
              <span className="font-semibold text-lg">Space bar</span>
            </div>

            <div className="ml-auto flex items-center">
              <div className=" px-2 py-1 rounded-sm text-xs">⎵</div>
            </div>

          </button>
        }

      </div>

      <div className="fixed bottom-6 right-6">
        <button className="bg-red-600 text-white p-3 rounded-full hover:bg-red-700 transition">
          <Phone className="w-6 h-6" />
        </button>
      </div>

    </div>
  );
};

export default LiveInterview;