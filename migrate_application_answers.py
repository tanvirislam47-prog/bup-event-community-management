from database import get_db_connection


def migrate_application_answers():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # =====================================================
        # Check application_id column
        # =====================================================

        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'club_application_answers'
            AND COLUMN_NAME = 'application_id'
            """
        )

        application_id_exists = cursor.fetchone()

        # =====================================================
        # Add application_id if missing
        # =====================================================

        if not application_id_exists:

            cursor.execute(
                """
                ALTER TABLE club_application_answers
                ADD COLUMN application_id INT NULL
                AFTER answer_id
                """
            )

            print("application_id column added.")

        else:

            print("application_id column already exists.")

        # =====================================================
        # Check Foreign Key
        # =====================================================

        cursor.execute(
            """
            SELECT CONSTRAINT_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'club_application_answers'
            AND COLUMN_NAME = 'application_id'
            AND REFERENCED_TABLE_NAME = 'club_applications'
            """
        )

        foreign_key_exists = cursor.fetchone()

        if not foreign_key_exists:

            cursor.execute(
                """
                ALTER TABLE club_application_answers
                ADD CONSTRAINT fk_application_answers_application
                FOREIGN KEY (application_id)
                REFERENCES club_applications(application_id)
                ON DELETE CASCADE
                """
            )

            print("application_id foreign key added.")

        else:

            print("application_id foreign key already exists.")

        # =====================================================
        # Check Unique Index
        # application + question should have one answer only
        # =====================================================

        cursor.execute(
            """
            SELECT INDEX_NAME
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'club_application_answers'
            AND INDEX_NAME = 'uq_application_question'
            """
        )

        unique_index_exists = cursor.fetchone()

        if not unique_index_exists:

            cursor.execute(
                """
                ALTER TABLE club_application_answers
                ADD CONSTRAINT uq_application_question
                UNIQUE (application_id, question_id)
                """
            )

            print("Application-question unique constraint added.")

        else:

            print("Application-question unique constraint already exists.")

        connection.commit()

        print("")
        print("club_application_answers migration completed successfully.")

    except Exception as error:

        if connection:
            connection.rollback()

        print(
            "Migration failed:",
            error
        )

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    migrate_application_answers()