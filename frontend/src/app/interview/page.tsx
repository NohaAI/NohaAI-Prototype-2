'use client'
import Feedback from "@/components/feedback";
import InterviewDetails from "@/components/InterviewDetails";
import LiveInterview from "@/components/LiveInterview";
import axios from "axios";
import { use, useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";

const MyPage = () => {

    const [interviewStarted, setInterviewStarted] = useState<boolean>(false);
    const [details, setDetails] = useState({} as any);
    const [callEnded, setCallEnded] = useState(false);
    const [backendServiceLink] = useState(
        "http://localhost:2000"
        // "https://apis.noha.ai"
        );
    const [userSocket, setUserSocket] = useState<any>(null);
    const [chats, setChats] = useState<Array<any>>([]);
    
    const [isMicOn, setIsMicOn] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [transcribedText, setTranscribedText] = useState("");
    const [isProcessing, setIsProcessing] = useState(false); // NEW: Processing state
    const [chatMetaData, setChatMetaData] = useState({} as any);

    const recognitionRef = useRef<any>(null);

    const startConnection = async (userDetails: any) => {
        const socketConnection = io(backendServiceLink + '/guest', { transports: ["websocket"] });

        socketConnection.on("connect", () => {
            console.log('Connected');
            setInterviewStarted(true);
            socketConnection.emit('initialize', { user_email: userDetails.email, user_name: userDetails.name });
        });

        socketConnection.on('initialize', (data: any) => {
            console.log(' initialize Received AI response', data);
            setChatMetaData(data);
            updateChats(data.greeting);
            speakText(data.greeting);
        });

        socketConnection.on("disconnect", () => {
            console.log("Client disconnected from server");
        });

        socketConnection.on("chat", (chatResponse: any) => {
            console.log('Chat  Received AI response', chatResponse);

            setChatMetaData(() => chatResponse)
            updateChats(chatResponse.bot_dialogue);
            speakText(chatResponse.bot_dialogue);

            // if(chatResponse.termination) {
            //     setTimeout(() => {
            //         disconnect()
            //         stopRecording();
            //         setCallEnded(true);
            //     }, 4000);
            // }

        });

        setUserSocket(socketConnection);
    };
    
    const disconnect = async() =>{
        const reqBody = {
            session_state: chatMetaData.session_state,
            chat_history: chatMetaData.chat_history,
            assessment_payload_record: chatMetaData.assessment_payload_record
        }
        userSocket?.emit('terminate', reqBody);
    }

    useEffect(()=>{
        return ()=>{
            disconnect()
        }
    }, [])

    const handleChat = async (data: { text: string }) => {
        try {
            delete chatMetaData.message;
            delete chatMetaData.greeting;
            delete chatMetaData.termination;

            const reqBody = {
                ...chatMetaData,
                "candidate_dialogue": data.text
            }

            userSocket.emit('chat', reqBody);
            
        } catch (error) {
            console.error("Error in handleStreamBack:", error);
        }
    };

    const updateChats = (msg: string, sender = "Noha AI") => {
        setChats((prevChats) => [
            { name: sender, message: msg },
            ...prevChats,
        ]);
    };

    const speakText = (text: string): void => {
        if (!window.speechSynthesis) {
            console.error("Speech synthesis is not supported in this browser.");
            return;
        }

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "en-IN";
        utterance.rate = 1;
        utterance.pitch = 1;

            // Event when speech starts
    utterance.onstart = () => {
        console.log("Speech started");
    };
 
    // Event when speech ends
    utterance.onend = () => {
        console.log("Speech finished", chatMetaData);
        if(chatMetaData.termination) {
                disconnect()
                stopRecording();
                setCallEnded(true);
        }
    };


        window.speechSynthesis.speak(utterance);
    };

    const handleSubmit = (data: { name: string; email: string }) => {
        setDetails({ ...data });
        startConnection({...data})
    };

    const onCancelCall = () =>{
        stopRecording();
        setCallEnded(true);
        disconnect()
    }

    const startRecording = () => {
        setIsMicOn(true);
        setIsRecording(true);
        setIsProcessing(true); // Show dot on mic icon
    
        if (!("webkitSpeechRecognition" in window)) {
            alert("Your browser does not support speech recognition. Please try Chrome.");
            return;
        }
    
        const recognition = new (window as any).webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = "en-US";
        recognition.maxAlternatives = 3; // Get up to 3 alternative transcriptions
    
        recognition.onresult = (event: any) => {
            let finalTranscript = "";
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                if (event.results[i].isFinal) {
                    const alternatives = event.results[i]; // Get all alternatives
                    
                    // Find the alternative with the highest confidence
                    let bestAlternative = alternatives[0]; // Default to the first
                    for (let j = 1; j < alternatives.length; j++) {
                        if (alternatives[j].confidence > bestAlternative.confidence) {
                            bestAlternative = alternatives[j];
                        }
                    }
    
                    finalTranscript += bestAlternative.transcript + " "; // Pick the most confident result
    
                    // Log all alternatives and their confidence scores
                    console.log("Alternatives:");
                    for (let j = 0; j < alternatives.length; j++) {
                        console.log(`Alternative ${j + 1}: "${alternatives[j].transcript}" (Confidence: ${alternatives[j].confidence})`);
                    }
                    console.log(`✅ Selected: "${bestAlternative.transcript}" (Confidence: ${bestAlternative.confidence})`);
                }
            }
    
            setTranscribedText((prev) => prev + finalTranscript);
        };
    
        recognition.onend = () => {
            console.log("Recognition ended, processing final text...");
            setIsProcessing(false); // Hide dot when processing is done
        };
    
        recognitionRef.current = recognition;
        recognition.start();
    };
    

    const stopRecording = () => {
        setIsRecording(false);
        setIsMicOn(false);

        if (recognitionRef.current) {
            recognitionRef.current.stop();
        }
    };

    useEffect(() => {
        if (!isRecording && !isProcessing && transcribedText.trim() !== "") {
            console.log('Emitting transcribed text:', transcribedText);
            // userSocket?.emit('STOP', transcribedText);
            handleChat({ text: transcribedText })
            updateChats(transcribedText, "Candidate");
            setTranscribedText(""); // Reset after emitting
        }
    }, [isRecording, isProcessing]);

    const sendFeedback = async (rating: number) => {
        window.location.reload();
        // try {
        //     const response = await axios.post("http://localhost:5000/feedback", { rating });
        //     console.log("Response:", response.data);
        //     return response.data;
        // } catch (error: any) {
        //     console.error("Error submitting feedback:", error.response ? error.response.data : error.message);
        //     throw error;
        // }
    };

    return (
        <>
            {!callEnded && (!interviewStarted ? (
                <InterviewDetails onSubmit={handleSubmit} />
            ) : (
                <LiveInterview
                    chats={chats}
                    name={details.name}
                    onCancelCall={onCancelCall}
                    userSocket={userSocket}
                    isMicOn={isMicOn}
                    startRecording={startRecording}
                    stopRecording={stopRecording}
                    isRecording={isRecording}
                    isProcessing={isProcessing} // Pass processing state to show dot on mic
                />
            ))}
            {callEnded && <Feedback sendFeedback={sendFeedback} />}
        </>
    );
};

export default MyPage;