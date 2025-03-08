from src.utils.helper import get_assessment_payload
class AssessmentPayloadRecord(list):
    def __init__(self):
        super().__init__()

    def add_record(self, interview_id, question_id, final_score, assessment_payload):
        self.append({
            "interview_id": interview_id,
            "question_id": question_id,
            "final_score": final_score, 
            "assessment_payload": assessment_payload
        }
        )
    def return_assessment_payload(self, interview_id, question_id):
        for record in self:
            if record["interview_id"] == interview_id and record["question_id"] == question_id:
                return record["assessment_payload"]
        return None
    def return_final_score(self, interview_id, question_id):
        for record in self:
            if record["interview_id"] == interview_id and record["question_id"] == question_id:
                return record["final_score"]
        return None
    def update_record(self, interview_id, question_id, final_score, assessment_payload):
        for record in self:
            if record["interview_id"] == interview_id and record["question_id"] == question_id:
                record["final_score"], record["assessment_payload"] = final_score, assessment_payload
                return True
        return False

