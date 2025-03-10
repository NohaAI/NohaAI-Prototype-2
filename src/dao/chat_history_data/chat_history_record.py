from typing import NamedTuple

class ChatHistoryRecord(NamedTuple):
    interview_id: int
    question_id: int
    bot_dialogue_type: str
    bot_dialogue: str
    candidate_dialogue: str
    distilled_candidate_dialogue: str

    # NOTE:  The filtered_chat_history logic is moved to ChatHistoryDAO (the DAO)
    # as it involves data access and transformation.  Data objects should be
    # simple data containers.