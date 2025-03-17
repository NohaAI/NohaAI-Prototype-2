from src.dao.utils.execute_query import execute_query
from src.dao.utils.connect import get_db_connection
from src.dao.exceptions import DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError
from src.dao.exceptions import ChatHistoryNotFoundException, InterviewNotFoundException, QuestionNotFoundException
from psycopg2.extras import execute_values
from src.dao.chat_history_data.chat_history_record import ChatHistoryRecord  # Import the data object
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)

class ChatHistoryDAO:
    def get_chat_history(self, interview_id: int) -> List[ChatHistoryRecord]:
        """
        Retrieves all chat history records for a given interview ID.
        """

        try:
            with get_db_connection() as conn:
                query = """
                    SELECT interview_id, question_id, bot_dialogue_type, bot_dialogue, candidate_dialogue, distilled_candidate_dialogue
                    FROM chat_history
                    WHERE interview_id = %s
                """
                records = execute_query(conn, query, (interview_id,), fetch_one=False)
                if not records:
                    logger.info(f"No chat history found for interview ID {interview_id}")
                    return []  # Return an empty list or raise a custom exception
            
                # Map to data objects
                chat_history_records = [ChatHistoryRecord(*record) for record in records]

                return chat_history_records
        except DatabaseConnectionError as e:
            logger.exception("Database connection error")
            raise e
        except DatabaseQueryError as e:
            logger.exception("Database query error")
            raise e
        except DatabaseOperationError as e:
            logger.exception("Database operation error")
            raise e

    def get_filtered_chat_history(self, interview_id: int, question_id: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Retrieves and filters chat history records, returning a list of dictionaries.

        Args:
            interview_id: Filter by interview ID.
            question_id: (Optional) Filter by question ID.

        Returns:
            A list of dictionaries, where each dictionary contains:
            - bot_dialogue_type: The type of bot dialogue (bot_dialogue_type).
            - bot_dialogue: The bot's dialogue (bot_dialogue).  (Note:  This should probably be 'user_dialogue').
            - candidate_dialogue: The candidate's dialogue (distilled_candidate_dialogue).
        """
        try:
            with get_db_connection() as conn:
                query = """
                    SELECT interview_id, question_id, bot_dialogue_type, bot_dialogue, candidate_dialogue, distilled_candidate_dialogue
                    FROM chat_history
                    WHERE interview_id = %s
                """
                params = [interview_id]

                if question_id is not None:
                    query += " AND question_id = %s"
                    params.append(question_id)

                records = execute_query(conn, query, tuple(params), fetch_one=False)

                filtered_history = []
                for record in records:
                    filtered_history.append({
                        "bot_dialogue_type": record[2],  # bot_dialogue_type
                        "bot_dialogue": record[3],  # bot_dialogue  (Consider renaming key to user_dialogue)
                        "candidate_dialogue": record[5]   # distilled_candidate_dialogue
                    })
                return filtered_history
        except DatabaseConnectionError as e:
            logger.exception("Database connection error")
            raise e
        except DatabaseQueryError as e:
            logger.exception("Database query error")
            raise e
        except DatabaseOperationError as e:
            logger.exception("Database operation error")
            raise e

    def update_chat_history(self, chat_history_turn_id: int, bot_dialogue: str = None, candidate_dialogue: str = None, bot_dialogue_type: str = None) -> Dict:
        """Updates a chat history entry."""
        try:
            with get_db_connection() as conn:
                # Check existence
                check_query = "SELECT chat_history_turn_id FROM chat_history WHERE chat_history_turn_id = %s"
                exists = execute_query(conn, check_query, (chat_history_turn_id,), fetch_one=True)
                if not exists:
                    raise ChatHistoryNotFoundException(chat_history_turn_id)

                # Build dynamic update
                update_fields = []
                update_params = []
                if bot_dialogue is not None:
                    update_fields.append("bot_dialogue = %s")
                    update_params.append(bot_dialogue)
                if candidate_dialogue is not None:
                    update_fields.append("candidate_dialogue = %s")
                    update_params.append(candidate_dialogue)
                if bot_dialogue_type is not None:
                    update_fields.append("bot_dialogue_type = %s")
                    update_params.append(bot_dialogue_type)

                if not update_fields:
                    raise Exception("No updated fields provided")

                update_params.append(chat_history_turn_id)

                update_query = f"""
                    UPDATE chat_history
                    SET {', '.join(update_fields)}
                    WHERE chat_history_turn_id = %s
                    RETURNING chat_history_turn_id, question_id, interview_id, bot_dialogue, candidate_dialogue, bot_dialogue_type
                """
                updated_record = execute_query(
                    conn,
                    update_query,
                    update_params,
                    fetch_one=True,
                    commit=True
                )

                return {
                    "chat_history_turn_id": updated_record[0],
                    "question_id": updated_record[1],
                    "interview_id": updated_record[2],
                    "bot_dialogue": updated_record[3],
                    "candidate_dialogue": updated_record[4],
                    "bot_dialogue_type": updated_record[5],
                }
        except DatabaseConnectionError as e:
            logger.exception("Database connection error")
            raise e
        except DatabaseQueryError as e:
            logger.exception("Database query error")
            raise e
        except DatabaseOperationError as e:
            logger.exception("Database operation error")
            raise e

    def add_chat_history(self, interview_id: int, question_id: int, bot_dialogue: str, candidate_dialogue: str, distilled_candidate_dialogue: str,
                         bot_dialogue_type: str) -> Dict:
        """Adds a new chat history entry."""
        try:
            with get_db_connection() as conn:
                interview_check_query = "SELECT interview_id FROM interview WHERE interview_id = %s"
                interview = execute_query(conn, interview_check_query, (interview_id,), fetch_one=True)
                if not interview:
                    raise InterviewNotFoundException

                question_check_query = "SELECT question FROM question WHERE question_id = %s"
                question = execute_query(conn, question_check_query, (question_id,), fetch_one=True)
                if not question:
                    raise QuestionNotFoundException

                insert_query = """
                    INSERT INTO chat_history (interview_id, question_id, bot_dialogue, candidate_dialogue, distilled_candidate_dialogue, bot_dialogue_type)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING chat_history_turn_id, interview_id, question_id, bot_dialogue, candidate_dialogue, distilled_candidate_dialogue, bot_dialogue_type
                """
                result = execute_query(
                    conn,
                    insert_query,
                    (interview_id, question_id, bot_dialogue, candidate_dialogue, distilled_candidate_dialogue, bot_dialogue_type),
                    fetch_one=True,
                    commit=True
                )

                return {
                    "chat_history_turn_id": result[0],
                    "interview_id": result[1],
                    "question_id": result[2],
                    "bot_dialogue": result[3],
                    "candidate_dialogue": result[4],
                    "distilled_candidate_dialogue": result[5],
                    "bot_dialogue_type": result[6]
                }
        except DatabaseConnectionError as e:
            logger.exception("Database connection error")
            raise e
        except DatabaseQueryError as e:
            logger.exception("Database query error")
            raise e
        except DatabaseOperationError as e:
            logger.exception("Database operation error")
            raise e

    def batch_insert_chat_history(self, chat_history_records: List[Dict]) -> List[Dict]:
        """
        Inserts multiple chat history entries in a batch operation.

        Args:
            chat_history_records (List[Dict]): List of chat history records.
                Each record should contain:
                - interview_id
                - question_id
                - bot_dialogue
                - candidate_dialogue
                - distilled_candidate_dialogue
                - bot_dialogue_type

        Returns:
            List[Dict]: List of inserted chat history records with their IDs.

        Raises:
            DatabaseQueryError: If the batch insert query fails.
        """
        try:
            with get_db_connection() as conn:
                # Validate input records
                required_fields = [
                    "interview_id",
                    "question_id",
                    "bot_dialogue",
                    "candidate_dialogue",
                    "distilled_candidate_dialogue",
                    "bot_dialogue_type"
                ]
                for record in chat_history_records:
                    for field in required_fields:
                        if field not in record:
                            raise ValueError(f"Missing '{field}' in chat history record")

                # Prepare values for batch insert
                values = [
                    (
                        record["interview_id"],
                        record["question_id"],
                        record["bot_dialogue"],
                        record["candidate_dialogue"],
                        record["distilled_candidate_dialogue"],
                        record["bot_dialogue_type"]
                    )
                    for record in chat_history_records
                ]
                logger.info(f"Values: {values}")
                if not values:
                    return []  # No records to insert

                # # Check if interviews and questions exist
                # interview_ids = [record["interview_id"] for record in chat_history_records]
                # question_ids = [record["question_id"] for record in chat_history_records]

                # interview_check_query = "SELECT interview_id FROM interview WHERE interview_id IN %s"
                # existing_interviews = execute_query(conn, interview_check_query, (tuple(interview_ids),))
                # existing_interview_ids = [row[0] for row in existing_interviews]
                # missing_interview_ids = set(interview_ids) - set(existing_interview_ids)
                # if missing_interview_ids:
                #     raise InterviewNotFoundException(f"Interviews with IDs {missing_interview_ids} do not exist")

                # question_check_query = "SELECT question_id FROM question WHERE question_id IN %s"
                # existing_questions = execute_query(conn, question_check_query, (tuple(question_ids),))
                # existing_question_ids = [row[0] for row in existing_questions]
                # missing_question_ids = set(question_ids) - set(existing_question_ids)
                # if missing_question_ids:
                #     raise QuestionNotFoundException(f"Questions with IDs {missing_question_ids} do not exist")

                # Batch insert query
                insert_query = """
                    INSERT INTO chat_history (interview_id, question_id, bot_dialogue, candidate_dialogue, distilled_candidate_dialogue, bot_dialogue_type)
                    VALUES %s
                    RETURNING chat_history_turn_id, interview_id, question_id, bot_dialogue, candidate_dialogue, distilled_candidate_dialogue, bot_dialogue_type
                """
                logger.info(f"Insert query: {insert_query}")
                cursor = conn.cursor()
                results = execute_values(cursor, insert_query, values, fetch=True)
                conn.commit()

                logger.info(f"Results: {results}")

                # Convert results to dictionaries
                inserted_records = [
                    {
                        "chat_history_turn_id": result[0],
                        "interview_id": result[1],
                        "question_id": result[2],
                        "bot_dialogue": result[3],
                        "candidate_dialogue": result[4],
                        "distilled_candidate_dialogue": result[5],
                        "bot_dialogue_type": result[6]
                    }
                    for result in results
                ]

            return inserted_records

        except DatabaseConnectionError as e:
            logger.exception("Database connection error")
            raise e
        except DatabaseQueryError as e:
            logger.exception("Database query error")
            raise e
        except DatabaseOperationError as e:
            logger.exception("Database operation error")
            raise e
            


    def delete_chat_history(self, interview_id: int) -> Dict:
        """Deletes chat history for a given interview ID."""
        try:
            with get_db_connection() as conn:
                try:
                    delete_query = """
                        DELETE FROM chat_history
                        WHERE interview_id = %s
                        RETURNING interview_id
                    """
                    deleted_feedback = execute_query(
                        conn,
                        delete_query,
                        (interview_id,),
                        fetch_one=True,
                        commit=True
                    )

                    if not deleted_feedback:
                        raise InterviewNotFoundException(interview_id)

                    return {"message": "chat history deleted successfully"}
                except Exception as e:
                    logger.error(f"Error deleting chat history : {e}")
                    raise
        except DatabaseConnectionError as e:
            logger.exception("Database connection error")
            raise e
        except DatabaseQueryError as e:
            logger.exception("Database query error")
            raise e
        except DatabaseOperationError as e:
            logger.exception("Database operation error")
            raise e
