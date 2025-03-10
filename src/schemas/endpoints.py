# Schema classes for endpoints
from pydantic import Field,BaseModel
from typing import List


class GenerateSubCriteriaRequest(BaseModel):
    """
    Represents the input request for generating sub-criteria based on a question.

    Attributes:
        question_id (int): The unique identifier for the question.
        question (str): The text of the question for which sub-criteria are to be generated.
        question_type_id (int): The identifier representing the type of question .
    """
    question_id: int
    question: str
    question_type_id: int


class EvaluateAnswerRequest(BaseModel):
    question_id: int
    question: str
    interview_id: int
    answer: str
    eval_distribution: List[float] = Field(default_factory=list) #[0,0,0,0,0,0,0]

class GenerateHintRequest(BaseModel):
    question : str
    chat_history: List[str]
    evaluation_results: List[dict]
