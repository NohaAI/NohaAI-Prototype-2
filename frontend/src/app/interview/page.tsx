'use client'
import Feedback from "@/components/feedback";
import InterviewDetails from "@/components/InterviewDetails";
import LiveInterview from "@/components/LiveInterview";
import axios from "axios";
import { useEffect, useRef, useState } from "react";
// import { io } from "socket.io-client";

const MyPage = () => {

    const [interviewStarted, setInterviewStarted] = useState<boolean>(false);
    const [details, setDetails] = useState({} as any);
    const [callEnded, setCallEnded] = useState(false);
    const [backendServiceLink] = useState(
        // "http://localhost:5000"
        "https://apis.noha.ai"
        );
    const [userSocket, setUserSocket] = useState<any>(null);
    const [chats, setChats] = useState<Array<any>>([]);
    
    const [isMicOn, setIsMicOn] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [transcribedText, setTranscribedText] = useState("");
    const [isProcessing, setIsProcessing] = useState(false); // NEW: Processing state
    const [chatMetaData, setChatMetaData] = useState({} as any);

    const recognitionRef = useRef<any>(null);

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

    const startConnection2 = async (userDetails: any) => {
        try {
            const connectRes = await axios.get(`${backendServiceLink}/connect`);
            const initializeRes = await axios.post(`${backendServiceLink}/initialize`, { user_name: userDetails.name, user_email: userDetails.email });

            console.log('start connection', connectRes)
            console.log('initialize data', initializeRes)
            
            setChatMetaData(initializeRes.data)
            setInterviewStarted(true);
          
            updateChats(initializeRes.data.greeting);
            speakText(initializeRes.data.greeting)

        } catch (error) {
            console.error("Error in startConnection2:", error);
            throw error; 
        }
    };
    
    const disconnect2 = async() =>{
        try {
            const res = await axios.post(`${backendServiceLink}/terminate`, {
                session_state: chatMetaData.session_state, 
                chat_history : chatMetaData.chat_history, 
                assessment_payload_record: chatMetaData.assessment_payload_record
            });
            console.log('terminate', res)
        } catch (error) {
            console.error('Error on terminate', error)
        }
    }

    useEffect(()=>{
        return ()=>{
            disconnect2()
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
            const res = await axios.post(`${backendServiceLink}/chat`, reqBody);
            console.log("Received AI response", res.data);
            setChatMetaData(res.data)
            updateChats(res.data.bot_dialogue);
            speakText(res.data.bot_dialogue);

            // check if the flag is true call the terminate api
            if(res.data.termination) {
                setTimeout(() => {
                    disconnect2()
                    stopRecording();
                    setCallEnded(true);
                }, 4000);
            }
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

        window.speechSynthesis.speak(utterance);
    };

    const handleSubmit = (data: { name: string; email: string }) => {
        setDetails({ ...data });
        // startConnection(data);
        startConnection2({...data})
    };

    // const onCancelCall = () => {
    //     stopRecording();
    //     setCallEnded(true);
    //     userSocket?.disconnect();
    // };

    const onCancelCall2 = () =>{
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

        recognition.onresult = (event: any) => {
            let finalTranscript = "";
            for (let i = event.resultIndex; i < event.results.length; i++) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript + " ";
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
                    onCancelCall={onCancelCall2}
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