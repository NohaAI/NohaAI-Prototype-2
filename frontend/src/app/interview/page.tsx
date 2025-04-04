'use client'
import Feedback from "@/components/Feedback";
import InterviewDetails from "@/components/InterviewDetails";
import LiveInterview from "@/components/LiveInterview";
import axios from "axios";
import { useEffect, useRef, useState } from "react";
import { ToastContainer, toast } from "react-toastify";
// import { io } from "socket.io-client";

const MyPage = () => {

    const [interviewStarted, setInterviewStarted] = useState<boolean>(false);
    const [details, setDetails] = useState({} as any);
    const [callEnded, setCallEnded] = useState(false);
    const [backendServiceLink] = useState(
	        process.env.NEXT_PUBLIC_BACKEND_URL
        );
    const [userSocket, setUserSocket] = useState<any>(null);
    const [chats, setChats] = useState<Array<any>>([]);
    
    const [isMicOn, setIsMicOn] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [transcribedText, setTranscribedText] = useState("");
    const [isProcessing, setIsProcessing] = useState(false); // NEW: Processing state
    const [chatMetaData, setChatMetaData] = useState({} as any);
    const [nohaResponseProcessing, setNohaResponseProcessing] = useState<boolean>(false);
    const [isAudioPlaying, setIsAudioPlaying] = useState<boolean>(false);

    const recognitionRef = useRef<any>(null);
    const [isSilence, setIsSilence] = useState<boolean | null>(null)
    
    const [errorMsg, setErrorMsg] = useState<string>("");

    // const startConnection = async (userDetails: any) => {
    //     const socketConnection = io(backendServiceLink + '/guest', { transports: ["websocket"] });
    //     const greetMsg: string = `Hi ${userDetails.name}, Find an index in an array where the sum of elements to the left equals the sum to the right.`;

    //     socketConnection.on("connect", () => {
    //         console.log('Connected');
    //         if (!interviewStarted) speakText(greetMsg);
    //         setInterviewStarted(true);
    //         updateChats(greetMsg);
    //     });

    //     socketConnection.on("disconnect", () => {
    //         console.log("Client disconnected from server");
    //     });

    //     socketConnection.on("streamBack", (data) => {
    //         console.log('Received AI response');
    //         updateChats(data);
    //         speakText(data);
    //     });

    //     setUserSocket(socketConnection);
    // };


    useEffect(() => {
        if(errorMsg){
            toast(errorMsg, {
                position: 'top-center',
                autoClose: 5000,
                theme: "dark",
            })
        }
    }, [errorMsg])

    const startConnection2 = async (userDetails: any) => {
        try {
            const connectRes = await axios.get(`${backendServiceLink}/connect`);
            const initializeRes = await axios.post(`${backendServiceLink}/initialize`, { user_name: userDetails.name, user_email: userDetails.email, live_code: userDetails.live_code });

            console.log('start connection', connectRes)
            console.log('initialize data', initializeRes)
            
            setChatMetaData(initializeRes.data)
            setInterviewStarted(true);
          
            updateChats(initializeRes.data.session_state.bot_dialogue);
            speakText(initializeRes.data.session_state.bot_dialogue)

        } catch (error: any) {
            let errorMessage = "Unknown error occurred";
        
            // Check if the error has a response (API error)
            if (error.response && error.response.data && error.response.data.detail) {
                errorMessage = error.response.data.detail; // Extract the "detail" field
            } else if (error.message) {
                errorMessage = error.message;
            }
        
            setErrorMsg(errorMessage);
            console.error("Error in startConnection2:", errorMessage);
            throw error;
        }        
    };
    
    const disconnect2 = async() =>{
        try {
            const res = await axios.post(`${backendServiceLink}/terminate`, {
                session_state: chatMetaData.session_state, 
                chat_history : chatMetaData.chat_history, 
                assessment: chatMetaData.assessment
            });
            console.log('terminate', res)
        } catch (error) {
            console.error('Error on terminate', error)
        }
    }

    useEffect(()=>{
        return ()=>{
            if(interviewStarted) disconnect2()
        }
    }, [])

    const handleChat = async (data: { text: string }) => {
        try {
            setNohaResponseProcessing(true);
            delete chatMetaData.message;
            delete chatMetaData.greeting;
            delete chatMetaData.termination;

            // Directly update the candidate_dialogue field in chatMetaData
            console.log("RMS=>:data.text");
            chatMetaData.session_state.candidate_dialogue = data.text;
            const lastIndex = chatMetaData.chat_history.length - 1;
            if (lastIndex >= 0) {  // Ensure chat_history is not empty
                 chatMetaData.chat_history[lastIndex].candidate_dialogue = data.text;
            }
            console.log("rms=>:chatMetaData:", chatMetaData);

            const res = await axios.post(`${backendServiceLink}/chat`, chatMetaData);
            setNohaResponseProcessing(false)
            console.log("Received Noha backend AI response", res.data);
            
            setChatMetaData(res.data)
            updateChats(res.data.session_state.bot_dialogue);
            
            speakText(res.data.session_state.bot_dialogue, { termination:  res.data.session_state.termination })


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

    const speakText = (text: string, info?: any) => {
            
        if (!window.speechSynthesis) {
            console.error("Speech synthesis is not supported in this browser.");
            return;
        }
        window.speechSynthesis.cancel(); // Stop any ongoing speech

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "en-US";
        utterance.rate = 0.9;
        utterance.pitch = 1.2;

        const voices = window.speechSynthesis.getVoices();
        // Try to find a female voice
        const femaleVoice = voices.find((voice) =>  voice.name.toLowerCase().includes("female") || voice.name.toLowerCase().includes("samantha"))
        if (femaleVoice) {
            utterance.voice = femaleVoice;
        } else if (voices.length > 0) {
            utterance.voice = voices[0]; // Fallback to any available voice
        }

        console.log('femaleVoice', femaleVoice)

        utterance.onstart = () =>{
            console.log("Speech started");
            setIsAudioPlaying(true)
        }

        utterance.onend = () => {
            console.log("Speech finished");
            setIsAudioPlaying(false)
            if(info?.termination) {
                disconnect2()
                stopRecording();
                setCallEnded(true);
            }
        };

        if (voices.length === 0) {
            window.speechSynthesis.onvoiceschanged = () => {
                speakText(text, info);
            };
        } else {
            window.speechSynthesis.speak(utterance);
        }
};

    const handleSubmit = async (data: { name: string; email: string, live_code: string }) => {
        console.log("Form submitted with data:", typeof(data.live_code));
        setDetails({ ...data });
        // startConnection(data);
        await startConnection2({...data})
    };

    // const onCancelCall = () => {
    //     stopRecording();
    //     setCallEnded(true);
    //     userSocket?.disconnect();
    // };

    const onCancelCall2 = () =>{
        window?.speechSynthesis?.cancel()
        stopRecording();
        setCallEnded(true);
        disconnect2()
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
    
        let silenceTimeout: NodeJS.Timeout; // Timer for detecting silence
    
        recognition.onresult = (event: any) => {
            clearTimeout(silenceTimeout); // Reset timer on speech
            console.log("No silence"); // Log when speech is detected
            setIsSilence(false)

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
    
            // Restart the silence detection timer
            silenceTimeout = setTimeout(() => {
                console.log("Silence"); // Log silence after 3 seconds of inactivity
                setIsSilence(true)
            }, 500); // Adjust time to define "silence" period
        };
    
        recognition.onend = () => {
            console.log("Recognition ended, processing final text...");
            setIsProcessing(false); // Hide dot when processing is done
            clearTimeout(silenceTimeout); // Ensure timer is cleared when recognition stops
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
        <ToastContainer/>
        {/* Display on medium and large devices */}
        <div className="hidden lg:block">
            {!callEnded && (
            !interviewStarted ? (
                <InterviewDetails onSubmit={handleSubmit} />
            ) : (
                <LiveInterview
                    chats={chats}
                    name={details.name}
                    onCancelCall={onCancelCall2}
                    userSocket={userSocket}
                    isMicOn={isMicOn}
                    startRecording={startRecording}
                    stopRecording={stopRecording}
                    isRecording={isRecording}
                    nohaResponseProcessing={nohaResponseProcessing}
                    isProcessing={isProcessing}
                    isAudioPlaying={isAudioPlaying}
                    isSilence={isSilence}
                />
            )
            )}
            {callEnded && <Feedback sendFeedback={sendFeedback} />}
        </div>
            
        {/* Display on small devices */}
        <div className="block lg:hidden flex items-center justify-center h-screen bg-gray-100">
            <p className="text-center text-2xl font-bold text-gray-800 p-4">
            This application is supported on desktops only.
            </p>
        </div>        
        </>
    );
};

export default MyPage;
