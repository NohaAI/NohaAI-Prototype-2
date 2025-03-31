from src.dao.utils.execute_query import execute_query
from src.dao.utils.connect import get_db_connection
from src.dao.exceptions import DatabaseConnectionError, DatabaseOperationError, DatabaseQueryError, LiveCodeNotFoundException
from datetime import datetime
class LiveCodeDAO:
    @staticmethod
    def check_live_code(live_code: int) -> bool:
        try: 
            with get_db_connection() as conn: 
                """Checks whether live code is present in the datatbase table or not"""
                query = "SELECT EXISTS(SELECT 1 FROM live_code WHERE live_code = %s)"
                check_live_code_tuple = execute_query(conn, query, (live_code,))
                check_live_code = check_live_code_tuple[0]
                if check_live_code:
                    return check_live_code
                else:
                    raise LiveCodeNotFoundException(live_code)
        except DatabaseConnectionError as e:
            raise e
        except DatabaseQueryError as e:
            raise e
        except DatabaseOperationError as e:
            raise e

    @staticmethod
    def add_live_code(live_code: int, status: str, code_generation_time: datetime) ->str:
        """Adds the generated live_code to the database"""
        try:
            with get_db_connection() as conn:
                query = "INSERT INTO live_code(live_code, status, code_generation_time) VALUES(%s, %s, %s) RETURNING live_code_id"
                live_code_id_tuple = execute_query(conn, query, (live_code, status, code_generation_time,), commit = True)
                live_code_id = live_code_id_tuple[0]
            return f"LIVE CODE {live_code} ADDED TO DATABASE WITH PRIMARY KEY{live_code_id}"
        except DatabaseConnectionError as e:
            raise e
        except DatabaseQueryError as e:
            raise e
        except DatabaseOperationError as e:
            raise e
    
    @staticmethod
    def update_status(status: str, live_code: int) -> str:
        """Updates the status of the interview"""
        try:
            with get_db_connection() as conn:
                query = "UPDATE LIVE_CODE SET status = %s WHERE live_code = %s RETURNING live_code_id"
                live_code_id_tuple = execute_query(conn, query, (status, live_code,), commit = True)
                if live_code_id_tuple:
                    return f"STATUS UPDATED  TO {status} FOR LIVE_CODE {live_code}"
                else:
                    raise LiveCodeNotFoundException(live_code)
        except DatabaseConnectionError as e:
            raise e
        except DatabaseQueryError as e:
            raise e
        except DatabaseOperationError as e:
            raise e
    
    @staticmethod
    def delete_live_code(live_code: int) -> str:
        """Updates the status of the interview"""
        try:
            with get_db_connection() as conn:
                query = "DELETE FROM live_code WHERE live_code = %s RETURNING live_code"
                deleted_live_code = execute_query(conn, query, (live_code,), commit = True)
                if deleted_live_code:
                    return f"DELETE ENTRY FROM LIVE CODE TABLE WHERE LIVE CODE: {deleted_live_code}"
                else:
                    raise LiveCodeNotFoundException(live_code)
        except DatabaseConnectionError as e:
            raise e
        except DatabaseQueryError as e:
            raise e
        except DatabaseOperationError as e:
            raise e
