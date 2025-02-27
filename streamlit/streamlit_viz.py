import streamlit as st
import numpy as np
import pandas as pd
import requests
import uvicorn
import asyncio
import json
from fastapi import FastAPI
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fastapi.responses import JSONResponse
from src.api import endpoints
from src.schemas.endpoints.schema import GenerateSubCriteriaRequest,EvaluateAnswerRequest, GenerateHintRequest
from src.services.workflows import subcriteria_generator,answer_evaluator
from src.services.workflows.candidate_greeter import generate_greeting
from src.services.workflows import answer_evaluator
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
    return await answer_evaluator.evaluate_answer(evaluation_input)


# Function to run the async function and return results
def run_async(func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(func)


# define layout
row1 = st.columns([0.70, 0.30])
row2 = st.columns([0.70, 0.30])
row3 = st.columns(1)
topleft = row1[0]
topright = row1[1]
midleft = row2[0]
midright = row2[1]
bottom = row3[0]

# simple handles for the cells
topleft.write("**NOHA AI**")
topright.write("**SCORE TREND**")
midleft.write("**CANDIDATE**")
midright.write("---")
bottom.write("**CHAT HISTORY**")

###### Some initial payload and variables for facilitation have been defined; refactor required later possibly; review
# Create an instance of EvaluateAnswerRequest; call it meta_payload for now as it is required throughout

meta_payload = EvaluateAnswerRequest(
    question_id=10, # Question 10 is chosen for now; later it needs to come from some selection criteria
    question="What is your favorite programming language?",
    interview_id=1,
    answer="Python",
    eval_distribution=[0, 0, 0, 0, 0, 0, 0]
)



def get_noha_utterance(turn=0, meta_payload=None):
    if turn == 0:
        meta_payload.question = "Hello 👋 interviewee, how are you doing? All set for the interview ?!"  

    elif turn == 1:
        # noha_utterance = "How to reverse a linked list ?" 
        question_id = meta_payload.question_id # receiving question_id from the initialised meta_payload; for now the question_id is 10 for demo sake
        # Call to interview_metadata helps fetch the question information at turn 1 after the greeting (turn 0)
        initial_question_metadata = run_async(async_get_question_metadata(question_id))
        meta_payload.question = initial_question_metadata['question']
    
    elif turn >=2 and turn < 25:
        meta_payload_from_backend = run_async(async_evaluate_answer(meta_payload))
        meta_payload = meta_payload_from_backend
    
    else:
        meta_payload.answer = "Okay, lets take a break now. Catch you later, bye !"
    
    return meta_payload

# Initialize chat messages and other artefacts if not already done
if "messages" not in st.session_state:
    st.session_state.turn = 0
    st.session_state.eval_distribution = []
    st.session_state.final_score = 0
    chat_history = []
    run_async(async_delete_chat_history(meta_payload.interview_id))
    meta_payload_from_backend = get_noha_utterance(st.session_state.turn, meta_payload)
    greeting = meta_payload_from_backend.question
    st.session_state.messages = [{"role": "bot", "content": greeting}]
    run_async(async_add_chat_history(meta_payload.interview_id, meta_payload.question_id, greeting, meta_payload.answer, 'greeting'))

# Chat input
user_input = midleft.chat_input("Type your message here...")

if user_input:
    # Add the user message to the session state and update_chat_history
    st.session_state.messages.append({"role": "user", "content": user_input})
    run_async(async_add_chat_history(meta_payload.interview_id, meta_payload.question_id, meta_payload.question, user_input, 'reciprocation'))

    # Simulate a bot response (here, echoing the user's message)
    st.session_state.turn += 1
    meta_payload.answer = user_input
    if (st.session_state.turn == 1):
        meta_payload_from_backend = get_noha_utterance(st.session_state.turn, meta_payload)
        initial_question = meta_payload_from_backend.question
        st.session_state.messages.append({"role": "bot", "content": initial_question})
        run_async(async_add_chat_history(meta_payload.interview_id, meta_payload.question_id, initial_question, user_input, 'technical'))
    else:
        meta_payload_from_backend = get_noha_utterance(st.session_state.turn, meta_payload)
        meta_payload.eval_distribution = meta_payload_from_backend['criteria_scores']
        final_score = meta_payload_from_backend['final_score']
        chat_history = async_get_chat_history(meta_payload.interview_id)
        # hint_question = "generated hint question" # this requires chat_history, eval_distribution, hint_count?? or hint_question?? ask Toyesh >@#%!#%
        hint_question = run_async(async_generate_hint(chat_history,meta_payload_from_backend,[0,0,0,0,0]))
        st.session_state.eval_distribution = meta_payload.eval_distribution
        st.session_state.final_score = final_score
        st.session_state.messages.append({"role": "bot", "content": hint_question})
        run_async(async_add_chat_history(meta_payload.interview_id, meta_payload.question_id, hint_question, user_input, 'hint'))

# Display chat messages using a for loop
placeholder_tl = topleft.empty()
with placeholder_tl.container():
    for msg in st.session_state.messages:
        print(st.session_state.messages)
        if msg["role"] == "user":
            placeholder_tl.chat_message("user").markdown(msg["content"])
            # bottom.write(msg['content'])
            bottom.markdown(f"<div class='scrollable-container'><b>Candidate:</b> { msg['content']}</div>", unsafe_allow_html=True)
        elif msg["role"] == "bot":
            placeholder_tl.chat_message("assistant").markdown(msg["content"])
            # bottom.write(msg['content'])
            bottom.markdown(f"<div class='scrollable-container'><b>Noha-bot:</b> { msg['content']}</div>", unsafe_allow_html=True)
            # time.sleep(0.5) 

placeholder_tr = topright.empty()
with placeholder_tr.container(): 
    if st.session_state.turn > 0 and st.session_state.eval_distribution:
        df = pd.DataFrame({'Scores': st.session_state.eval_distribution})
        topright.bar_chart(df)

placeholder_mr = midright.empty()
with placeholder_mr.container():
    if st.session_state.turn > 0 and st.session_state.eval_distribution:
        placeholder_mr.markdown(f"""
    <div style='text-align: center; margin-top: 2px; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>
        <h1 style='font-size: 16px;'> SCORE: {st.session_state.final_score}</h1>
    </div>
    """,
    unsafe_allow_html=True)