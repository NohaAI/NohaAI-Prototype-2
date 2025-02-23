"use client";
import { useEffect, useState, useRef } from "react";
import { io } from "socket.io-client";

const VideoInterview = () => {
    const [backendServiceLink] = useState("http://localhost:2000");
    const [userSocket, setUserSocket] = useState(null);
    const [isRecording, setIsRecording] = useState(false);
    const [isMuted, setIsMuted] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);

    const mediaRecorderRef = useRef(null);
    const audioStreamRef = useRef(null);
    const audioTrackRef = useRef(null);
    const audioPlayerRef = useRef(null);
    const mediaSourceRef = useRef(null);
    const sourceBufferRef = useRef(null);
    const audioQueueRef = useRef([]);

    useEffect(() => {
        startConnection();
    }, []);

    const startConnection = async () => {
        const socketConnection = io(backendServiceLink + "/guest", {
            transports: ["websocket"],
        });

        socketConnection.on("streamBack", (audioData) => {
            // console.log(audioData)
            queueAudioData(audioData);
        });

        setUserSocket(socketConnection);
    };

    const checkMicrophonePermission = async () => {
        try {
            const permissionStatus = await navigator.permissions.query({ name: "microphone" });
            if (permissionStatus.state === "denied") {
                alert("Microphone access is denied. Please allow access in your browser settings.");
                return false;
            }
            return true;
        } catch (error) {
            console.warn("Microphone permission query not supported, trying direct access.");
            return true;
        }
    };

    const startRecording = async () => {
        const hasPermission = await checkMicrophonePermission();
        if (!hasPermission) return;

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            audioStreamRef.current = stream;
            audioTrackRef.current = stream.getAudioTracks()[0];

            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0 && userSocket && !isMuted) {
                    userSocket.emit("audioStream", event.data);
                }
            };

            mediaRecorder.start(100);
            setIsRecording(true);
            setIsSpeaking(true);

        } catch (error) {
            console.error("Error accessing microphone:", error);
            alert("Failed to access microphone. Please check browser settings.");
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
        }
        if (audioStreamRef.current) {
            audioStreamRef.current.getTracks().forEach((track) => track.stop());
        }

            
        setIsRecording(false);
        setIsSpeaking(false);

        mediaSourceRef.current.endOfStream()
    

        if (userSocket) {
            console.log('stopRecording')
            userSocket.emit("stopRecording");
        }
    };

    /** ✅ Handles continuous streaming by queueing and appending chunks */
    const queueAudioData = (audioData) => {
        if (!(audioData instanceof Uint8Array || audioData instanceof ArrayBuffer)) {
            console.error("Invalid audio data received:", audioData);
            return;
        }

        const uint8Array = new Uint8Array(audioData);
        audioQueueRef.current.push(uint8Array);

        if (!mediaSourceRef.current || mediaSourceRef.current.readyState !== "open") {
            initializeMediaSource();
        } else {
            appendAudioBuffer();
        }
    };

    /** ✅ Initializes MediaSource for streaming playback */
    const initializeMediaSource = () => {
        if (!audioPlayerRef.current) return;

        mediaSourceRef.current = new MediaSource();
        audioPlayerRef.current.src = URL.createObjectURL(mediaSourceRef.current);

        mediaSourceRef.current.addEventListener("sourceopen", () => {
            const mediaSource = mediaSourceRef.current;
            if (!mediaSource) return;

            sourceBufferRef.current = mediaSource.addSourceBuffer('audio/webm; codecs="opus"');

            sourceBufferRef.current.addEventListener("updateend", appendAudioBuffer);

            appendAudioBuffer();
        });

        console.log(audioPlayerRef)
        audioPlayerRef.current.play().catch((err) => console.log("Playback error:", err));
    };

    /** ✅ Appends buffered chunks to SourceBuffer */
    const appendAudioBuffer = () => {
        if (!sourceBufferRef.current || sourceBufferRef.current.updating || audioQueueRef.current.length === 0) {
            return;
        }

        const chunk = audioQueueRef.current.shift();
        sourceBufferRef.current.appendBuffer(chunk);
    };

    return (
        <div>
            <p>FROM VIDEO</p>
            <button onClick={isRecording ? stopRecording : startRecording}>
                {isRecording ? "Stop Recording" : "Start Recording"}
            </button>

            {isSpeaking && <p>AI is speaking...</p>}
            <audio ref={audioPlayerRef} controls style={{ display: "none" }}></audio>
        </div>
    );
};

export default VideoInterview;
