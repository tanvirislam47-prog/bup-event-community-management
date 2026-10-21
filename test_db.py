from database import get_db_connection

try:
    connection = get_db_connection()

    if connection.is_connected():
        print("MySQL connection successful!")

        cursor = connection.cursor()

        cursor.execute("SELECT DATABASE();")
        database_name = cursor.fetchone()[0]
        print("Connected database:", database_name)

        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'university_event_management'
        """)
        table_count = cursor.fetchone()[0]
        print("Total tables:", table_count)

        cursor.close()
        connection.close()

except Exception as error:
    print("Database connection failed!")
    print(error)