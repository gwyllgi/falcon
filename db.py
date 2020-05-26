import mysql.connector
from datetime import datetime

import settings as discord_settings


def get_db_connection():
    config = {
        'user': discord_settings.DB_USER,
        'password': discord_settings.DB_PASSWORD,
        'host': discord_settings.DB_HOST,
        'database': discord_settings.DB_NAME,
    }

    db_connection = mysql.connector.connect(**config)
    return db_connection


def setup_db_table():
    """
    setup_db_table
        Method to setup search history table if not exists.
    """
    db_connection = get_db_connection()
    cur = db_connection.cursor()
    cur.execute(
        '''
            CREATE TABLE IF NOT EXISTS search_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                created DATETIME,
                search_key VARCHAR(255) NOT NULL UNIQUE
            )
        '''
    )


def create_search_history(search_keyword):
    """
    create_search_history
        method to create search history info in database
    """
    statement = (
        "REPLACE  INTO search_history"
        "(search_key, created)"
        "VALUES (%s, %s)"
    )
    db_connection = get_db_connection()
    data = (search_keyword, datetime.utcnow())
    cur = db_connection.cursor()
    cur.execute(statement, data)
    db_connection.commit()
    cur.close()


def get_search_history(
        search_keyword,
        result_count=discord_settings.MAX_SEARCH_HISTORY_RESULT_COUNT,
):
    """
    get_search_history
        method to get recent search history for a specified search keyword
    :param search_keyword:
    :return:
    """
    db_connection = get_db_connection()
    cur = db_connection.cursor()
    cur.execute(
        '''
        SELECT search_key FROM search_history where search_key LIKE '%{}%' 
        ORDER BY created DESC LIMIT {}
        '''.format(
            search_keyword,
            result_count,
        )
    )
    search_results = []
    for result in cur.fetchall():
        search_results.append(result[0])
    cur.close()
    return search_results
