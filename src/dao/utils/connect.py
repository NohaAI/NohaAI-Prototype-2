import psycopg2
from psycopg2.pool import SimpleConnectionPool
import os
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
from src.dao.utils.config import load_simple_connection_config
from src.dao.exceptions import DatabaseConnectionError
# Create connection pool
simple_connection_config=load_simple_connection_config()
connection_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    **simple_connection_config
)
@contextmanager
def get_db_connection():
    """
    Database connection management with error handling.
    
    Yields:
        connection: Database connection from the connection pool
        
    Raises:
        DatabaseConnectionError: If connection cannot be established
    """
    connection = None
    try:
        connection = connection_pool.getconn()
        yield connection
    except psycopg2.OperationalError as e:
        logger.error(f"Failed to get database connection: {e}")
        raise DatabaseConnectionError(f"Cannot establish database connection: {str(e)}")
    finally:
        if connection is not None:
            try:
                connection_pool.putconn(connection)
            except Exception as e:
                logger.error(f"Failed to return connection to pool: {e}")

