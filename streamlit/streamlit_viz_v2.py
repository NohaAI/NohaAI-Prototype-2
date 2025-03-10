import streamlit as st
# import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import requests
import uvicorn
import asyncio
import json
from fastapi import FastAPI
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from src.api import endpoints
from src.schemas.endpoints.schema import GenerateSubCriteriaRequest,EvaluateAnswerRequest, GenerateHintRequest
from src.services.workflows.candidate_greeter import generate_greeting
from src.services.workflows import subcriteria_generator
from src.services.workflows import solution_evaluator
from src.services.workflows.hint_generator import generate_hint
from src.utils.logger import get_logger
from src.utils.response_helper import decorate_response
from src.dao.utils.db_utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool
from src.dao.question import get_question_metadata
from src.dao.exceptions import QuestionNotFoundException,InterviewNotFoundException
from src.dao.chat_history import get_chat_history
from src.dao.interview import get_interview_metadata
from src.dao.chat_history import add_chat_history
from src.dao.question import get_initial_question_metadata
from src.dao.chat_history import delete_chat_history
from src.api.endpoints import greet_candidate
from test.simulate_candidate_response import simulate_candidate_response

# Function to fetch chat history asynchronously
async def async_get_chat_history(interview_id):
    return await get_chat_history(interview_id)

# Function to delete and reset chat history for a specific interview_id asynchronously
async def async_delete_chat_history(interview_id):
    return await delete_chat_history(interview_id)

# Function to add chat history asynchronously
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

# Function that prepares a generate_hint call
async def async_generate_hint(chat_history, meta_payload, hint_list):
    return await generate_hint(chat_history, meta_payload, hint_list)

async def async_evaluate_answer(evaluation_input):
    return await solution_evaluator.evaluate_solution(evaluation_input)


# Function to run the async function and return results
def run_async(func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(func)

# define layout

# Set the page configuration to use wide mode
st.set_page_config(page_title="Your App Title", layout="wide")

row1 = st.columns([0.70, 0.30], gap="large")
row2 = st.columns([0.70, 0.30], gap="large")
row3 = st.columns([0.70, 0.30], gap="large")
topleft = row1[0]
topright = row1[1]
midleft = row2[0]
midright = row2[1]
bottomleft = row3[0]
bottomright = row3[1]
#for dev
# if("turn" in st.session_state and st.session_state.turn > 25):
#     # bottomleft.write(f"**INTERVIEW RESULTS**: {st.session_state.final_score}")
#     st.markdown(f'<p style="font-size: 24px;"><strong>INTERVIEW RESULTS</strong>: {st.session_state.final_score}</p>', unsafe_allow_html=True)
#     st.stop()
#for prod
if("turn" in st.session_state and "final_score" in st.session_state and st.session_state.turn > 12 and st.session_state.final_score > 7.0):
    # bottomleft.write(f"**INTERVIEW RESULTS**: {st.session_state.final_score}")
    st.markdown(f'<p style="font-size: 24px;"><strong>INTERVIEW RESULTS</strong>: {st.session_state.final_score}</p>', unsafe_allow_html=True)
    st.stop() 

###### Some initial payload and variables for facilitation have been defined; refactor required later possibly; review
# Initialize chat messages and other artefacts if not already done
if "messages" not in st.session_state:
    st.session_state.hint_count=[0,0,0,0,0]
    st.session_state.turn = 0
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
    greeting = "Hello 👋 interviewee, how are you doing? All set for the interview ?!"
    st.session_state.meta_payload.question=greeting
    st.session_state.messages = [{"role": "bot", "content": greeting}]

placeholder_bl = bottomleft.container(height=320, border=True)
placeholder_bl.write("**CHAT HISTORY**")

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
container_ml = midleft.container(height=100, border=False)
container_ml.write("**CANDIDATE**")
user_input = container_ml.chat_input("Type your message here...")

if user_input:
    # Add the user message to the session state and update_chat_history
    if st.session_state.turn==0:
        st.session_state.messages.append({"role": "user", "content": user_input})
        run_async(async_add_chat_history(st.session_state.meta_payload.interview_id, st.session_state.meta_payload.question_id, st.session_state.meta_payload.question, user_input, 'greeting'))
        st.session_state.turn += 1
        # Code block to fetch initial question; input args: question_id

        # get question_id from the initialised st.session_state.meta_payload; question_id == 10 for now, to be generalised later
        question_id = st.session_state.meta_payload.question_id 
        initial_question_metadata = run_async(async_get_question_metadata(question_id))
        initial_question = initial_question_metadata['question']
        st.session_state.meta_payload.question = initial_question
        st.session_state.messages.append({"role": "bot", "content": initial_question})
        # run_async(async_add_chat_history(st.session_state.meta_payload.interview_id, st.session_state.meta_payload.question_id, initial_question, user_input, 'technical'))
    elif (st.session_state.turn == 1):
        st.session_state.messages.append({"role": "user", "content": user_input})
        run_async(async_add_chat_history(st.session_state.meta_payload.interview_id, st.session_state.meta_payload.question_id, st.session_state.meta_payload.question, user_input, 'technical'))
        # Code block to prepare input args(evaluation_answer_payload) and call evaluate_answer
        # answer_evaluation_payload={
        #     "question_id":initial_question_metadata['question_id'],
        #     "question":initial_question,
        #     "interview_id":interview_id,
        #     "answer":candidate_response,
        #     "eval_distribution":initial_eval_distribution
        # }
        # IN STREAMLIT st.session_state.meta_payload is the evaluation_answer_payload
        # ALGO: assessment_payload = evaluate_answer(evaluate_answer_payload)
        st.session_state.meta_payload.answer = user_input
        assessment_payload = run_async(async_evaluate_answer(st.session_state.meta_payload))
        st.session_state.meta_payload.eval_distribution = assessment_payload['criteria_scores']
        st.session_state.eval_distribution = assessment_payload['criteria_scores']
        st.session_state.final_score = assessment_payload['final_score']
        st.session_state.turn += 1
        # Code block to fetch hint question for the first time : input args: chat_history, assessment_payload, hint_count
        chat_history = run_async(async_get_chat_history(st.session_state.meta_payload.interview_id))
        hint_question = run_async(async_generate_hint(chat_history, assessment_payload, st.session_state.hint_count))
        st.session_state.meta_payload.question = hint_question
        st.session_state.messages.append({"role": "bot", "content": hint_question})

        # run_async(async_add_chat_history(st.session_state.meta_payload.interview_id, st.session_state.meta_payload.question_id, initial_question, user_input, 'technical'))
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        run_async(async_add_chat_history(st.session_state.meta_payload.interview_id, st.session_state.meta_payload.question_id, st.session_state.meta_payload.question, user_input, 'hint'))
        # ALGO: assessment_payload = evaluate_answer(evaluation_answer_payload)
        st.session_state.meta_payload.answer = user_input
        assessment_payload = run_async(async_evaluate_answer(st.session_state.meta_payload))
        st.session_state.meta_payload.eval_distribution = assessment_payload['criteria_scores']
        st.session_state.eval_distribution = assessment_payload['criteria_scores']
        st.session_state.final_score = assessment_payload['final_score']
        st.session_state.turn += 1
        chat_history = run_async(async_get_chat_history(st.session_state.meta_payload.interview_id))
        hint_question = run_async(async_generate_hint(chat_history,assessment_payload, st.session_state.hint_count))
        st.session_state.meta_payload.question = hint_question
        st.session_state.messages.append({"role": "bot", "content": hint_question})
    print(f"CONVERSATION COUNT: {st.session_state.turn}")

    # Display chat messages using a for loop
    topleft.write("**NOHA AI-BOT**")
    placeholder_tl = topleft.empty()
    with placeholder_tl.container(height=240, border=True):
        for msg in st.session_state.messages:
            print(st.session_state.messages)
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
        st.markdown(f"""
    <div style='text-align: center; margin-bottom: 6px; background-color: #f0f0f0; padding: 3px; border-radius: 5px; width: 250px'>
        <h4 style='font-size: 14px;'> SCORE: {st.session_state.final_score}</h4>
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
with placeholder_br.container(height=240):
    if 'stacked_data' not in st.session_state:
        st.session_state.stacked_data = pd.DataFrame(columns=["Turn"] + [f'Score {i+1}' for i in range(7)])  # Initialize DataFrame for scores

    if st.session_state.turn >= 0 and st.session_state.eval_distribution:
        # Create a new DataFrame for the new data point
        new_data = pd.DataFrame([[st.session_state.turn] + st.session_state.eval_distribution], columns=st.session_state.stacked_data.columns)
        # Concatenate the new data point with the existing DataFrame stored in session state
        st.session_state.stacked_data = pd.concat([st.session_state.stacked_data, new_data], ignore_index=False)
        # Display the stacked bar chart
        if not st.session_state.stacked_data.empty:
            # Create a placeholder for dynamic updates
            placeholder_br.bar_chart(st.session_state.stacked_data.set_index("Turn"), use_container_width=False, width=360, height=300)



