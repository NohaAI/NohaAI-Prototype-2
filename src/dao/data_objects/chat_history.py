class ChatHistoryRecord(list):
    def __init__(self):
        super().__init__()

    def add_record(self, interview_id, question_id, turn_input_type, turn_input, turn_output, distilled_turn_output):
        self.append({
            "interview_id": interview_id,
            "question_id": question_id,
            "turn_input_type": turn_input_type,
            "turn_input": turn_input,
            "turn_output": turn_output,
            "distilled_turn_output": distilled_turn_output
        })

    def filtered_chat_history(self, interview_id, question_id):
        return [
            {"bot_dialogue_type": record["turn_input_type"], "bot_dialogue": record["turn_input"], "candidate_dialogue": record["distilled_turn_output"]}
            for record in self if record["interview_id"] == interview_id and (question_id is None or record["question_id"] == question_id)
        ]