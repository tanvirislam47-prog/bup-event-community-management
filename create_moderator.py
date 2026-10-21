from werkzeug.security import generate_password_hash

from database import get_db_connection


# =========================================================
# Development Moderator Account
# =========================================================

FULL_NAME = "CPC Moderator Test"
EMAIL = "moderator.cpc@bup.local"
PASSWORD = "Moderator@123"

CLUB_ID = 1


def create_moderator():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        # -----------------------------------------
        # Get CLUB_MODERATOR Role
        # -----------------------------------------

        cursor.execute(
            """
            SELECT role_id
            FROM roles
            WHERE role_name = %s
            """,
            ("CLUB_MODERATOR",)
        )

        role = cursor.fetchone()

        if role is None:
            print("ERROR: CLUB_MODERATOR role not found.")
            return

        moderator_role_id = role[0]

        # -----------------------------------------
        # Check Club
        # -----------------------------------------

        cursor.execute(
            """
            SELECT club_id, name
            FROM clubs
            WHERE club_id = %s
            """,
            (CLUB_ID,)
        )

        club = cursor.fetchone()

        if club is None:
            print("ERROR: Club not found.")
            return

        # -----------------------------------------
        # Check Existing User
        # -----------------------------------------

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE email = %s
            """,
            (EMAIL,)
        )

        existing_user = cursor.fetchone()

        password_hash = generate_password_hash(PASSWORD)

        if existing_user:

            user_id = existing_user[0]

            cursor.execute(
                """
                UPDATE users
                SET
                    role_id = %s,
                    full_name = %s,
                    password_hash = %s,
                    is_active = TRUE
                WHERE user_id = %s
                """,
                (
                    moderator_role_id,
                    FULL_NAME,
                    password_hash,
                    user_id
                )
            )

            print("Existing user updated.")

        else:

            cursor.execute(
                """
                INSERT INTO users
                (
                    role_id,
                    full_name,
                    email,
                    password_hash,
                    is_active
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    TRUE
                )
                """,
                (
                    moderator_role_id,
                    FULL_NAME,
                    EMAIL,
                    password_hash
                )
            )

            user_id = cursor.lastrowid

            print("New moderator user created.")

        # -----------------------------------------
        # Check Existing Club Assignment
        # -----------------------------------------

        cursor.execute(
            """
            SELECT moderator_id
            FROM club_moderators
            WHERE user_id = %s
            """,
            (user_id,)
        )

        existing_assignment = cursor.fetchone()

        if existing_assignment:

            cursor.execute(
                """
                UPDATE club_moderators
                SET
                    club_id = %s,
                    is_active = TRUE
                WHERE user_id = %s
                """,
                (
                    CLUB_ID,
                    user_id
                )
            )

            print("Club assignment updated.")

        else:

            cursor.execute(
                """
                INSERT INTO club_moderators
                (
                    user_id,
                    club_id,
                    is_active
                )
                VALUES
                (
                    %s,
                    %s,
                    TRUE
                )
                """,
                (
                    user_id,
                    CLUB_ID
                )
            )

            print("Club assignment created.")

        connection.commit()

        # -----------------------------------------
        # Success
        # -----------------------------------------

        print()
        print("========================================")
        print("Moderator created successfully")
        print("========================================")
        print("User ID:", user_id)
        print("Name:", FULL_NAME)
        print("Email:", EMAIL)
        print("Club:", club[1])
        print("Club ID:", CLUB_ID)
        print("Status: ACTIVE")
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
    create_moderator()