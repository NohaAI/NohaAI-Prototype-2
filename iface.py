import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt

# Function to simulate question fetching from backend
def get_question():
    questions = [
        "What is your greatest strength?",
        "Describe a challenge you faced and how you overcame it.",
        "Where do you see yourself in five years?",
        "Why should we hire you?"
    ]
    return random.choice(questions)

# Function to evaluate answers and return a score
def evaluate_answer(answer):
    # Simulate scoring logic (for demonstration purposes)
    return random.randint(1, 10)  # Random score between 1 and 10

# Initialize session state for messages and scores
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.scores = []
    st.session_state.current_question = get_question()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Display current question
if st.session_state.current_question:
    st.markdown(f"**Bot:** {st.session_state.current_question}")

# Accept user input for candidate's answer
candidate_input = st.text_input("Your Answer:", "")

if st.button("Submit Answer"):
    if candidate_input:
        # Store candidate's answer in chat history
        st.session_state.messages.append({"role": "Candidate", "content": candidate_input})

        # Evaluate the answer and store the score
        score = evaluate_answer(candidate_input)
        st.session_state.scores.append(score)

        # Store bot's response (for demonstration)
        bot_response = f"Evaluated Score: {score}"
        st.session_state.messages.append({"role": "Bot", "content": bot_response})

        # Get next question
        st.session_state.current_question = get_question()

        # Clear input field after submission
        candidate_input = ""

# Display scores graphically
if st.session_state.scores:
    plt.figure(figsize=(10, 5))
    plt.plot(st.session_state.scores, marker='o')
    plt.title("Candidate's Score Over Time")
    plt.xlabel("Turn")
    plt.ylabel("Score")
    plt.xticks(range(len(st.session_state.scores)))
    plt.grid()
    
    # Show plot in Streamlit
    st.pyplot(plt)

# Display conversation history as a list
st.subheader("Conversation History:")
for message in st.session_state.messages:
    st.write(f"{message['role']}: {message['content']}")

