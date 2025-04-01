'use client';
import type { StartAvatarResponse } from "@heygen/streaming-avatar";

import StreamingAvatar, {
  AvatarQuality,
  StreamingEvents,
  TaskMode,
  TaskType,
  VoiceEmotion,
} from "@heygen/streaming-avatar";

import { useEffect, useRef, useState } from "react";
import { usePrevious } from "ahooks";
import { on } from "stream";

export default function InteractiveAvatar({ nohaResponseText, onSessionStart, onStartPlaying, onStopPlaying, ref }: any) {
  
  const [isLoadingSession, setIsLoadingSession] = useState(false);
  const [isLoadingRepeat, setIsLoadingRepeat] = useState(false);
  const [stream, setStream] = useState<MediaStream>();
  const [knowledgeId] = useState<string>("");
  const [avatarId] = useState<string>("Elenora_IT_Sitting_public");
  const [language] = useState<string>("en");

  const [data, setData] = useState<StartAvatarResponse>();
  const [text, setText] = useState<string>(nohaResponseText);
  const mediaStream = useRef<HTMLVideoElement>(null);
  const avatar = useRef<StreamingAvatar | null>(null);

  function baseApiUrl() {
    return "https://api.heygen.com";
  }

  async function fetchAccessToken() {
    try {
      const response = await fetch("/api/get-access-token", {
        method: "POST",
      });
      const token = await response.text();

      console.log("Access Token:", token); // Log the token to verify

      return token;
    } catch (error) {
      console.error("Error fetching access token:", error);
    }

    return "";
  }

  async function startSession() {
    console.log('startSession>>>>>>>>')
    setIsLoadingSession(true);
    const newToken = await fetchAccessToken();

    avatar.current = new StreamingAvatar({
      token: newToken,
      basePath: baseApiUrl(),
    });
    avatar.current.on(StreamingEvents.AVATAR_START_TALKING, (e) => {
      console.log("Avatar started talking", e);
      onStartPlaying();
    });
    avatar.current.on(StreamingEvents.AVATAR_STOP_TALKING, (e) => {
      console.log("Avatar stopped talking", e);
      onStopPlaying();
    });
    avatar.current.on(StreamingEvents.STREAM_DISCONNECTED, () => {
      // console.log("Stream disconnected");
      endSession();
    });
    avatar.current?.on(StreamingEvents.STREAM_READY, (event) => {
      // console.log(">>>>> Stream ready:", event.detail);
      setStream(event.detail);
    });
    avatar.current?.on(StreamingEvents.USER_START, (event) => {
      // console.log(">>>>> User started talking:", event);
    });
    avatar.current?.on(StreamingEvents.USER_STOP, (event) => {
      // console.log(">>>>> User stopped talking:", event);
    });
    try {
      const res = await avatar.current.createStartAvatar({
        quality: AvatarQuality.Low,
        avatarName: avatarId,
        knowledgeId: knowledgeId, // Or use a custom `knowledgeBase`.
        voice: {
          rate: 1.5, // 0.5 ~ 1.5
          emotion: VoiceEmotion.EXCITED,
          // elevenlabsSettings: {
          //   stability: 1,
          //   similarity_boost: 1,
          //   style: 1,
          //   use_speaker_boost: false,
          // },
        },
        language: language,
        disableIdleTimeout: true,
      });
      
      res.current = { ...res.current, sessionData: res }
      console.log(res)
      setData(res);
      onSessionStart(res)
    } catch (error) {
      console.error("Error starting avatar session:", error);
    } finally {
      setIsLoadingSession(false);
    }
  }
  
  async function handleSpeak(latestText: string) {
    setIsLoadingRepeat(true);
    if (!avatar.current) {
      console.log("Avatar API not initialized");

      return;
    }

    await avatar.current
      .speak({ text: latestText, taskType: TaskType.REPEAT, taskMode: TaskMode.SYNC })
      .catch((e) => {
        console.log(e.message);
      });
    setIsLoadingRepeat(false);
  }

  async function handleInterrupt() {
    if (!avatar.current) {
      console.log("Avatar API not initialized");

      return;
    }
    await avatar.current.interrupt().catch((e) => {
      console.log(e.message);
    });
  }

  async function endSession() {
    await avatar.current?.stopAvatar();
    setStream(undefined);
  }

  if(ref){
    ref.current = {
      startSession,
      handleSpeak,
      handleInterrupt,
      endSession,
      isLoadingSession,
      isLoadingRepeat
  }}

  // const previousText = usePrevious(text);
  // useEffect(() => {
  //   if (!previousText && text) {
  //     avatar.current?.startListening();
  //   } else if (previousText && !text) {
  //     avatar?.current?.stopListening();
  //   }
  // }, [text, previousText]);

  useEffect(() => {
    return () => {
      endSession();
    };
  }, []);

  useEffect(() => {
    if (stream && mediaStream.current) {
      mediaStream.current.srcObject = stream;
      mediaStream.current.onloadedmetadata = () => {
        mediaStream.current!.play();
        console.log("Playing");
      };
    }
  }, [mediaStream, stream]);

  return (
      <div>
        {/* <button className="text-white" onClick={handleSpeak}>SPeak</button> */}
        <div className="flex flex-col justify-center items-center">
          {stream ? (
            <div className="h-[458px] w-[474px] justify-center items-center flex rounded-lg overflow-hidden">
              <video
                ref={mediaStream}
                autoPlay
                playsInline
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "contain",
                }}
              >
                <track kind="captions" />
              </video>
             
            </div>
          ) : isLoadingSession && (
            <div className="text-white">Loading session...</div>
          )}
        </div>
      </div>
  );
}
