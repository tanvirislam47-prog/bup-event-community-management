from database import get_db_connection


def setup_club_applications():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS club_applications (

                application_id INT AUTO_INCREMENT PRIMARY KEY,

                club_id INT NOT NULL,

                student_user_id INT NOT NULL,

                status ENUM(
                    'DRAFT',
                    'PENDING',
                    'APPROVED',
                    'REJECTED',
                    'WITHDRAWN'
                ) NOT NULL DEFAULT 'DRAFT',

                submitted_at TIMESTAMP NULL,

                withdrawn_at TIMESTAMP NULL,

                reviewed_by INT NULL,

                reviewed_at TIMESTAMP NULL,

                rejection_reason TEXT NULL,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                updated_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,

                CONSTRAINT fk_club_applications_club
                    FOREIGN KEY (club_id)
                    REFERENCES clubs(club_id)
                    ON DELETE CASCADE,

                CONSTRAINT fk_club_applications_student
                    FOREIGN KEY (student_user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,

                CONSTRAINT fk_club_applications_reviewer
                    FOREIGN KEY (reviewed_by)
                    REFERENCES users(user_id)
                    ON DELETE SET NULL
            )
            """
        )

        connection.commit()

        print("club_applications table created successfully.")

    except Exception as error:

        if connection:
            connection.rollback()

        print(
            "Failed to create club_applications table:",
            error
        )

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    setup_club_applications()