import streamlit as st

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Title of the app
st.title("Interview Conversation Log")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input for Interviewer and Candidate messages
interviewer_input = st.text_input("Interviewer Input", "")
candidate_input = st.text_input("Candidate Input", "")

# Handle Interviewer message submission
if st.button("Send Interviewer Message"):
    if interviewer_input:
        # Display the interviewer message in chat message container
        with st.chat_message("Interviewer"):
            st.markdown(interviewer_input)
        
        # Add interviewer message to chat history
        st.session_state.messages.append({"role": "Interviewer", "content": interviewer_input})
        print()
        # Clear input field
        st.rerun()

# Handle Candidate message submission
if st.button("Send Candidate Message"):
    if candidate_input:
        # Display the candidate message in chat message container
        with st.chat_message("Candidate"):
            st.markdown(candidate_input)
        
        # Add candidate message to chat history
        st.session_state.messages.append({"role": "Candidate", "content": candidate_input})
        
        # Clear input field
        st.rerun()

# Optionally, provide a button to clear the conversation log
if st.button("Clear Conversation Log"):
    st.session_state.messages.clear()
    st.rerun()
