import json
import logging
from psycopg2.extras import execute_values
from src.dao.utils.execute_query import execute_query
from src.dao.utils.connect import get_db_connection
from src.dao.exceptions import DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError
from typing import List, Dict
from src.dao.assessment_data.assessment_record import AssessmentRecord


# Logger configuration
logger = logging.getLogger(__name__)

import json
import psycopg2
from typing import List, Dict, Optional

class AssessmentDAO:
    @staticmethod
    def get_assessments(interview_id: int) -> List[Dict]:
        """Fetch all assessments for a given interview ID."""
        query = """
        SELECT question_id, primary_question_score, assessment_payloads 
        FROM assessment WHERE interview_id = %s
        """
        records = execute_query(get_db_connection(), query, (interview_id,), fetch_one=False)
        
        assessments = []
        for record in records:
            assessments.append({
                "question_id": record[0],
                "primary_question_score": record[1],
                "assessment_payloads": json.loads(record[2]) if record[2] else []  # Ensure JSON parsing
            })
        return assessments

    @staticmethod
    def add_assessment(interview_id: int, question_id: int, primary_question_score: float, assessment_payloads: List[Dict]) -> None:
        """Insert a new assessment record."""
        query = """
        INSERT INTO assessment (interview_id, question_id, primary_question_score, assessment_payloads) 
        VALUES (%s, %s, %s, %s)
        """
        
        assessment_payloads_json = json.dumps(assessment_payloads)  # Convert list of dicts to JSON
        execute_query(get_db_connection(), query, (interview_id, question_id, primary_question_score, assessment_payloads_json))

    @staticmethod
    def update_assessment(interview_id: int, question_id: int, primary_question_score: float, assessment_payloads: List[Dict]) -> None:
        """Update an existing assessment record."""
        query = """
        UPDATE assessment 
        SET primary_question_score = %s, assessment_payloads = %s
        WHERE interview_id = %s AND question_id = %s
        """
        
        assessment_payloads_json = json.dumps(assessment_payloads)
        execute_query(get_db_connection(), query, (primary_question_score, assessment_payloads_json, interview_id, question_id))

    @staticmethod
    def batch_insert_assessments(assessments: List[Dict]) -> None:
        """Batch insert multiple assessment records."""
        query = """
        INSERT INTO assessment (interview_id, question_id, primary_question_score, assessment_payloads) 
        VALUES (%s, %s, %s, %s)
        """
        
        values = [(assess['interview_id'], assess['question_id'], assess['primary_question_score'], json.dumps(assess['assessment_payloads'])) for assess in assessments]
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.executemany(query, values)  # Efficient batch insert
                    conn.commit()
        except psycopg2.DatabaseError as e:
            conn.rollback()
            raise

    @staticmethod
    def delete_assessment(interview_id: int, question_id: int) -> None:
        """Delete an assessment record."""
        query = """
        DELETE FROM assessment WHERE interview_id = %s AND question_id = %s
        """
        execute_query(get_db_connection(), query, (interview_id, question_id))
