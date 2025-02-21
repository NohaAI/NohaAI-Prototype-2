# Custom Exceptions
import psycopg2
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from src.dao.exceptions import DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError

def execute_query(connection, query, params=None, fetch_one=True, commit=False):
    """
    Execute database queries with enhanced error handling.
    
    Args:
        connection: Database connection
        query (str): SQL query to execute
        params (tuple, optional): Query parameters
        fetch_one (bool): If True, fetch single row
        commit (bool): If True, commit transaction
        
    Returns:
        Query results
        
    Raises:
        DatabaseConnectionError: For connection issues
        DatabaseQueryError: For query execution issues
        DatabaseOperationError: For other database operations issues
    """
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        
        if commit:
            try:
                connection.commit()
            except psycopg2.Error as e:
                connection.rollback()
                logger.error(f"Transaction commit failed: {e}")
                raise DatabaseOperationError(f"Failed to commit transaction: {str(e)}")
        
        result = cursor.fetchone() if fetch_one else cursor.fetchall()
        if result is None and fetch_one:
            return None
        return result

    except psycopg2.OperationalError as e:
        logger.error(f"Database connection error: {e}")
        raise DatabaseConnectionError(f"Database connection failed: {str(e)}")
    
    except psycopg2.DataError as e:
        logger.error(f"Invalid data format: {e}")
        raise DatabaseQueryError(f"Invalid data format: {str(e)}")
    
    except psycopg2.IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
        raise DatabaseOperationError(f"Database constraint violation: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        raise DatabaseOperationError(f"Unexpected error: {str(e)}")
    
    finally:
        if cursor is not None:
            cursor.close()