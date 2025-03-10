import json
import logging
from psycopg2.extras import execute_values
from src.dao.utils.db_utils import (
    get_db_connection,
    execute_query,
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseQueryError,
)
from src.schemas.dao import AssessmentRequest, AssessmentResponse
from typing import List, Dict, Optional
from src.dao.assessment_data.assessment_record import AssessmentRecord


# Logger configuration
logger = logging.getLogger(__name__)


class AssessmentDAO:
    """
    DAO for handling database operations related to Assessments.
    """

    @staticmethod
    def get_assessments(interview_id: int) -> List[AssessmentRecord]:
        """
        Retrieves all assessments for a given interview.

        Args:
            interview_id (int): Unique identifier for the interview.

        Returns:
            List[AssessmentRecord]: A list of structured assessment records.

        Raises:
            ValueError: If the interview ID is not found.
            DatabaseQueryError: If a query execution fails.
        """
        try:
            with get_db_connection() as conn:
                # Validate interview existence
                interview_check_query = "SELECT interview_id FROM Interview WHERE interview_id = %s"
                interview_exists = execute_query(conn, interview_check_query, (interview_id,), fetch_one=True)
                if not interview_exists:
                    raise ValueError(f"Interview with ID {interview_id} not found.")

                # Fetch all assessment records
                query = """
                    SELECT interview_id, question_id, primary_question_score, assessment_payload_json
                    FROM assessment
                    WHERE interview_id = %s
                """
                records = execute_query(conn, query, (interview_id,), fetch_one=False)

                assessment_records = []
                for record in records:
                    interview_id, question_id, primary_question_score, assessment_payload_json = record
                    parsed_payload = json.loads(assessment_payload_json)
                    assessment_records.append(AssessmentRecord(interview_id, question_id, primary_question_score, parsed_payload))

                return assessment_records

        except (DatabaseConnectionError, DatabaseQueryError, DatabaseOperationError) as e:
            logger.error(f"Database error in get_assessments: {e}")
            raise

    @staticmethod
    def add_assessment(
        interview_id: int, question_id: int, primary_question_score: float, assessment_payload: str
    ) -> AssessmentRecord:
        """
        Inserts a new assessment record into the database.

        Args:
            interview_id (int): ID of the interview.
            question_id (int): ID of the question.
            primary_question_score (float): Assessment primary_question_score.
            assessment_payload (str): JSON string representing assessment details.

        Returns:
            AssessmentRecord: The inserted record.

        Raises:
            ValueError: If the interview is not found.
            KeyError: If the question is not found.
            DatabaseQueryError: If the insert query fails.
        """
        print(f"primary_question_score {type(primary_question_score)}")
        try:
            with get_db_connection() as conn:
                
                # Validate interview existence
                interview_check_query = "SELECT interview_id FROM Interview WHERE interview_id = %s"
                interview_exists = execute_query(conn, interview_check_query, (interview_id,), fetch_one=True)
                if not interview_exists:
                    raise ValueError(f"Interview with ID {interview_id} not found.")

                # Validate question existence
                question_check_query = "SELECT question_id FROM Question WHERE question_id = %s"
                question_exists = execute_query(conn, question_check_query, (question_id,), fetch_one=True)
                if not question_exists:
                    raise KeyError(f"Question with ID {question_id} not found.")

                # ✅ Convert dict to JSON string
                assessment_payload_json = json.dumps(assessment_payload) 

                # Insert new assessment
                insert_query = """
                    INSERT INTO assessment (interview_id, question_id, primary_question_score, assessment_payload_json)
                VALUES (%s, %s, %s, %s)
                RETURNING interview_id, question_id, primary_question_score, assessment_payload_json
                """
                inserted_record = execute_query(
                    conn, insert_query, (interview_id, question_id, primary_question_score, assessment_payload_json), fetch_one=True, commit=True
                )
                print(f"DEBUG: inserted_record = {inserted_record}")
                return AssessmentRecord(
                    inserted_record[0], inserted_record[1], inserted_record[2], json.loads(inserted_record[3])
                )

        except (DatabaseConnectionError, DatabaseQueryError, DatabaseOperationError) as e:
            logger.error(f"Database error in add_assessment: {e}")
            raise

    @staticmethod
    def batch_insert_assessments(
        assessment_payload_records: List[Dict]
    ) -> str:
        """
        Inserts multiple assessments in a batch operation.

        Args:
            assessment_payload_records (List[Dict]): List of assessment records.

        Returns:
            str: Success message.

        Raises:
            DatabaseQueryError: If the batch insert query fails.
        """
        try:
            with get_db_connection() as conn:
                values = [
                    (
                        record["interview_id"],
                        record["question_id"],
                        record["final_score"],
                        json.dumps(record["assessment_payload"])
                    )
                    for record in assessment_payload_records
                ]

                if not values:
                    return "NO ASSESSMENT PAYLOAD RECORDS TO INSERT"

                query = """
                INSERT INTO assessment
                (interview_id, question_id, primary_question_score, assessment_payload_json) 
                VALUES %s
                """
                
                cursor = conn.cursor()
                execute_values(cursor, query, values)
                conn.commit()

                return "BATCH INSERT SUCCESSFUL"

        except (DatabaseConnectionError, DatabaseQueryError, DatabaseOperationError) as e:
            logger.error(f"Database error in batch_insert_assessments: {e}")
            raise
    
    @staticmethod
    def update_assessment(
        question_evaluation_id: int, primary_question_score: float, assessment_payload: Dict
    ) -> AssessmentRecord:
        """
        Updates an existing assessment record.

        Args:
            question_evaluation_id (int): ID of the assessment to update.
            primary_question_score (float): Updated assessment primary_question_score.
            assessment_payload (Dict): Updated assessment details as a JSON dictionary.

        Returns:
            AssessmentRecord: The updated assessment record.

        Raises:
            KeyError: If the assessment ID is not found.
            DatabaseQueryError: If the update query fails.
        """
        try:
            with get_db_connection() as conn:
                # Check if the assessment exists
                check_query = "SELECT question_evaluation_id FROM assessment WHERE question_evaluation_id = %s"
                existing_record = execute_query(conn, check_query, (question_evaluation_id,), fetch_one=True)

                if not existing_record:
                    raise KeyError(f"Assessment with ID {question_evaluation_id} not found.")

                # Update the assessment
                update_query = """
                    UPDATE assessment
                    SET primary_question_score = %s, assessment_payload_json = %s
                    WHERE question_evaluation_id = %s
                    RETURNING interview_id, question_id, primary_question_score, assessment_payload_json
                """
                updated_record = execute_query(
                    conn,
                    update_query,
                    (primary_question_score, json.dumps(assessment_payload), question_evaluation_id),
                    fetch_one=True,
                    commit=True,
                )

                return AssessmentRecord(
                    updated_record[0], updated_record[1], updated_record[2], json.loads(updated_record[3])
                )

        except (DatabaseConnectionError, DatabaseQueryError, DatabaseOperationError) as e:
            logger.error(f"Database error in update_assessment: {e}")
            raise

    @staticmethod
    def delete_assessment(question_evaluation_id: int) -> Dict[str, str]:
        """
        Deletes an assessment by ID.

        Args:
            question_evaluation_id (int): ID of the assessment.

        Returns:
            dict: Success message.

        Raises:
            KeyError: If the record does not exist.
            DatabaseQueryError: If the delete query fails.
        """
        try:
            with get_db_connection() as conn:
                delete_query = """
                    DELETE FROM assessment 
                    WHERE question_evaluation_id = %s 
                    RETURNING question_evaluation_id
                """
                deleted_record = execute_query(conn, delete_query, (question_evaluation_id,), fetch_one=True, commit=True)

                if not deleted_record:
                    raise KeyError(f"Assessment with ID {question_evaluation_id} not found.")

                return {"message": "Assessment deleted successfully"}

        except (DatabaseConnectionError, DatabaseQueryError, DatabaseOperationError) as e:
            logger.error(f"Database error in delete_assessment: {e}")
            raise
