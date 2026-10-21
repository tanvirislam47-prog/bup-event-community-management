from database import get_db_connection


def setup_application_question_tables():

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # =====================================================
        # Club Application Questions
        # =====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS club_application_questions
            (
                question_id INT AUTO_INCREMENT PRIMARY KEY,

                club_id INT NOT NULL,

                question_text VARCHAR(500) NOT NULL,

                question_type ENUM(
                    'SHORT_TEXT',
                    'LONG_TEXT',
                    'YES_NO',
                    'SINGLE_CHOICE'
                ) NOT NULL DEFAULT 'SHORT_TEXT',

                options_json TEXT NULL,

                is_required BOOLEAN NOT NULL DEFAULT TRUE,

                sort_order INT NOT NULL DEFAULT 1,

                is_active BOOLEAN NOT NULL DEFAULT TRUE,

                created_by INT NULL,
                updated_by INT NULL,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                updated_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,

                CONSTRAINT fk_application_question_club
                    FOREIGN KEY (club_id)
                    REFERENCES clubs(club_id)
                    ON DELETE CASCADE,

                CONSTRAINT fk_application_question_created_by
                    FOREIGN KEY (created_by)
                    REFERENCES users(user_id)
                    ON DELETE SET NULL,

                CONSTRAINT fk_application_question_updated_by
                    FOREIGN KEY (updated_by)
                    REFERENCES users(user_id)
                    ON DELETE SET NULL
            )
            """
        )

        # =====================================================
        # Club Application Answers
        # =====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS club_application_answers
            (
                answer_id INT AUTO_INCREMENT PRIMARY KEY,

                membership_id INT NOT NULL,

                question_id INT NOT NULL,

                answer_text TEXT NULL,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                updated_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,

                CONSTRAINT uq_membership_question
                    UNIQUE (membership_id, question_id),

                CONSTRAINT fk_application_answer_membership
                    FOREIGN KEY (membership_id)
                    REFERENCES club_memberships(membership_id)
                    ON DELETE CASCADE,

                CONSTRAINT fk_application_answer_question
                    FOREIGN KEY (question_id)
                    REFERENCES club_application_questions(question_id)
                    ON DELETE CASCADE
            )
            """
        )

        connection.commit()

        print("========================================")
        print("Application question system ready")
        print("========================================")
        print("Created/verified:")
        print("1. club_application_questions")
        print("2. club_application_answers")
        print("========================================")

    except Exception as error:

        if connection:
            connection.rollback()

        print("ERROR:", error)

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    setup_application_question_tables()