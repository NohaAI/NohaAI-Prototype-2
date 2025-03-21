from typing import NamedTuple, Dict

class AssessmentRecord(NamedTuple):
    interview_id: int
    question_id: int
    primary_question_score: float
    assessment_payloads: list[Dict]
