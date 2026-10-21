from database import get_db_connection


def cleanup_old_pending_application():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        # Remove old test application records
        # that were created by the previous direct-apply flow.

        cursor.execute(
            """
            DELETE FROM club_memberships
            WHERE club_id = 1
            AND status = 'PENDING'
            """
        )

        connection.commit()

        print(
            f"{cursor.rowcount} old pending application(s) removed."
        )

    except Exception as error:

        if connection:
            connection.rollback()

        print(
            "Cleanup failed:",
            error
        )

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    cleanup_old_pending_application()