#EXCEPTIONS DURING INTERVIEW EVALUATION GENERATION

class EmptyChatHistoryException(Exception):
   
    """Raised when the chat history fetched from data is empty for the latest interview taken by the user."""
   
    def __init__(self, message="Chat history can not be empty", chat_history=None):
        self.message = message
        self.chat_history = chat_history
        
        if chat_history:
            self.message += f" (list: {chat_history})"
        
        super().__init__(self.message)

class EmptyAssessmentPayloadException(Exception):
   
    """Raised when the assessment_payload fetched from data is empty for the latest interview taken by the user."""
   
    def __init__(self, message="Assessment payload can not be empty", assessment_payloads=None):
        self.message = message
        self.assessment_payloads = assessment_payloads
        
        if assessment_payloads:
            self.message += f" (list: {assessment_payloads})"
        
        super().__init__(self.message)