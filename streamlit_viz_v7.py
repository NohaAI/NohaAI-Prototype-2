import streamlit as st
import time
from datetime import datetime
import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as plt
import asyncio
import os
import json
from src.schemas.endpoints.schema import EvaluateAnswerRequest
from src.services.workflows import answer_evaluator
from src.services.workflows.hint_generator import generate_hint
from src.dao.question import get_question_metadata
from src.dao.chat_history import get_chat_history
from src.dao.interview import get_interview_metadata
from src.dao.chat_history import add_chat_history
from src.dao.chat_history import delete_chat_history
from src.api.endpoints import greet_candidate
from src.services.workflows.policy_violation import check_policy_violation
from src.services.workflows.candidate_dialogue_classifier import classify_candidate_dialogue
from src.services.workflows.bot_dialogue_generatorv2 import generate_dialogue 
from src.dao.chat_history import batch_insert_chat_history
from src.services.workflows.answer_classifer import classify_candidate_answer

# Function to fetch chat history asynchronously
async def async_get_chat_history(interview_id):
    return await get_chat_history(interview_id)
# Function to verify candidate responses that were accepted as answers
async def async_classify_candidate_answer(question, candidate_answer, chat_history, follow_up_question=None):
    return await classify_candidate_answer(question, candidate_answer, chat_history, follow_up_question)
# Function to delete and reset chat history for a specific interview_id asynchronously
async def async_delete_chat_history(interview_id):
    return await delete_chat_history(interview_id)
# add_chat_history(interview_id,initial_question_metadata['question_id'],hint,candidate_response,'hint_question')
async def async_add_chat_history(interview_id, question_id, question, answer, hint_type):
    return await add_chat_history(interview_id, question_id, question, answer, hint_type)

# Function that prepares a greet interview with the user_name
async def async_greet_candidate(user_id):
    return await greet_candidate(user_id)

# Function to get interview_metadata asynchronously
async def async_get_interview_metadata(interview_id):
    return await get_interview_metadata(interview_id)

async def async_get_question_metadata(question_id):
    return await get_question_metadata(question_id)

async def async_check_policy_violation(question, answer, interim_chat_history, hint=None):
    return await check_policy_violation(question, answer, interim_chat_history, hint)

# Function that prepares a generate_hint call
async def async_generate_hint(chat_history, meta_payload, hint_list):
    return await generate_hint(chat_history, meta_payload, hint_list)

async def async_classify_candidate_dialogue(question, answer, interim_chat_history):
    return await classify_candidate_dialogue(question, answer, interim_chat_history)

async def async_evaluate_answer(evaluation_input):
    return await answer_evaluator.evaluate_answer(evaluation_input)

async def async_batch_insert_chat_history(interview_id,question_id,chat_history_data):
    return await batch_insert_chat_history(interview_id,question_id,chat_history_data)
    
async def async_generate_dialogue(label, chat_history, answer, question, hint_count,answer_evaluation=None, previous_bot_dialogue=None,rationale=None):
    return await generate_dialogue(label, chat_history, answer, question, hint_count, answer_evaluation, previous_bot_dialogue,rationale)
# Function to run the async function and return results



def write_to_chat_history_csv(filename, data):
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write header if file does not exist
        if not file_exists:
            writer.writerow(["Date", "Chat_History"])
        
        # Write data
        writer.writerow(data)

# Example usage

def run_async(func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(func)

# define layout

# Set the page configuration to use wide mode
st.set_page_config(page_title="Your App Title", layout="wide")

app_tab,rationale_evaluation_tab=st.tabs(["Application", "Evaluation and Rationale"])
with app_tab:
    row1 = st.columns([0.70, 0.30], gap="large")
    row2 = st.columns([0.70, 0.30], gap="large")
    row3 = st.columns([0.70, 0.30], gap="large")
    topleft = row1[0]
    topright = row1[1]
    midleft = row2[0]
    midright = row2[1]
    bottomleft = row3[0]
    bottomright = row3[1]

    if "turn" in st.session_state and st.session_state.conclude == True:
        run_async(async_batch_insert_chat_history(st.session_state.meta_payload.interview_id, st.session_state.meta_payload.question_id,st.session_state.interim_chat_history))
        placeholder_ml=midleft.empty()
        chat_history_csv_data=[datetime.now().strftime("%d %b %Y - %I:%M %p"),st.session_state.messages]
        write_to_chat_history_csv('interview_sessions.csv',chat_history_csv_data)
        placeholder_ml.progress(0, "Thank you for your time ...")
        time.sleep(2)
        placeholder_ml.progress(20, "Thank you for your time ...")
        time.sleep(1)
        placeholder_ml.progress(40, "Thank you for your time ...")
        time.sleep(1)
        placeholder_ml.progress(60, "Thank you for your time ...")
        time.sleep(1)
        placeholder_ml.progress(100, "Thank you for your time ...")
        time.sleep(2)
        placeholder_ml.empty()
        placeholder_ml.markdown(f'<p style="font-size: 24px;"><strong>INTERVIEW RESULTS</strong>: {round(st.session_state.final_score, 2)}</p>', unsafe_allow_html=True)
        
        placeholder_bl=bottomleft.empty()
        placeholder_bl = bottomleft.container(height=420, border=True)
        chat_history_str = datetime.now().strftime("**CHAT HISTORY** - (%d %b %Y) - (%I:%M %p)")
        placeholder_bl.write(chat_history_str)
        topleft.write("**NOHA AI-BOT**")
        placeholder_tl = topleft.empty()
        with placeholder_tl.container(height=240, border=True):
            for msg in st.session_state.messages:
                #print(st.session_state.messages)
                if msg["role"] == "user":
                    placeholder_tl.chat_message("user").markdown(msg["content"])
                    # bottomleft.write(msg['content'])
                    placeholder_bl.markdown(f"<div class='scrollable-container'><b>Candidate:</b> { msg['content']}</div>", unsafe_allow_html=True)
                if msg["role"] == "bot":
                    placeholder_tl.chat_message("assistant").markdown(msg["content"])
                    # bottomleft.write(msg['content'])
                    placeholder_bl.markdown(f"<div class='scrollable-container'><b>Noha-bot:</b> { msg['content']}</div>", unsafe_allow_html=True)
        st.stop()

    #for dev
    MAX_TURNS=50
    SCORE_THRESHOLD=100.0
    MAX_CONTIGUOUS_GUARDRAIL_COUNT=100
    MAX_GUARDRAIL_COUNT=100
    MAX_CONTIGUOUS_UNACCEPTABLE_ANSWER_COUNT=100
    #for prod/demo
    # MAX_TURNS=12
    # SCORE_THRESHOLD=5.0
    # MAX_CONTIGUOUS_GUARDRAIL_COUNT=4
    # MAX_GUARDRAIL_COUNT=8

#FIXME: Exception: Unexpected error in evaluation process: 'Subcriterion question' 

    ###### Some initial payload and variables for facilitation have been defined; refactor required later possibly; review
    # Initialize chat messages and other artefacts if not already done
    if "messages" not in st.session_state:
        st.session_state.interim_chat_history=[]
        st.session_state.rationale_logs = []  # logs containing rationale etc. to be printed on the second tab
        st.session_state.hint_count=[0,0,0,0,0]
        st.session_state.turn = 0
        st.session_state.previous_bot_dialogue=""
        st.session_state.assessment_payload=None
        st.session_state.guardrails_count=0
        st.session_state.contiguous_unacceptable_answer_count=0
        st.session_state.conversation_turn=0
        st.session_state.contigous_guardrails_count=0
        st.session_state.conclude=False
        st.session_state.call_for_termination=False
        st.session_state.conclude_message=""
        st.session_state.class_label=None #added class_label so it could be accessed globally across tabs
        # Create an instance of EvaluateAnswerRequest; call it st.session_state.meta_payload for now as it is required throughout
        st.session_state.meta_payload = EvaluateAnswerRequest(
            question_id=1, # Question 10 is chosen for now; later it needs to come from some selection criteria
            question="What is your favorite programming language?",
            interview_id=1,
            answer="Python",
            eval_distribution=[0, 0, 0, 0, 0, 0, 0]
        )
        st.session_state.eval_distribution = st.session_state.meta_payload.eval_distribution
        st.session_state.final_score = 0
        chat_history = run_async(async_get_chat_history(st.session_state.meta_payload.interview_id))
        if chat_history:
            run_async(async_delete_chat_history(st.session_state.meta_payload.interview_id))
        greeting = "Hello Arun, I am Noha. I'm your interviewer today. We have planned a data structures and algorithms interview with you, are you good to go?"
        #Hi I am Noha I take care of DSA questions 
        st.session_state.meta_payload.question=greeting
        st.session_state.messages = [{"role": "bot", "content": greeting}]

    placeholder_bl = bottomleft.container(height=420, border=True)
    chat_history_str = datetime.now().strftime("**CHAT HISTORY** - (%d %b %Y) - (%I:%M %p)")
    placeholder_bl.write(chat_history_str)

    if st.session_state.turn == 0:
        # Display chat messages using a for loop
        topleft.write("**NOHA AI-BOT**")
        placeholder_tl = topleft.empty()
        with placeholder_tl.container(height=240, border=True):
            for msg in st.session_state.messages:
                print(st.session_state.messages)
                if msg["role"] == "user":
                    placeholder_tl.chat_message("user").markdown(msg["content"])
                if msg["role"] == "bot":
                    placeholder_tl.chat_message("assistant").markdown(msg["content"])

    # Chat input
    placeholder_ml=midleft.empty()
    container_ml = placeholder_ml.container(height=100, border=False)
    container_ml.write("**CANDIDATE**")
    user_input = container_ml.chat_input("Type your message here...")

    if user_input:
        start_time=time.time()
        # Add the user message to the session state and update_chat_history
        if st.session_state.turn==0:
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.interim_chat_history.append({"greeting" : st.session_state.meta_payload.question, "answer" : user_input})
            st.session_state.turn += 1
            st.session_state.conversation_turn += 1
            # get question_id from the initialised st.session_state.meta_payload; question_id == 10 for now, to be generalised later
            question_id = st.session_state.meta_payload.question_id 
            initial_question_metadata = run_async(async_get_question_metadata(question_id))
            st.session_state.initial_question = initial_question_metadata['question']
            st.session_state.meta_payload.question = st.session_state.initial_question
            st.session_state.messages.append({"role": "bot", "content": st.session_state.initial_question})
            st.session_state.previous_bot_dialogue=st.session_state.initial_question
        elif (st.session_state.turn == 1):
            st.session_state.messages.append({"role": "user", "content": user_input})
            if st.session_state.previous_bot_dialogue==st.session_state.initial_question:
                st.session_state.interim_chat_history.append({"technical": st.session_state.previous_bot_dialogue,"answer": user_input})
            else:
                st.session_state.interim_chat_history.append({"reciprocation": st.session_state.previous_bot_dialogue,"answer": user_input})
            classify_candidate_dialogue=run_async(async_classify_candidate_dialogue(st.session_state.initial_question,user_input,st.session_state.interim_chat_history))
            classify_candidate_dialogue=json.loads(classify_candidate_dialogue.content)
            class_label=classify_candidate_dialogue[0]
            st.session_state.class_label = class_label
            if class_label == 'clarification(open)' or class_label == 'clarification(specific)' or class_label == 'request(guidance)' or class_label == 'uncertainty' or  class_label == 'request(termination)':
                if class_label != 'request(termination)':
                    st.session_state.guardrails_count+=1
                    st.session_state.contigous_guardrails_count+=1
                else:    
                    st.session_state.call_for_termination=True
            if class_label != 'technical' and class_label != 'clarification(specific)':
                #label, chat_history, answer, question,answer_evaluation, hint_count, previous_bot_dialogue=None
                bot_dialogue=run_async(async_generate_dialogue(class_label,st.session_state.interim_chat_history,user_input, st.session_state.initial_question,st.session_state.hint_count,st.session_state.assessment_payload,None,None))
                bot_dialogue=json.loads(bot_dialogue.content)
                st.session_state.previous_bot_dialogue=bot_dialogue[1]
                print("######################################################################################################")
                print(f"USER INPUT : {user_input}")
                print(f"CLASS : {class_label}")
                print(f"RATIONALE_CLASSIFICATION : {classify_candidate_dialogue[1]}")
                print(f"RESPONSE : {bot_dialogue[1]}")
                print(f"RATIONALE_RESPONSE : {bot_dialogue[2]}")
                print("######################################################################################################")
                st.session_state.messages.append({"role": "bot", "content": bot_dialogue[1]})
            
                st.session_state.conversation_turn += 1
            else:
                st.session_state.contigous_guardrails_count=0
                candidate_answer_classification_payload=run_async(async_classify_candidate_answer(st.session_state.meta_payload.question, user_input, st.session_state.interim_chat_history))
                candidate_answer_label=json.loads(candidate_answer_classification_payload.content)[0]
                candidate_answer_classification_rationale=json.loads(candidate_answer_classification_payload.content)[1]
                print("######################################################################################################")
                print(f"USER INPUT : {user_input}")
                print(f"CANDIDATE ANSWER LABEL : {candidate_answer_label}")
                print(f"RATIONALE CANDIDATE ANSWER: {candidate_answer_classification_rationale}")
                print("######################################################################################################")

                candidate_answer_labels_not_tobe_evaluated=['incorrect','clarity(unclear)','verification(not_done)']
                if candidate_answer_label not in candidate_answer_labels_not_tobe_evaluated:
                    st.session_state.meta_payload.answer = user_input
                    assessment_payload = run_async(async_evaluate_answer(st.session_state.meta_payload))
                    st.session_state.assessment_payload=assessment_payload
                    st.session_state.meta_payload.eval_distribution = assessment_payload['criteria_scores']
                    st.session_state.eval_distribution = assessment_payload['criteria_scores']
                    st.session_state.final_score = assessment_payload['final_score']
                else:
                    st.session_state.contiguous_unacceptable_answer_count+=1
                st.session_state.turn += 1
                st.session_state.conversation_turn += 1
                
                bot_dialogue=run_async(async_generate_dialogue(candidate_answer_label,st.session_state.interim_chat_history,user_input, st.session_state.initial_question,st.session_state.hint_count,st.session_state.assessment_payload,st.session_state.meta_payload.question,candidate_answer_classification_rationale))
                bot_dialogue_rationale=json.loads(bot_dialogue.content)[2]
                bot_dialogue_subcriterion_id=json.loads(bot_dialogue.content)[3]
                bot_dialogue=json.loads(bot_dialogue.content)[1]
                print("#####################################################################")
                print(f" CANDIDATE ANSWER LABEL : {candidate_answer_label}")
                print(f" BOT FOLLOW UP DIALOGUE : {bot_dialogue}")
                print(f" RATIONALE : {bot_dialogue_rationale}")
                print(f" SUBCRITERION ID : {bot_dialogue_subcriterion_id}")
                print("#####################################################################")
                st.session_state.previous_bot_dialogue=bot_dialogue
                #bot_dialogue=bot_dialogue.content
                st.session_state.meta_payload.question = bot_dialogue
                st.session_state.messages.append({"role": "bot", "content": bot_dialogue})
        else:
            st.session_state.messages.append({"role": "user", "content": user_input})
            if st.session_state.previous_bot_dialogue==st.session_state.meta_payload.question:
                st.session_state.interim_chat_history.append({"hint": st.session_state.previous_bot_dialogue,"answer": user_input})
            else:
                st.session_state.interim_chat_history.append({"reciprocation": st.session_state.previous_bot_dialogue,"answer": user_input})
            classify_candidate_dialogue=run_async(async_classify_candidate_dialogue(st.session_state.meta_payload.question,user_input,st.session_state.interim_chat_history))
            classify_candidate_dialogue=json.loads(classify_candidate_dialogue.content)
            class_label=classify_candidate_dialogue[0]
            st.session_state.class_label = class_label
            if class_label == 'clarification(open)' or class_label == 'clarification(specific)' or class_label == 'request(guidance)' or class_label == 'uncertainty' or  class_label == 'request(termination)':
                if class_label != 'request(termination)':
                    st.session_state.guardrails_count+=1
                    st.session_state.contigous_guardrails_count+=1
                else:    
                    st.session_state.call_for_termination=True
            if class_label != 'technical' and class_label != 'clarification(specific)':
                st.session_state.interim_chat_history.append({"reciprocation": st.session_state.previous_bot_dialogue,"answer": user_input})

                bot_dialogue=run_async(async_generate_dialogue(class_label,st.session_state.interim_chat_history,user_input, st.session_state.initial_question,st.session_state.hint_count,st.session_state.assessment_payload,st.session_state.meta_payload.question,None))
                bot_dialogue=json.loads(bot_dialogue.content)
                st.session_state.previous_bot_dialogue=bot_dialogue[1]
                print("######################################################################################################")
                print(f"USER INPUT : {user_input}")
                print(f"CLASS : {class_label}")
                print(f"RATIONALE_CLASSIFICATION : {classify_candidate_dialogue[1]}")
                print(f"RESPONSE : {bot_dialogue[1]}")
                print(f"RATIONALE_RESPONSE : {bot_dialogue[2]}")
                print("######################################################################################################")
                st.session_state.messages.append({"role": "bot", "content": bot_dialogue[1]})
                st.session_state.turn += 1
                st.session_state.conversation_turn += 1
            else:
                candidate_answer_classification_payload=run_async(async_classify_candidate_answer(st.session_state.meta_payload.question, user_input, st.session_state.interim_chat_history))
                candidate_answer_label=json.loads(candidate_answer_classification_payload.content)[0]
                candidate_answer_classification_rationale=json.loads(candidate_answer_classification_payload.content)[1] 
                print("######################################################################################################")
                print(f"USER INPUT : {user_input}")
                print(f"CANDIDATE ANSWER LABEL : {candidate_answer_label}")
                print(f"RATIONALE CANDIDATE ANSWER: {candidate_answer_classification_rationale}")
                print("######################################################################################################")

                #st.session_state.interim_chat_history.append({"hint": st.session_state.meta_payload.question, "answer": user_input})

                # ALGO: assessment_payload = evaluate_answer(evaluation_answer_payload)
                candidate_answer_labels_not_tobe_evaluated=['incorrect','clarity(unclear)','verification(not_done)','verification(clarification)']
                if candidate_answer_label not in candidate_answer_labels_not_tobe_evaluated:
                    st.session_state.meta_payload.answer = user_input
                    assessment_payload = run_async(async_evaluate_answer(st.session_state.meta_payload))
                    st.session_state.assessment_payload=assessment_payload
                    st.session_state.meta_payload.eval_distribution = assessment_payload['criteria_scores']
                    st.session_state.eval_distribution = assessment_payload['criteria_scores']
                    st.session_state.final_score = assessment_payload['final_score']
                else:
                    st.session_state.contiguous_unacceptable_answer_count+=1
                st.session_state.turn += 1
                st.session_state.conversation_turn += 1
                
                bot_dialogue=run_async(async_generate_dialogue(candidate_answer_label,st.session_state.interim_chat_history,user_input, st.session_state.initial_question,st.session_state.hint_count,st.session_state.assessment_payload,st.session_state.meta_payload.question,candidate_answer_classification_rationale))
                
                bot_dialogue_rationale=json.loads(bot_dialogue.content)[2]
                bot_dialogue_subcriterion_id=json.loads(bot_dialogue.content)[3]
                bot_dialogue=json.loads(bot_dialogue.content)[1]
                print("#####################################################################")
                print(f" CANDIDATE ANSWER LABEL : {candidate_answer_label}")
                print(f" BOT FOLLOW UP DIALOGUE : {bot_dialogue}")
                print(f" RATIONALE : {bot_dialogue_rationale}")
                print(f" SUBCRITERION ID : {bot_dialogue_subcriterion_id}")
                print("#####################################################################")
                st.session_state.previous_bot_dialogue=bot_dialogue
                #bot_dialogue=bot_dialogue.content
                st.session_state.meta_payload.question = bot_dialogue
                st.session_state.messages.append({"role": "bot", "content": bot_dialogue})

        end_time=time.time()
        latency=(end_time-start_time)

        if(("turn" in st.session_state and "final_score" in st.session_state) and (st.session_state.final_score > SCORE_THRESHOLD)):
            st.session_state.conclude=True      
            st.session_state.conclude_message="Since you have solved this question, can you now start writing code for it?"
            st.session_state.meta_payload.question = st.session_state.conclude_message
            st.session_state.messages.append({"role": "bot", "content": st.session_state.conclude_message})
            st.rerun() 
        if(("turn" in st.session_state and "final_score" in st.session_state) and (st.session_state.conversation_turn > MAX_TURNS)):
            st.session_state.conclude=True      
            st.session_state.conclude_message="We appreciate your effort on the problem! Now, can you code it for us? Let us know when you're ready."
            st.session_state.meta_payload.question = st.session_state.conclude_message
            st.session_state.messages.append({"role": "bot", "content": st.session_state.conclude_message})
            st.rerun()
        if("turn" in st.session_state  and (st.session_state.contigous_guardrails_count==MAX_CONTIGUOUS_GUARDRAIL_COUNT or st.session_state.contiguous_unacceptable_answer_count > MAX_CONTIGUOUS_UNACCEPTABLE_ANSWER_COUNT)):
            st.session_state.conclude=True
            st.session_state.conclude_message="It seems there is a lack of clarity. Let us move on to the next question."
            st.session_state.meta_payload.question = st.session_state.conclude_message
            st.session_state.messages.append({"role": "bot", "content": st.session_state.conclude_message})
            st.rerun()
        if("turn" in st.session_state  and (st.session_state.call_for_termination==True)):
            st.session_state.conclude=True
            # st.session_state.conclude_message="It seems there is a lack of clarity. Let us move on to the next question."
            # st.session_state.meta_payload.question = st.session_state.conclude_message
            # st.session_state.messages.append({"role": "bot", "content": st.session_state.conclude_message})
            st.rerun()

        print(f"LATENCY FOR TURN {st.session_state.turn} IS {latency}")
        print(f"CONVERSATION COUNT: {st.session_state.turn}")
        # Display chat messages using a for loop
        topleft.write("**NOHA AI-BOT**")
        placeholder_tl = topleft.empty()
        with placeholder_tl.container(height=240, border=True):
            for msg in st.session_state.messages:
                #print(st.session_state.messages)
                if msg["role"] == "user":
                    placeholder_tl.chat_message("user").markdown(msg["content"])
                    # bottomleft.write(msg['content'])
                    placeholder_bl.markdown(f"<div class='scrollable-container'><b>Candidate:</b> { msg['content']}</div>", unsafe_allow_html=True)
                if msg["role"] == "bot":
                    placeholder_tl.chat_message("assistant").markdown(msg["content"])
                    # bottomleft.write(msg['content'])
                    placeholder_bl.markdown(f"<div class='scrollable-container'><b>Noha-bot:</b> { msg['content']}</div>", unsafe_allow_html=True)
                    # time.sleep(0.5) 
                #else:bottomright.write("Error in message roles from state.session")

    container_tr = topright.container(height=240, border=False)
    container_tr.write("**SCORE TREND**")


    if st.session_state.turn >= 0 and st.session_state.eval_distribution:
        df = pd.DataFrame({'Scores': st.session_state.eval_distribution})
        container_tr.bar_chart(df, use_container_width=False, width=280, height=160)


    ### For the midright cell    
    # Initialize an empty DataFrame in session state if it doesn't exist
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame(columns=["Turn", "Score"])

    placeholder_mr = midright.empty()
    with placeholder_mr.container(height=200, border=False):
        if st.session_state.turn > 0 and st.session_state.eval_distribution:
            # Get current theme
            is_dark_theme = st.get_option("theme.base") == "dark"
            
            # Set colors based on theme
            bg_color = "#1E1E1E" if is_dark_theme else "#f0f0f0" 
            text_color = "#FFFFFF" if is_dark_theme else "#000000"
            
            st.markdown(f"""
                <div style='
                    text-align: center; 
                    margin-bottom: 6px; 
                    background-color: {bg_color}; 
                    padding: 3px; 
                    border-radius: 5px; 
                    width: 250px;
                    color: {text_color};
                    border: 1px solid {'rgba(255,255,255,0.1)' if is_dark_theme else 'rgba(0,0,0,0.1)'};
                '>
                    <h4 style='font-size: 14px; margin: 8px 0;'> SCORE: {st.session_state.final_score}</h4>
                </div>
            """, unsafe_allow_html=True)

        # Create a new DataFrame for the new data point
        new_data = pd.DataFrame({"Turn": [st.session_state.turn], "Score": [st.session_state.final_score]})
            
        # Concatenate the new data point with the existing DataFrame stored in session state
        st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)

        # Update the line chart with the new data points
        st.line_chart(st.session_state.data.set_index("Turn"), width=280, height=160, use_container_width=False)

        st.write("")

    ### For the bottomright cell
    placeholder_br = bottomright.empty()
    with placeholder_br.container(height=420, border=True):
        # Create mapping between score numbers and evaluation criteria
        # evaluation_criteria = {
        #     f"Score {i+1}": criterion for i, criterion in enumerate([
        #         "Are the assumptions clarified?",
        #         "Does the candidate account for corner cases?",
        #         "Does the candidate choose the appropriate data structure for the problem?",
        #         "Does the candidate select a suitable algorithm for the task?",
        #         "Does the solution proposed by the candidate have optimal time complexity?",
        #         "Does the solution proposed by the candidate have optimal space complexity?",
        #         "Does the proposed solution handle generic use cases?"
        #     ])
        # }
        evaluation_criteria = {
        f"Score {i+1}": criterion for i, criterion in enumerate([
            "Generalization ability",
            "Space Complexity",
            "Time Complexity",
            "Algorithm choice",
            "Data structure choice",
            "Corner case clarification",
            "Assumption clarification"
        ])
        }
        if 'stacked_data' not in st.session_state:
            st.session_state.stacked_data = pd.DataFrame(columns=["Turn"] + [f'Score {i+1}' for i in range(7)])

        if st.session_state.turn >= 0 and st.session_state.eval_distribution:
            # Create a new DataFrame for the new data point
            new_data = pd.DataFrame([[st.session_state.turn] + st.session_state.eval_distribution], 
                                columns=st.session_state.stacked_data.columns)
            
            # Concatenate the new data point with the existing DataFrame
            st.session_state.stacked_data = pd.concat([st.session_state.stacked_data, new_data], 
                                                    ignore_index=False)
            
            # Display the stacked bar chart with legend
            if not st.session_state.stacked_data.empty:
                # First melt using the actual column names
                melted_df = st.session_state.stacked_data.melt(
                    id_vars=['Turn'],
                    value_vars=[f'Score {i+1}' for i in range(7)]
                )

                # Then replace the Score labels with full criteria
                melted_df['variable'] = melted_df['variable'].map(evaluation_criteria)

                # Define a color palette
                bar_colors = ['#F06292', '#BA68C8', '#9575CD', '#7986CB', '#64B5F6', '#4FC3F7', '#4DD0E1']
                bar_colors = ['#F08080', '#FA8072', '#E9967A', '#F0E68C', '#BDB76B', '#ADD8E6', '#778899'] #rainbow palette
                bar_colors = ['#2E9CCA', '#D65A31', '#4A4A4A', '#90AFC5', '#336B87', '#763626', '#A3D1FF'] #distinct palette
                bar_colors = ['#2E9CCA', '#D65A31', '#4A4FEA', '#FFDA63', '#336B87', '#90EE90', '#A3D1FF'] #distinct palette

                # Create the stacked bar chart using matplotlib
                fig, ax = plt.subplots(figsize=((32/2.54),(15/2.54)))  # Reduced figsize for better fit
                bottom = np.zeros(len(melted_df['Turn'].unique()), dtype=float) # Initialize the bottom for stacking

                # Get unique evaluation criteria for iterating in plotting
                criteria = melted_df['variable'].unique()

                # Create a dictionary to store the turn values
                turn_values = {turn: i for i, turn in enumerate(melted_df['Turn'].unique())}

                # Iterate through criteria and create the bars
                for i, criterion in enumerate(criteria):
                    criterion_data = melted_df[melted_df['variable'] == criterion]
                    values = criterion_data['value'].values
                    try:
                        values = values.astype(float)  # Convert to float if it's not already
                    except ValueError as e:
                        print(f"Error converting values to float: {e}")
                        print(f"Problematic criterion: {criterion}")
                        print(f"Data type of values: {values.dtype}")
                        # Add more debugging information as needed
                        raise # re-raise the exception
                    turns = criterion_data['Turn'].values
                    turn_indices = [turn_values[turn] for turn in turns]  # Get corresponding index values
                    ax.bar(turn_indices, values, label=criterion, bottom=bottom[turn_indices], width=0.3, color=bar_colors[i % len(bar_colors)]) # plot data with color) # plot data

                    # Update the bottom for the next bar
                    bottom[turn_indices] += values

                # Add labels and title
                ax.set_xlabel('Turn', fontsize=26)
                ax.set_ylabel('Value', fontsize=26)
                ax.set_title('Evaluation Criteria Distribution',fontsize=28)
                ax.set_xticks(list(turn_values.values())) # set only integer values as ticks
                ax.set_xticklabels(list(turn_values.keys()), fontsize=26)  # Label the ticks with Turn values
                ax.tick_params(axis='x', rotation=0) # change the rotation

                # # Add legend, adjust its position
                fig.legend(title='Criteria',loc="outside left center",bbox_to_anchor=(0.05, -0.4, 2, 0.5),title_fontsize=18, fontsize=18, fancybox=True, shadow=True, ncol=2)  # Adjust ncol for spacing
                # # Adjust the layout to make room for the legend and reduce whitespace
                # plt.tight_layout(rect=[0,0,0,0]) # Adjust right parameter to prevent legend overlap
                plt.tight_layout()

                # Show the chart in Streamlit
                st.pyplot(fig)

# with rationale_evaluation_tab:
#     class_label = st.session_state.class_label
#     st.write(f"**CONVERSATION TURN {st.session_state.conversation_turn}**")
#     if class_label:
#         st.write(f" CANDIDATE DIALOGUE : {user_input}")
#         st.write(f" CANDIDATE DIALOGUE CLASS LABEL : {class_label}")
#         if class_label !='technical' and class_label != 'clarification(specific)':
#             st.write(f" BOT DIALOGUE: {bot_dialogue[1]}")
#             st.write(f" DIALOGUE CLASSIFICATION RATIONALE : { bot_dialogue[2]}")
#         else:
#             st.write(f"CANDIDATE ANSWER LABEL : {candidate_answer_label}")
#             st.write(f"RATIONALE CANDIDATE ANSWER: {candidate_answer_classification_rationale}")
#             if candidate_answer_label not in candidate_answer_labels_not_tobe_evaluated:
#                 st.write(f" BOT FOLLOW UP DIALOGUE : {bot_dialogue}")
#                 st.write(f" BOT FOLLOW UP RATIONALE : {bot_dialogue_rationale}")
#                 st.write(f" SUBCRITERION ID : {bot_dialogue_subcriterion_id}")
#                 st.write("**ANSWER EVALUATION**")
#                 st.write(st.session_state.assessment_payload['evaluation_results'])
#             else:    
#                 st.write(f" BOT FOLLOW UP DIALOGUE : {bot_dialogue}")
#                 st.write(f" BOT FOLLOW UP RATIONALE : {bot_dialogue_rationale}")
#                 st.write(f" SUBCRITERION ID : {bot_dialogue_subcriterion_id}")
with rationale_evaluation_tab:
    if "rationale_logs" not in st.session_state:
        st.session_state.rationale_logs = []

    class_label = st.session_state.class_label
    log_entry = f"### CONVERSATION TURN {st.session_state.conversation_turn}\n"

    if class_label:
        log_entry += f"**CANDIDATE DIALOGUE:** {user_input}\n"
        log_entry += f"**CANDIDATE DIALOGUE CLASS LABEL:** {class_label}\n"
        
        if class_label != 'technical' and class_label != 'clarification(specific)':
            log_entry += f"**BOT DIALOGUE:** {bot_dialogue[1]}\n"
            log_entry += f"**DIALOGUE CLASSIFICATION RATIONALE:** {bot_dialogue[2]}\n"
        else:
            log_entry += f"**CANDIDATE ANSWER LABEL:** {candidate_answer_label}\n"
            log_entry += f"**RATIONALE CANDIDATE ANSWER:** {candidate_answer_classification_rationale}\n"

            if candidate_answer_label not in candidate_answer_labels_not_tobe_evaluated:
                log_entry += f"**BOT FOLLOW UP DIALOGUE:** {bot_dialogue}\n"
                log_entry += f"**BOT FOLLOW UP RATIONALE:** {bot_dialogue_rationale}\n"
                log_entry += f"**SUBCRITERION ID:** {bot_dialogue_subcriterion_id}\n"
                log_entry += "**ANSWER EVALUATION**\n"
                for dct in assessment_payload['evaluation_results']:
                # log_entry += f"{st.session_state.assessment_payload['evaluation_results']}\n"
                    log_entry += f"{dct}\n"
            else:    
                log_entry += f"**BOT FOLLOW UP DIALOGUE:** {bot_dialogue}\n"
                log_entry += f"**BOT FOLLOW UP RATIONALE:** {bot_dialogue_rationale}\n"
                log_entry += f"**SUBCRITERION ID:** {bot_dialogue_subcriterion_id}\n"

    # Append log entry
    st.session_state.rationale_logs.append(log_entry)

    # Display logs properly formatted
    for log in st.session_state.rationale_logs:
        st.markdown(log.replace("\n", "  \n"), unsafe_allow_html=True)
