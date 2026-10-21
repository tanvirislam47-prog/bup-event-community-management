import os
import json


from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for
)

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import get_db_connection
from uuid import uuid4


# =========================================================
# Environment Setup
# =========================================================

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
# =========================================================
# Event Gallery Upload Configuration
# =========================================================

EVENT_GALLERY_UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads",
    "event_gallery"
)

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

app.config["EVENT_GALLERY_UPLOAD_FOLDER"] = EVENT_GALLERY_UPLOAD_FOLDER

# Maximum upload request size: 20 MB
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

os.makedirs(
    EVENT_GALLERY_UPLOAD_FOLDER,
    exist_ok=True
)
def allowed_image_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )
# =========================================================
# Student Profile Upload Configuration
# =========================================================

PROFILE_PHOTO_UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads",
    "profile_photos"
)

STUDENT_CV_UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads",
    "student_cvs"
)


ALLOWED_PROFILE_PHOTO_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


ALLOWED_CV_EXTENSIONS = {
    "pdf",
    "doc",
    "docx"
}


app.config["PROFILE_PHOTO_UPLOAD_FOLDER"] = (
    PROFILE_PHOTO_UPLOAD_FOLDER
)

app.config["STUDENT_CV_UPLOAD_FOLDER"] = (
    STUDENT_CV_UPLOAD_FOLDER
)


os.makedirs(
    PROFILE_PHOTO_UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    STUDENT_CV_UPLOAD_FOLDER,
    exist_ok=True
)


def allowed_profile_photo(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_PROFILE_PHOTO_EXTENSIONS
    )


def allowed_cv_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_CV_EXTENSIONS
    )
# =========================================================
# Home
# =========================================================

@app.route("/")
def home():
    return "University Event Management System is running!"


# =========================================================
# Database Test
# =========================================================

@app.route("/db-test")
def db_test():

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        return f"Database connected! Total users: {total_users}"

    except Exception as error:
        return f"Database error: {error}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

# =========================================================
# Student Club Application Form
# =========================================================

@app.route(
    "/clubs/<int:club_id>/apply",
    methods=["GET", "POST"]
)
def club_application_form(club_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "STUDENT":
        return "Access denied!", 403
    

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # =====================================================
        # LOAD ACTIVE CLUB
        # =====================================================

        cursor.execute(
            """
            SELECT
                club_id,
                name,
                category,
                description,
                status
            FROM clubs
            WHERE club_id = %s
            AND status = 'ACTIVE'
            LIMIT 1
            """,
            (club_id,)
        )

        club = cursor.fetchone()

        if club is None:
            return "Club not found!", 404


        # =====================================================
        # CHECK APPROVED MEMBERSHIP
        # =====================================================

        cursor.execute(
            """
            SELECT
                membership_id,
                status
            FROM club_memberships
            WHERE club_id = %s
            AND student_id = %s
            AND status = 'APPROVED'
            LIMIT 1
            """,
            (
                club_id,
                session["user_id"]
            )
        )

        approved_membership = cursor.fetchone()

        if approved_membership:

            return redirect(
                url_for(
                    "club_details",
                    club_id=club_id
                )
            )


        # =====================================================
        # CHECK EXISTING PENDING APPLICATION
        # =====================================================

        cursor.execute(
            """
            SELECT
                application_id,
                status
            FROM club_applications
            WHERE club_id = %s
            AND student_user_id = %s
            AND status = 'PENDING'
            ORDER BY application_id DESC
            LIMIT 1
            """,
            (
                club_id,
                session["user_id"]
            )
        )

        pending_application = cursor.fetchone()

        if pending_application:

            return redirect(
                url_for("student_dashboard")
            )


        # =====================================================
        # LOAD APPLICATION QUESTIONS
        # =====================================================

        cursor.execute(
            """
            SELECT
                question_id,
                question_text,
                question_type,
                options_json,
                is_required,
                sort_order
            FROM club_application_questions
            WHERE club_id = %s
            AND is_active = TRUE
            ORDER BY
                sort_order ASC,
                question_id ASC
            """,
            (club_id,)
        )

        questions = cursor.fetchall()


        # =====================================================
        # POST - SUBMIT APPLICATION
        # =====================================================

        if request.method == "POST":
            print("FORM DATA:", request.form)
            print("FILES DATA:", request.files)
            print("PHOTO FILE:", request.files.get("profile_photo_file"))

            answers = []


            # -------------------------------------------------
            # Validate Answers
            # -------------------------------------------------

            for question in questions:

                field_name = (
                    f"question_{question['question_id']}"
                )

                answer = request.form.get(
                    field_name,
                    ""
                ).strip()


                # Required Question Validation

                if (
                    question["is_required"]
                    and not answer
                ):

                    return (
                        f"Please answer the required question: "
                        f"{question['question_text']}",
                        400
                    )


                # YES / NO Validation

                if (
                    question["question_type"] == "YES_NO"
                    and answer
                    and answer not in ("Yes", "No")
                ):

                    return (
                        "Invalid answer submitted.",
                        400
                    )


                answers.append(
                    {
                        "question_id":
                            question["question_id"],

                        "answer_text":
                            answer
                    }
                )


            # -------------------------------------------------
            # Create Application
            # -------------------------------------------------

            cursor.execute(
                """
                INSERT INTO club_applications
                (
                    club_id,
                    student_user_id,
                    status,
                    submitted_at
                )
                VALUES
                (
                    %s,
                    %s,
                    'PENDING',
                    CURRENT_TIMESTAMP
                )
                """,
                (
                    club_id,
                    session["user_id"]
                )
            )

            application_id = cursor.lastrowid


            # -------------------------------------------------
            # Save Answers
            # -------------------------------------------------

            for answer in answers:

                cursor.execute(
                    """
                    INSERT INTO club_application_answers
                    (
                        application_id,
                        membership_id,
                        question_id,
                        answer_text
                    )
                    VALUES
                    (
                        %s,
                        NULL,
                        %s,
                        %s
                    )
                    """,
                    (
                        application_id,
                        answer["question_id"],
                        answer["answer_text"]
                    )
                )


            # -------------------------------------------------
            # Commit Everything
            # -------------------------------------------------

            connection.commit()


            # -------------------------------------------------
            # Redirect Student Dashboard
            # -------------------------------------------------

            return redirect(
                url_for("student_dashboard")
            )


        # =====================================================
        # GET - LOAD STUDENT PROFILE
        # =====================================================

        cursor.execute(
            """
            SELECT
                u.full_name,
                u.email,
                u.phone,
                sp.student_id,
                sp.department,
                sp.batch
            FROM users u

            JOIN student_profiles sp
                ON sp.user_id = u.user_id

            WHERE u.user_id = %s
            LIMIT 1
            """,
            (session["user_id"],)
        )

        student = cursor.fetchone()

        if student is None:
            return "Student profile not found!", 404


        # =====================================================
        # RENDER APPLICATION FORM
        # =====================================================

        return render_template(
            "club_application_form.html",
            club=club,
            questions=questions,
            student=student
        )


    except Exception as error:

        if connection:
            connection.rollback()

        return (
            f"Application submission failed: {error}",
            500
        )


    finally:

        if cursor:
            cursor.close()

        if (
            connection
            and connection.is_connected()
        ):
            connection.close()
# =========================================================
# Student Registration
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        student_id = request.form.get("student_id", "").strip()
        department = request.form.get("department", "").strip()
        batch = request.form.get("batch", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # -----------------------------------------
        # Validation
        # -----------------------------------------

        if not full_name:
            return "Full name is required!"

        if not email:
            return "Email is required!"

        if not student_id:
            return "Student ID is required!"

        if not department:
            return "Department is required!"

        if not batch:
            return "Batch is required!"

        if not password:
            return "Password is required!"

        if password != confirm_password:
            return "Passwords do not match!"

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # -----------------------------------------
            # Get STUDENT Role
            # -----------------------------------------

            cursor.execute(
                """
                SELECT role_id
                FROM roles
                WHERE role_name = %s
                """,
                ("STUDENT",)
            )

            role = cursor.fetchone()

            if role is None:
                return "STUDENT role not found!"

            student_role_id = role[0]

            # -----------------------------------------
            # Duplicate Email Check
            # -----------------------------------------

            cursor.execute(
                """
                SELECT user_id
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            if cursor.fetchone():
                return "This email is already registered!"

            # -----------------------------------------
            # Duplicate Student ID Check
            # -----------------------------------------

            cursor.execute(
                """
                SELECT user_id
                FROM student_profiles
                WHERE student_id = %s
                """,
                (student_id,)
            )

            if cursor.fetchone():
                return "This Student ID is already registered!"

            # -----------------------------------------
            # Hash Password
            # -----------------------------------------

            password_hash = generate_password_hash(password)

            # -----------------------------------------
            # Insert User
            # -----------------------------------------

            cursor.execute(
                """
                INSERT INTO users
                (
                    role_id,
                    full_name,
                    email,
                    password_hash,
                    phone
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    student_role_id,
                    full_name,
                    email,
                    password_hash,
                    phone
                )
            )

            new_user_id = cursor.lastrowid

            # -----------------------------------------
            # Insert Student Profile
            # -----------------------------------------

            cursor.execute(
                """
                INSERT INTO student_profiles
                (
                    user_id,
                    student_id,
                    department,
                    batch
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    new_user_id,
                    student_id,
                    department,
                    batch
                )
            )

            connection.commit()

            return redirect(url_for("login"))

        except Exception as error:

            if connection:
                connection.rollback()

            return f"Registration failed: {error}"

        finally:

            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    return render_template("register.html")


# =========================================================
# Login
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    # -----------------------------------------
    # Already Logged In
    # -----------------------------------------

    if request.method == "GET":

        if session.get("role") == "STUDENT":
            return redirect(
                url_for("student_dashboard")
            )

        if session.get("role") == "CLUB_MODERATOR":
            return redirect(
                url_for("moderator_dashboard")
            )

    # -----------------------------------------
    # Login Submission
    # -----------------------------------------

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        selected_login_role = request.form.get(
            "login_role",
            ""
        ).strip().upper()

        # -----------------------------------------
        # Basic Validation
        # -----------------------------------------

        if not email or not password:
            return (
                "Email and password are required!",
                400
            )

        allowed_login_types = {
            "STUDENT",
            "CLUB_MODERATOR",
            "AUTHORIZED_STAFF"
        }

        if selected_login_role not in allowed_login_types:
            return (
                "Please select an account type before signing in.",
                400
            )

        connection = None
        cursor = None

        try:

            connection = get_db_connection()
            cursor = connection.cursor()

            # -----------------------------------------
            # Find User
            # -----------------------------------------

            cursor.execute(
                """
                SELECT
                    users.user_id,
                    users.full_name,
                    users.password_hash,
                    users.is_active,
                    roles.role_name

                FROM users

                JOIN roles
                    ON users.role_id = roles.role_id

                WHERE users.email = %s

                LIMIT 1
                """,
                (email,)
            )

            user = cursor.fetchone()

            if user is None:
                return (
                    "Invalid email or password!",
                    401
                )

            user_id = user[0]
            full_name = user[1]
            password_hash = user[2]
            is_active = user[3]
            role_name = user[4]

            # -----------------------------------------
            # Account Status
            # -----------------------------------------

            if not is_active:
                return (
                    "Your account is inactive!",
                    403
                )

            # -----------------------------------------
            # Password Check
            # -----------------------------------------

            if not check_password_hash(
                password_hash,
                password
            ):

                return (
                    "Invalid email or password!",
                    401
                )

            # -----------------------------------------
            # Convert DB Role To Login Type
            # -----------------------------------------

            if role_name == "STUDENT":

                actual_login_type = "STUDENT"

            elif role_name == "CLUB_MODERATOR":

                actual_login_type = "CLUB_MODERATOR"

            elif role_name in (
                "AUTHORITY",
                "REPORTER",
                "ADMIN"
            ):

                actual_login_type = "AUTHORIZED_STAFF"

            else:

                return (
                    "This account role is not supported!",
                    403
                )

            # -----------------------------------------
            # Check Selected Role
            # -----------------------------------------

            if selected_login_role != actual_login_type:

                login_type_labels = {
                    "STUDENT":
                        "Student",

                    "CLUB_MODERATOR":
                        "Club Moderator",

                    "AUTHORIZED_STAFF":
                        "Authorized Staff"
                }

                correct_label = (
                    login_type_labels.get(
                        actual_login_type,
                        "correct account type"
                    )
                )

                return (
                    f"This account belongs to {correct_label}. "
                    f"Please select {correct_label} and try again.",
                    403
                )

            # -----------------------------------------
            # Create Fresh Session
            # -----------------------------------------

            session.clear()

            session["user_id"] = user_id
            session["full_name"] = full_name
            session["role"] = role_name

            # -----------------------------------------
            # Role Based Redirect
            # -----------------------------------------

            if role_name == "STUDENT":

                return redirect(
                    url_for("student_dashboard")
                )

            elif role_name == "CLUB_MODERATOR":

                return redirect(
                    url_for("moderator_dashboard")
                )

            # Authority / Reporter / Admin
            # dashboard later
            return (
                f"Login successful as {role_name}. "
                "Dashboard for this role is not available yet."
            )

        except Exception as error:

            return (
                f"Login failed: {error}",
                500
            )

        finally:

            if cursor:
                cursor.close()

            if (
                connection
                and connection.is_connected()
            ):
                connection.close()

    return render_template(
        "login.html"
    )
# =========================================================
# Student Dashboard
# =========================================================

@app.route("/student-dashboard")
def student_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "STUDENT":
        return "Access denied!", 403

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        user_id = session["user_id"]

        # =====================================================
        # STUDENT PROFILE
        # =====================================================

        cursor.execute(
            """
            SELECT
                u.user_id,
                u.full_name,
                u.email,
                u.phone,
                sp.student_id,
                sp.department,
                sp.batch
            FROM users u

            JOIN student_profiles sp
                ON sp.user_id = u.user_id

            WHERE u.user_id = %s

            LIMIT 1
            """,
            (user_id,)
        )

        student = cursor.fetchone()

        if student is None:
            return "Student profile not found!", 404


        # =====================================================
        # DASHBOARD STATISTICS
        # =====================================================

        cursor.execute(
            """
            SELECT

                (
                    SELECT COUNT(*)
                    FROM club_memberships
                    WHERE student_id = %s
                    AND status = 'APPROVED'
                ) AS active_memberships,

                (
                    SELECT COUNT(*)
                    FROM club_applications
                    WHERE student_user_id = %s
                    AND status = 'PENDING'
                ) AS pending_applications,

                (
                    SELECT COUNT(*)
                    FROM events
                    WHERE status = 'UPCOMING'
                ) AS upcoming_events,

                (
                    SELECT COUNT(*)
                    FROM clubs
                    WHERE status = 'ACTIVE'
                ) AS available_clubs
            """,
            (
                user_id,
                user_id
            )
        )

        dashboard_stats = cursor.fetchone()


        # =====================================================
        # STUDENT MEMBERSHIPS
        # =====================================================

        cursor.execute(
            """
            SELECT
                cm.membership_id,
                cm.status,
                cm.joined_at,

                c.club_id,
                c.name AS club_name,
                c.category

            FROM club_memberships cm

            JOIN clubs c
                ON c.club_id = cm.club_id

            WHERE cm.student_id = %s
            AND cm.status = 'APPROVED'

            ORDER BY cm.joined_at DESC

            LIMIT 4
            """,
            (user_id,)
        )

        memberships = cursor.fetchall()


        # =====================================================
        # UPCOMING EVENTS
        # =====================================================

        cursor.execute(
            """
            SELECT
                e.event_id,
                e.title,
                e.event_date,
                e.location,

                COALESCE(
                    c.name,
                    'BUP Event'
                ) AS club_name

            FROM events e

            LEFT JOIN clubs c
                ON c.club_id = e.club_id

            WHERE e.status = 'UPCOMING'

            ORDER BY
                e.event_date ASC,
                e.start_time ASC

            LIMIT 5
            """
        )

        upcoming_events = cursor.fetchall()


        # =====================================================
        # RECENT NOTICES
        # =====================================================

        cursor.execute(
            """
            SELECT
                n.notice_id,
                n.title,
                n.created_at,

                COALESCE(
                    c.name,
                    'BUP'
                ) AS club_name

            FROM notices n

            LEFT JOIN clubs c
                ON c.club_id = n.club_id

            WHERE n.status = 'PUBLISHED'

            ORDER BY n.created_at DESC

            LIMIT 5
            """
        )

        recent_notices = cursor.fetchall()


        # =====================================================
        # RENDER DASHBOARD
        # =====================================================

        return render_template(
            "student_dashboard.html",
            student=student,
            dashboard_stats=dashboard_stats,
            memberships=memberships,
            upcoming_events=upcoming_events,
            recent_notices=recent_notices
        )


    except Exception as error:

        return f"Student dashboard failed: {error}"


    finally:

        if cursor:
            cursor.close()

        if (
            connection
            and connection.is_connected()
        ):
            connection.close()
# =========================================================
# Club Moderator Dashboard
# =========================================================

@app.route("/moderator-dashboard")
def moderator_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "CLUB_MODERATOR":
        return "Access denied!"

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -----------------------------------------
        # Get Assigned Club
        # -----------------------------------------

        cursor.execute(
            """
            SELECT
                cm.moderator_id,
                cm.club_id,
                cm.is_active,
                c.name AS club_name,
                c.category,
                c.status,
                c.description
            FROM club_moderators cm
            JOIN clubs c
                ON cm.club_id = c.club_id
            WHERE cm.user_id = %s
            AND cm.is_active = TRUE
            """,
            (session["user_id"],)
        )

        moderator_club = cursor.fetchone()

        if moderator_club is None:
            return "No active club assignment found!"

        club_id = moderator_club["club_id"]

        # -----------------------------------------
        # Dashboard Statistics
        # -----------------------------------------

        cursor.execute(
            """
            SELECT

                (
                    SELECT COUNT(*)
                    FROM club_memberships
                    WHERE club_id = %s
                    AND status = 'PENDING'
                ) AS pending_requests,

                (
                    SELECT COUNT(*)
                    FROM club_memberships
                    WHERE club_id = %s
                    AND status = 'APPROVED'
                ) AS total_members,

                (
                    SELECT COUNT(*)
                    FROM events
                    WHERE club_id = %s
                    AND event_type = 'CLUB'
                    AND status = 'UPCOMING'
                ) AS upcoming_events,

                (
                    SELECT COUNT(*)
                    FROM notices
                    WHERE club_id = %s
                    AND notice_type = 'CLUB'
                    AND status = 'PUBLISHED'
                ) AS published_notices

            """,
            (
                club_id,
                club_id,
                club_id,
                club_id
            )
        )

        moderator_stats = cursor.fetchone()

        return render_template(
            "moderator_dashboard.html",
            moderator_club=moderator_club,
            moderator_stats=moderator_stats
        )

    except Exception as error:
        return f"Moderator dashboard failed: {error}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
            # =========================================================
# Club Moderator - Membership Requests
# =========================================================

@app.route("/moderator/membership-requests")
def moderator_membership_requests():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "CLUB_MODERATOR":
        return "Access denied!"

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -----------------------------------------
        # Get Moderator Assigned Club
        # -----------------------------------------

        cursor.execute(
            """
            SELECT
                cm.club_id,
                c.name AS club_name
            FROM club_moderators cm
            JOIN clubs c
                ON cm.club_id = c.club_id
            WHERE cm.user_id = %s
            AND cm.is_active = TRUE
            """,
            (session["user_id"],)
        )

        moderator_club = cursor.fetchone()

        if moderator_club is None:
            return "No active club assignment found!"

        club_id = moderator_club["club_id"]

        # -----------------------------------------
        # Get Pending Membership Requests
        # -----------------------------------------

        cursor.execute(
            """
            SELECT
                cm.membership_id,
                cm.student_id,
                cm.status,
                cm.requested_at,

                u.full_name,
                u.email,
                u.phone,

                sp.student_id AS university_student_id,
                sp.department,
                sp.batch

            FROM club_memberships cm

            JOIN users u
                ON cm.student_id = u.user_id

            LEFT JOIN student_profiles sp
                ON u.user_id = sp.user_id

            WHERE cm.club_id = %s
            AND cm.status = 'PENDING'

            ORDER BY cm.requested_at ASC
            """,
            (club_id,)
        )

        membership_requests = cursor.fetchall()

        return render_template(
            "moderator_membership_requests.html",
            moderator_club=moderator_club,
            membership_requests=membership_requests
        )

    except Exception as error:
        return f"Membership requests loading failed: {error}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
            # =========================================================
# Club Moderator - Approve Membership
# =========================================================

@app.route(
    "/moderator/membership-requests/<int:membership_id>/approve",
    methods=["POST"]
)
def moderator_approve_membership(membership_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "CLUB_MODERATOR":
        return "Access denied!"

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check that this membership belongs to
        # the moderator's assigned active club
        cursor.execute(
            """
            SELECT
                cm.membership_id,
                cm.student_id,
                cm.club_id
            FROM club_memberships cm

            JOIN club_moderators m
    ON cm.club_id = m.club_id

WHERE cm.membership_id = %s
AND cm.status = 'PENDING'
AND m.user_id = %s
AND m.is_active = TRUE
            """,
            (
                membership_id,
                session["user_id"]
            )
        )

        membership = cursor.fetchone()

        if membership is None:
            return "Membership request not found or access denied!"

        cursor.execute(
            """
            UPDATE club_memberships
            SET
                status = 'APPROVED',
                reviewed_by = %s,
                reviewed_at = CURRENT_TIMESTAMP,
                joined_at = CURRENT_TIMESTAMP
            WHERE membership_id = %s
            """,
            (
                session["user_id"],
                membership_id
            )
        )

        connection.commit()

        return redirect(
            url_for("moderator_membership_requests")
        )

    except Exception as error:

        if connection:
            connection.rollback()

        return f"Membership approval failed: {error}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# Club Moderator - Reject Membership
# =========================================================

@app.route(
    "/moderator/membership-requests/<int:membership_id>/reject",
    methods=["POST"]
)
def moderator_reject_membership(membership_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "CLUB_MODERATOR":
        return "Access denied!"

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                cm.membership_id,
                cm.student_id,
                cm.club_id
            FROM club_memberships cm

            JOIN club_moderators m
    ON cm.club_id = m.club_id

WHERE cm.membership_id = %s
AND cm.status = 'PENDING'
AND m.user_id = %s
AND m.is_active = TRUE
            """,
            (
                membership_id,
                session["user_id"]
            )
        )

        membership = cursor.fetchone()

        if membership is None:
            return "Membership request not found or access denied!"

        cursor.execute(
            """
            UPDATE club_memberships
            SET
                status = 'REJECTED',
                reviewed_by = %s,
                reviewed_at = CURRENT_TIMESTAMP,
                joined_at = NULL
            WHERE membership_id = %s
            """,
            (
                session["user_id"],
                membership_id
            )
        )

        connection.commit()

        return redirect(
            url_for("moderator_membership_requests")
        )

    except Exception as error:

        if connection:
            connection.rollback()

        return f"Membership rejection failed: {error}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
        # =========================================================
# Club Moderator - Approved Members
# =========================================================

@app.route("/moderator/members")
def moderator_members():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "CLUB_MODERATOR":
        return "Access denied!"

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -----------------------------------------
        # Get Moderator Assigned Club
        # -----------------------------------------

        cursor.execute(
            """
            SELECT
                cm.club_id,
                c.name AS club_name
            FROM club_moderators cm
            JOIN clubs c
                ON cm.club_id = c.club_id
            WHERE cm.user_id = %s
            AND cm.is_active = TRUE
            """,
            (session["user_id"],)
        )

        moderator_club = cursor.fetchone()

        if moderator_club is None:
            return "No active club assignment found!"

        club_id = moderator_club["club_id"]

        # -----------------------------------------
        # Get Approved Members
        # -----------------------------------------

        cursor.execute(
            """
            SELECT
                cm.membership_id,
                cm.student_id,
                cm.status,
                cm.requested_at,
                cm.joined_at,

                u.full_name,
                u.email,
                u.phone,

                sp.student_id AS university_student_id,
                sp.department,
                sp.batch

            FROM club_memberships cm

            JOIN users u
                ON cm.student_id = u.user_id

            LEFT JOIN student_profiles sp
                ON u.user_id = sp.user_id

            WHERE cm.club_id = %s
            AND cm.status = 'APPROVED'

            ORDER BY
                cm.joined_at DESC,
                u.full_name ASC
            """,
            (club_id,)
        )

        members = cursor.fetchall()

        return render_template(
            "moderator_members.html",
            moderator_club=moderator_club,
            members=members
        )

    except Exception as error:
        return f"Members loading failed: {error}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

@app.route("/moderator/application-questions")
def moderator_application_questions():

    # Login check
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Only club moderators
    if session.get("role") != "CLUB_MODERATOR":
        return "Unauthorized access", 403

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:

        # -----------------------------------------------------
        # Get moderator's assigned club
        # -----------------------------------------------------

        cursor.execute(
            """
            SELECT
                c.club_id,
                c.name AS club_name,
                c.category
            FROM club_moderators cm
            JOIN clubs c
                ON c.club_id = cm.club_id
            WHERE cm.user_id = %s
            AND cm.is_active = TRUE
            AND c.status = 'ACTIVE'
            LIMIT 1
            """,
            (session["user_id"],)
        )

        moderator_club = cursor.fetchone()

        if not moderator_club:
            return "No active club assigned to this moderator.", 403


        # -----------------------------------------------------
        # Get only this club's application questions
        # -----------------------------------------------------

        cursor.execute(
            """
            SELECT
                question_id,
                question_text,
                question_type,
                options_json,
                is_required,
                sort_order,
                is_active,
                created_at,
                updated_at
            FROM club_application_questions
            WHERE club_id = %s
            ORDER BY sort_order ASC, question_id ASC
            """,
            (moderator_club["club_id"],)
        )

        questions = cursor.fetchall()


        return render_template(
            "moderator_application_questions.html",
            moderator_club=moderator_club,
            questions=questions
        )

    finally:

        cursor.close()
        connection.close()
        # =========================================================
# Club Moderator - Add Application Question
# =========================================================

@app.route(
    "/moderator/application-questions/add",
    methods=["POST"]
)
def moderator_add_application_question():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "CLUB_MODERATOR":
        return "Unauthorized access", 403

    question_text = request.form.get(
        "question_text",
        ""
    ).strip()

    question_type = request.form.get(
        "question_type",
        "SHORT_TEXT"
    ).strip()

    question_options = request.form.get(
        "question_options",
        ""
    ).strip()

    is_required = (
        1 if request.form.get("is_required") else 0
    )

    try:
        sort_order = int(
            request.form.get("sort_order", 1)
        )
    except ValueError:
        sort_order = 1

    # -----------------------------------------
    # Validation
    # -----------------------------------------

    if not question_text:
        return "Question text is required!"

    allowed_types = {
        "SHORT_TEXT",
        "LONG_TEXT",
        "YES_NO",
        "SINGLE_CHOICE"
    }

    if question_type not in allowed_types:
        return "Invalid question type!"

    if sort_order < 1:
        sort_order = 1

    options_json = None

    if question_type == "SINGLE_CHOICE":

        options = [
            option.strip()
            for option in question_options.split(",")
            if option.strip()
        ]

        if len(options) < 2:
            return (
                "Single Choice question must have "
                "at least 2 options."
            )

        options_json = json.dumps(options)

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(
            dictionary=True
        )

        # -----------------------------------------
        # Get Moderator Assigned Club
        # -----------------------------------------

        cursor.execute(
            """
            SELECT
                cm.club_id
            FROM club_moderators cm

            JOIN clubs c
                ON cm.club_id = c.club_id

            WHERE cm.user_id = %s
            AND cm.is_active = TRUE
            AND c.status = 'ACTIVE'

            LIMIT 1
            """,
            (session["user_id"],)
        )

        moderator_club = cursor.fetchone()

        if moderator_club is None:
            return (
                "No active club assignment found!",
                403
            )

        club_id = moderator_club["club_id"]

        # -----------------------------------------
        # Insert Question
        # -----------------------------------------

        cursor.execute(
            """
            INSERT INTO club_application_questions
            (
                club_id,
                question_text,
                question_type,
                options_json,
                is_required,
                sort_order,
                is_active,
                created_by,
                updated_by
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                TRUE,
                %s,
                %s
            )
            """,
            (
                club_id,
                question_text,
                question_type,
                options_json,
                is_required,
                sort_order,
                session["user_id"],
                session["user_id"]
            )
        )

        connection.commit()

        return redirect(
            url_for(
                "moderator_application_questions"
            )
        )

    except Exception as error:

        if connection:
            connection.rollback()

        return (
            f"Question creation failed: {error}"
        )

    finally:

        if cursor:
            cursor.close()

        if (
            connection
            and connection.is_connected()
        ):
            connection.close()
# =========================================================
# Club Moderator - Enable / Disable Application Question
# =========================================================

@app.route(
    "/moderator/application-questions/<int:question_id>/toggle",
    methods=["POST"]
)
def moderator_toggle_application_question(question_id):

    # -----------------------------------------
    # Login Check
    # -----------------------------------------

    if "user_id" not in session:
        return redirect(url_for("login"))

    # -----------------------------------------
    # Only Club Moderator
    # -----------------------------------------

    if session.get("role") != "CLUB_MODERATOR":
        return "Unauthorized access", 403

    # -----------------------------------------
    # Get Requested Action
    # -----------------------------------------

    action = request.form.get("action", "").strip().lower()

    if action not in ("enable", "disable"):
        return "Invalid action!", 400

    if action == "enable":
        new_status = 1
    else:
        new_status = 0

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # -----------------------------------------
        # Verify Question Belongs To
        # Moderator's Assigned Club
        # -----------------------------------------

        cursor.execute(
            """
            SELECT
                q.question_id,
                q.club_id,
                q.is_active

            FROM club_application_questions q

            JOIN club_moderators cm
                ON q.club_id = cm.club_id

            WHERE q.question_id = %s

            AND cm.user_id = %s

            AND cm.is_active = TRUE

            LIMIT 1
            """,
            (
                question_id,
                session["user_id"]
            )
        )

        question = cursor.fetchone()

        if question is None:
            return (
                "Question not found or access denied!",
                403
            )

        # -----------------------------------------
        # Update Question Status
        # -----------------------------------------

        cursor.execute(
            """
            UPDATE club_application_questions

            SET
                is_active = %s,
                updated_by = %s

            WHERE question_id = %s
            """,
            (
                new_status,
                session["user_id"],
                question_id
            )
        )

        connection.commit()

        # -----------------------------------------
        # Back To Questions Page
        # -----------------------------------------

        return redirect(
            url_for(
                "moderator_application_questions"
            )
        )

    except Exception as error:

        if connection:
            connection.rollback()

        return (
            f"Question status update failed: {error}"
        )

    finally:

        if cursor:
            cursor.close()

        if (
            connection
            and connection.is_connected()
        ):
            connection.close() 

    # =========================================================
# Club Moderator - Edit Application Question
# =========================================================

@app.route(
    "/moderator/application-questions/<int:question_id>/edit",
    methods=["POST"]
)
def moderator_edit_application_question(question_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "CLUB_MODERATOR":
        return "Unauthorized access", 403

    question_text = request.form.get(
        "question_text",
        ""
    ).strip()

    question_type = request.form.get(
        "question_type",
        "SHORT_TEXT"
    ).strip()

    question_options = request.form.get(
        "question_options",
        ""
    ).strip()

    is_required = (
        1 if request.form.get("is_required") else 0
    )

    try:
        sort_order = int(
            request.form.get("sort_order", 1)
        )
    except ValueError:
        sort_order = 1

    # -----------------------------------------
    # Validation
    # -----------------------------------------

    if not question_text:
        return "Question text is required!", 400

    if len(question_text) < 5:
        return "Question must be at least 5 characters.", 400

    if len(question_text) > 500:
        return "Question cannot exceed 500 characters.", 400

    allowed_types = {
        "SHORT_TEXT",
        "LONG_TEXT",
        "YES_NO",
        "SINGLE_CHOICE"
    }

    if question_type not in allowed_types:
        return "Invalid question type!", 400

    if sort_order < 1:
        sort_order = 1

    options_json = None

    if question_type == "SINGLE_CHOICE":

        options = [
            option.strip()
            for option in question_options.split(",")
            if option.strip()
        ]

        unique_options = []

        for option in options:

            if option.lower() not in [
                item.lower()
                for item in unique_options
            ]:
                unique_options.append(option)

        if len(unique_options) < 2:
            return (
                "Single Choice question must have "
                "at least 2 different options.",
                400
            )

        options_json = json.dumps(unique_options)

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(
            dictionary=True
        )

        # -----------------------------------------
        # Verify Question Belongs To
        # Moderator's Assigned Club
        # -----------------------------------------

        cursor.execute(
            """
            SELECT
                q.question_id,
                q.club_id

            FROM club_application_questions q

            JOIN club_moderators cm
                ON q.club_id = cm.club_id

            WHERE q.question_id = %s
            AND cm.user_id = %s
            AND cm.is_active = TRUE

            LIMIT 1
            """,
            (
                question_id,
                session["user_id"]
            )
        )

        question = cursor.fetchone()

        if question is None:
            return (
                "Question not found or access denied!",
                403
            )

        # -----------------------------------------
        # Update Question
        # -----------------------------------------

        cursor.execute(
            """
            UPDATE club_application_questions

            SET
                question_text = %s,
                question_type = %s,
                options_json = %s,
                is_required = %s,
                sort_order = %s,
                updated_by = %s

            WHERE question_id = %s
            """,
            (
                question_text,
                question_type,
                options_json,
                is_required,
                sort_order,
                session["user_id"],
                question_id
            )
        )

        connection.commit()

        return redirect(
            url_for(
                "moderator_application_questions"
            )
        )

    except Exception as error:

        if connection:
            connection.rollback()

        return f"Question update failed: {error}"

    finally:

        if cursor:
            cursor.close()

        if (
            connection
            and connection.is_connected()
        ):
            connection.close()
    # =========================================================
# Student - Professional Profile
# =========================================================

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "STUDENT":
        return "Access denied!", 403

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        # =====================================================
        # BASIC + PROFESSIONAL PROFILE
        # =====================================================

        cursor.execute(
            """
            SELECT
                u.user_id,
                u.full_name,
                u.email,
                u.phone,

                sp.student_id,
                sp.department,
                sp.batch,

                spp.profile_photo,
                spp.bio,
                spp.skills,
                spp.github_url,
                spp.linkedin_url,
                spp.facebook_url,
                spp.portfolio_url,
                spp.cv_url

            FROM users u

            JOIN student_profiles sp
                ON sp.user_id = u.user_id

            LEFT JOIN student_professional_profiles spp
                ON spp.user_id = u.user_id

            WHERE u.user_id = %s

            LIMIT 1
            """,
            (session["user_id"],)
        )

        student = cursor.fetchone()

        if student is None:
            return "Student profile not found!", 404


        # =====================================================
        # PROJECTS
        # =====================================================

        cursor.execute(
            """
            SELECT
                project_id,
                project_title,
                project_description,
                technologies,
                project_url,
                github_url,
                start_date,
                end_date,
                is_ongoing,
                sort_order

            FROM student_projects

            WHERE user_id = %s

            ORDER BY
                sort_order ASC,
                start_date DESC,
                project_id DESC
            """,
            (session["user_id"],)
        )

        projects = cursor.fetchall()
        


        # =====================================================
        # EXPERIENCE
        # =====================================================

        cursor.execute(
            """
            SELECT
                experience_id,
                organization_name,
                role_title,
                experience_type,
                description,
                start_date,
                end_date,
                is_current,
                sort_order

            FROM student_experiences

            WHERE user_id = %s

            ORDER BY
                sort_order ASC,
                start_date DESC,
                experience_id DESC
            """,
            (session["user_id"],)
        )

        experiences = cursor.fetchall()


        # =====================================================
        # ACHIEVEMENTS
        # =====================================================

        cursor.execute(
            """
            SELECT
                achievement_id,
                achievement_title,
                achievement_type,
                organization_name,
                description,
                achievement_date,
                credential_url,
                sort_order

            FROM student_profile_achievements

            WHERE user_id = %s

            ORDER BY
                sort_order ASC,
                achievement_date DESC,
                achievement_id DESC
            """,
            (session["user_id"],)
        )

        profile_achievements = cursor.fetchall()


        # =====================================================
        # PROFILE COMPLETION
        # =====================================================

        profile_fields = [
            student.get("full_name"),
            student.get("email"),
            student.get("phone"),
            student.get("student_id"),
            student.get("department"),
            student.get("batch"),
            student.get("bio"),
            student.get("skills"),
            student.get("github_url"),
            student.get("linkedin_url"),
            student.get("cv_url")
        ]

        completed_fields = sum(
            1
            for field in profile_fields
            if field
        )

        profile_completion = round(
            (
                completed_fields
                / len(profile_fields)
            )
            * 100
        )


        # =====================================================
        # RENDER PROFILE
        # =====================================================

        return render_template(
            "profile.html",
            student=student,
            projects=projects,
            experiences=experiences,
            profile_achievements=profile_achievements,
            profile_completion=profile_completion
        )


    except Exception as error:

        return f"Profile loading failed: {error}", 500


    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
# =========================================================
# Student - Edit Professional Profile
# =========================================================

@app.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "STUDENT":
        return "Access denied!", 403

    connection = None
    cursor = None

    user_id = session["user_id"]

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        # =====================================================
        # UPLOAD FOLDERS
        # =====================================================

        profile_photo_folder = os.path.join(
            app.root_path,
            "static",
            "uploads",
            "profile_photos"
        )

        student_cv_folder = os.path.join(
            app.root_path,
            "static",
            "uploads",
            "student_cvs"
        )


        # Create folders automatically if missing

        os.makedirs(
            profile_photo_folder,
            exist_ok=True
        )

        os.makedirs(
            student_cv_folder,
            exist_ok=True
        )


        # =====================================================
        # LOAD EXISTING PROFESSIONAL PROFILE
        # =====================================================

        cursor.execute(
            """
            SELECT
                profile_photo,
                cv_url

            FROM student_professional_profiles

            WHERE user_id = %s

            LIMIT 1
            """,
            (user_id,)
        )

        existing_professional_profile = cursor.fetchone()


        current_profile_photo = None
        current_cv = None


        if existing_professional_profile:

            current_profile_photo = (
                existing_professional_profile.get(
                    "profile_photo"
                )
            )

            current_cv = (
                existing_professional_profile.get(
                    "cv_url"
                )
            )


        # Keep old files until database update succeeds

        old_profile_photo = current_profile_photo
        old_cv = current_cv

        new_profile_photo_uploaded = False
        new_cv_uploaded = False


        # =====================================================
        # POST - UPDATE PROFILE
        # =====================================================

        if request.method == "POST":


            # =================================================
            # BASIC INFORMATION
            # =================================================

            full_name = request.form.get(
                "full_name",
                ""
            ).strip()

            phone = request.form.get(
                "phone",
                ""
            ).strip()

            department = request.form.get(
                "department",
                ""
            ).strip()

            batch = request.form.get(
                "batch",
                ""
            ).strip()


            # =================================================
            # PROFESSIONAL INFORMATION
            # =================================================

            bio = request.form.get(
                "bio",
                ""
            ).strip()

            skills = request.form.get(
                "skills",
                ""
            ).strip()

            github_url = request.form.get(
                "github_url",
                ""
            ).strip()

            linkedin_url = request.form.get(
                "linkedin_url",
                ""
            ).strip()

            facebook_url = request.form.get(
                "facebook_url",
                ""
            ).strip()

            portfolio_url = request.form.get(
                "portfolio_url",
                ""
            ).strip()


            # =================================================
            # BASIC VALIDATION
            # =================================================

            if not full_name:
                return "Full name is required!", 400

            if not department:
                return "Department is required!", 400

            if not batch:
                return "Batch is required!", 400


            # =================================================
            # PROFILE PHOTO UPLOAD
            # =================================================

            profile_photo_file = request.files.get(
                "profile_photo_file"
            )


            if (
                profile_photo_file
                and profile_photo_file.filename
            ):

                original_photo_filename = secure_filename(
                    profile_photo_file.filename
                )


                if not original_photo_filename:

                    return (
                        "Invalid profile photo filename.",
                        400
                    )


                if "." not in original_photo_filename:

                    return (
                        "Invalid profile photo file.",
                        400
                    )


                photo_extension = (
                    original_photo_filename
                    .rsplit(".", 1)[1]
                    .lower()
                )


                allowed_photo_extensions = {
                    "jpg",
                    "jpeg",
                    "png",
                    "webp"
                }


                if (
                    photo_extension
                    not in allowed_photo_extensions
                ):

                    return (
                        "Profile photo must be JPG, JPEG, PNG or WEBP.",
                        400
                    )


                # ---------------------------------------------
                # Generate unique filename
                # ---------------------------------------------

                new_photo_filename = (
                    f"{uuid4().hex}.{photo_extension}"
                )


                photo_absolute_path = os.path.join(
                    profile_photo_folder,
                    new_photo_filename
                )


                # ---------------------------------------------
                # Save physical image
                # ---------------------------------------------

                profile_photo_file.save(
                    photo_absolute_path
                )


                # ---------------------------------------------
                # Relative path for database
                # ---------------------------------------------

                current_profile_photo = (
                    f"uploads/profile_photos/"
                    f"{new_photo_filename}"
                )


                new_profile_photo_uploaded = True


            # =================================================
            # CV / RESUME UPLOAD
            # =================================================

            cv_file = request.files.get(
                "cv_file"
            )


            if (
                cv_file
                and cv_file.filename
            ):

                original_cv_filename = secure_filename(
                    cv_file.filename
                )


                if not original_cv_filename:

                    return (
                        "Invalid CV filename.",
                        400
                    )


                if "." not in original_cv_filename:

                    return (
                        "Invalid CV file.",
                        400
                    )


                cv_extension = (
                    original_cv_filename
                    .rsplit(".", 1)[1]
                    .lower()
                )


                allowed_cv_extensions = {
                    "pdf",
                    "doc",
                    "docx"
                }


                if (
                    cv_extension
                    not in allowed_cv_extensions
                ):

                    return (
                        "CV must be PDF, DOC or DOCX.",
                        400
                    )


                # ---------------------------------------------
                # Generate unique filename
                # ---------------------------------------------

                new_cv_filename = (
                    f"{uuid4().hex}.{cv_extension}"
                )


                cv_absolute_path = os.path.join(
                    student_cv_folder,
                    new_cv_filename
                )


                # ---------------------------------------------
                # Save physical CV
                # ---------------------------------------------

                cv_file.save(
                    cv_absolute_path
                )


                # ---------------------------------------------
                # Relative path for database
                # ---------------------------------------------

                current_cv = (
                    f"uploads/student_cvs/"
                    f"{new_cv_filename}"
                )


                new_cv_uploaded = True


            # =================================================
            # UPDATE USERS TABLE
            # =================================================

            cursor.execute(
                """
                UPDATE users

                SET
                    full_name = %s,
                    phone = %s

                WHERE user_id = %s
                """,
                (
                    full_name,
                    phone or None,
                    user_id
                )
            )


            # =================================================
            # UPDATE STUDENT ACADEMIC PROFILE
            # =================================================

            cursor.execute(
                """
                UPDATE student_profiles

                SET
                    department = %s,
                    batch = %s

                WHERE user_id = %s
                """,
                (
                    department,
                    batch,
                    user_id
                )
            )


            # =================================================
            # INSERT / UPDATE PROFESSIONAL PROFILE
            # =================================================

            cursor.execute(
                """
                INSERT INTO student_professional_profiles
                (
                    user_id,
                    profile_photo,
                    bio,
                    skills,
                    github_url,
                    linkedin_url,
                    facebook_url,
                    portfolio_url,
                    cv_url
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )

                ON DUPLICATE KEY UPDATE

                    profile_photo = VALUES(profile_photo),

                    bio = VALUES(bio),

                    skills = VALUES(skills),

                    github_url = VALUES(github_url),

                    linkedin_url = VALUES(linkedin_url),

                    facebook_url = VALUES(facebook_url),

                    portfolio_url = VALUES(portfolio_url),

                    cv_url = VALUES(cv_url)
                """,
                (
                    user_id,
                    current_profile_photo,
                    bio or None,
                    skills or None,
                    github_url or None,
                    linkedin_url or None,
                    facebook_url or None,
                    portfolio_url or None,
                    current_cv
                )
            )


            # =================================================
            # COMMIT DATABASE
            # =================================================

            connection.commit()


            # =================================================
            # DELETE OLD PROFILE PHOTO AFTER SUCCESS
            # =================================================

            if (
                new_profile_photo_uploaded
                and old_profile_photo
                and old_profile_photo
                    != current_profile_photo
                and old_profile_photo.startswith(
                    "uploads/profile_photos/"
                )
            ):

                old_photo_absolute_path = os.path.join(
                    app.root_path,
                    "static",
                    old_profile_photo
                )


                if os.path.isfile(
                    old_photo_absolute_path
                ):

                    try:

                        os.remove(
                            old_photo_absolute_path
                        )

                    except OSError:

                        pass


            # =================================================
            # DELETE OLD CV AFTER SUCCESS
            # =================================================

            if (
                new_cv_uploaded
                and old_cv
                and old_cv != current_cv
                and old_cv.startswith(
                    "uploads/student_cvs/"
                )
            ):

                old_cv_absolute_path = os.path.join(
                    app.root_path,
                    "static",
                    old_cv
                )


                if os.path.isfile(
                    old_cv_absolute_path
                ):

                    try:

                        os.remove(
                            old_cv_absolute_path
                        )

                    except OSError:

                        pass


            # =================================================
            # UPDATE SESSION NAME
            # =================================================

            session["full_name"] = full_name


            # =================================================
            # REDIRECT
            # =================================================

            return redirect(
                url_for("profile")
            )


               # =====================================================
        # GET - LOAD CURRENT PROFILE
        # =====================================================

        cursor.execute(
            """
            SELECT
                u.user_id,
                u.full_name,
                u.email,
                u.phone,

                sp.student_id,
                sp.department,
                sp.batch,

                spp.profile_photo,
                spp.bio,
                spp.skills,
                spp.github_url,
                spp.linkedin_url,
                spp.facebook_url,
                spp.portfolio_url,
                spp.cv_url

            FROM users u

            JOIN student_profiles sp
                ON sp.user_id = u.user_id

            LEFT JOIN student_professional_profiles spp
                ON spp.user_id = u.user_id

            WHERE u.user_id = %s

            LIMIT 1
            """,
            (user_id,)
        )


        student = cursor.fetchone()


        if student is None:
            return "Student profile not found!", 404


        # =====================================================
        # LOAD STUDENT PROJECTS
        # =====================================================

        cursor.execute(
            """
            SELECT
                project_id,
                project_title,
                project_description,
                technologies,
                project_url,
                github_url,
                start_date,
                end_date,
                is_ongoing,
                sort_order

            FROM student_projects

            WHERE user_id = %s

            ORDER BY
                sort_order ASC,
                start_date DESC,
                project_id DESC
            """,
            (user_id,)
        )


        projects = cursor.fetchall()


        # =====================================================
        # RENDER EDIT PROFILE
        # =====================================================

        return render_template(
            "edit_profile.html",
            student=student,
            projects=projects
        )


    except Exception as error:

        if connection:
            connection.rollback()


        return (
            f"Profile update failed: {error}",
            500
        )


    finally:

        if cursor:
            cursor.close()

        if (
            connection
            and connection.is_connected()
        ):
            connection.close()
            # =========================================================
# Student - Add Project
# =========================================================

@app.route("/profile/projects/add", methods=["GET", "POST"])
def add_student_project():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "STUDENT":
        return "Access denied!", 403

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        user_id = session["user_id"]

        # =====================================================
        # POST - CREATE PROJECT
        # =====================================================

        if request.method == "POST":

            project_title = request.form.get(
                "project_title",
                ""
            ).strip()

            project_description = request.form.get(
                "project_description",
                ""
            ).strip()

            technologies = request.form.get(
                "technologies",
                ""
            ).strip()

            project_url = request.form.get(
                "project_url",
                ""
            ).strip()

            github_url = request.form.get(
                "github_url",
                ""
            ).strip()

            start_date = request.form.get(
                "start_date",
                ""
            ).strip()

            end_date = request.form.get(
                "end_date",
                ""
            ).strip()

            is_ongoing = (
                request.form.get("is_ongoing")
                == "1"
            )

            # =================================================
            # VALIDATION
            # =================================================

            if not project_title:
                return "Project title is required!", 400

            if (
                start_date
                and end_date
                and not is_ongoing
                and end_date < start_date
            ):
                return (
                    "End date cannot be earlier than start date.",
                    400
                )

            if is_ongoing:
                end_date = None

            # =================================================
            # INSERT PROJECT
            # =================================================

            cursor.execute(
                """
                INSERT INTO student_projects
                (
                    user_id,
                    project_title,
                    project_description,
                    technologies,
                    project_url,
                    github_url,
                    start_date,
                    end_date,
                    is_ongoing,
                    sort_order
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    user_id,
                    project_title,
                    project_description or None,
                    technologies or None,
                    project_url or None,
                    github_url or None,
                    start_date or None,
                    end_date or None,
                    1 if is_ongoing else 0,
                    1
                )
            )

            connection.commit()

            return redirect(
                url_for("edit_profile")
            )

        # =====================================================
        # GET
        # =====================================================

        return render_template(
            "student_project_form.html",
            project=None,
            form_mode="add"
        )

    except Exception as error:

        if connection:
            connection.rollback()

        return (
            f"Project creation failed: {error}",
            500
        )

    finally:

        if cursor:
            cursor.close()

        if (
            connection
            and connection.is_connected()
        ):
            connection.close()
            # =========================================================
# Student - Edit Project
# =========================================================

@app.route(
    "/profile/projects/<int:project_id>/edit",
    methods=["GET", "POST"]
)
def edit_student_project(project_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "STUDENT":
        return "Access denied!", 403

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        user_id = session["user_id"]

        # =====================================================
        # CHECK PROJECT OWNERSHIP
        # =====================================================

        cursor.execute(
            """
            SELECT
                project_id,
                project_title,
                project_description,
                technologies,
                project_url,
                github_url,
                start_date,
                end_date,
                is_ongoing,
                sort_order

            FROM student_projects

            WHERE project_id = %s
            AND user_id = %s

            LIMIT 1
            """,
            (
                project_id,
                user_id
            )
        )

        project = cursor.fetchone()

        if project is None:
            return "Project not found!", 404


        # =====================================================
        # POST - UPDATE PROJECT
        # =====================================================

        if request.method == "POST":

            project_title = request.form.get(
                "project_title",
                ""
            ).strip()

            project_description = request.form.get(
                "project_description",
                ""
            ).strip()

            technologies = request.form.get(
                "technologies",
                ""
            ).strip()

            project_url = request.form.get(
                "project_url",
                ""
            ).strip()

            github_url = request.form.get(
                "github_url",
                ""
            ).strip()

            start_date = request.form.get(
                "start_date",
                ""
            ).strip()

            end_date = request.form.get(
                "end_date",
                ""
            ).strip()

            is_ongoing = (
                request.form.get("is_ongoing")
                == "1"
            )


            # =================================================
            # VALIDATION
            # =================================================

            if not project_title:
                return "Project title is required!", 400


            if (
                start_date
                and end_date
                and not is_ongoing
                and end_date < start_date
            ):
                return (
                    "End date cannot be earlier than start date.",
                    400
                )


            if is_ongoing:
                end_date = None


            # =================================================
            # UPDATE PROJECT
            # =================================================

            cursor.execute(
                """
                UPDATE student_projects

                SET
                    project_title = %s,
                    project_description = %s,
                    technologies = %s,
                    project_url = %s,
                    github_url = %s,
                    start_date = %s,
                    end_date = %s,
                    is_ongoing = %s

                WHERE project_id = %s
                AND user_id = %s
                """,
                (
                    project_title,
                    project_description or None,
                    technologies or None,
                    project_url or None,
                    github_url or None,
                    start_date or None,
                    end_date or None,
                    1 if is_ongoing else 0,
                    project_id,
                    user_id
                )
            )

            connection.commit()

            return redirect(
                url_for("edit_profile")
            )


        # =====================================================
        # GET - OPEN EDIT FORM
        # =====================================================

        return render_template(
            "student_project_form.html",
            project=project,
            form_mode="edit"
        )


    except Exception as error:

        if connection:
            connection.rollback()

        return (
            f"Project update failed: {error}",
            500
        )


    finally:

        if cursor:
            cursor.close()

        if (
            connection
            and connection.is_connected()
        ):
            connection.close()
            # =========================================================
# Student - Delete Project
# =========================================================

@app.route(
    "/profile/projects/<int:project_id>/delete",
    methods=["POST"]
)
def delete_student_project(project_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "STUDENT":
        return "Access denied!", 403

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        user_id = session["user_id"]

        # =====================================================
        # DELETE ONLY OWN PROJECT
        # =====================================================

        cursor.execute(
            """
            DELETE FROM student_projects

            WHERE project_id = %s
            AND user_id = %s
            """,
            (
                project_id,
                user_id
            )
        )

        connection.commit()

        return redirect(
            url_for("edit_profile")
        )

    except Exception as error:

        if connection:
            connection.rollback()

        return (
            f"Project deletion failed: {error}",
            500
        )

    finally:

        if cursor:
            cursor.close()

        if (
            connection
            and connection.is_connected()
        ):
            connection.close()
            # =========================================================
# Student - Add Experience
# =========================================================

@app.route(
    "/profile/experiences/add",
    methods=["GET", "POST"]
)
def add_student_experience():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "STUDENT":
        return "Access denied!", 403

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        user_id = session["user_id"]

        # =====================================================
        # POST - CREATE EXPERIENCE
        # =====================================================

        if request.method == "POST":

            organization_name = request.form.get(
                "organization_name",
                ""
            ).strip()

            role_title = request.form.get(
                "role_title",
                ""
            ).strip()

            experience_type = request.form.get(
                "experience_type",
                "OTHER"
            ).strip()

            description = request.form.get(
                "description",
                ""
            ).strip()

            start_date = request.form.get(
                "start_date",
                ""
            ).strip()

            end_date = request.form.get(
                "end_date",
                ""
            ).strip()

            is_current = (
                request.form.get("is_current") == "1"
            )


            # =================================================
            # VALIDATION
            # =================================================

            if not organization_name:
                return "Organization name is required!", 400

            if not role_title:
                return "Role title is required!", 400


            allowed_types = {
                "JOB",
                "INTERNSHIP",
                "VOLUNTEER",
                "CLUB",
                "FREELANCE",
                "OTHER"
            }


            if experience_type not in allowed_types:
                experience_type = "OTHER"


            if (
                start_date
                and end_date
                and not is_current
                and end_date < start_date
            ):
                return (
                    "End date cannot be earlier than start date.",
                    400
                )


            if is_current:
                end_date = None


            # =================================================
            # INSERT EXPERIENCE
            # =================================================

            cursor.execute(
                """
                INSERT INTO student_experiences
                (
                    user_id,
                    organization_name,
                    role_title,
                    experience_type,
                    description,
                    start_date,
                    end_date,
                    is_current,
                    sort_order
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    user_id,
                    organization_name,
                    role_title,
                    experience_type,
                    description or None,
                    start_date or None,
                    end_date or None,
                    1 if is_current else 0,
                    1
                )
            )


            connection.commit()


            return redirect(
                url_for("edit_profile")
            )


        # =====================================================
        # GET - OPEN FORM
        # =====================================================

        return render_template(
            "student_experience_form.html",
            experience=None,
            form_mode="add"
        )


    except Exception as error:

        if connection:
            connection.rollback()

        return (
            f"Experience creation failed: {error}",
            500
        )


    finally:

        if cursor:
            cursor.close()

        if (
            connection
            and connection.is_connected()
        ):
            connection.close()
            # =========================================================
# Club Moderator - View All Clubs
# =========================================================

@app.route("/moderator/clubs")
def moderator_clubs():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "CLUB_MODERATOR":
        return "Unauthorized access", 403

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -----------------------------------------
        # Get Moderator Assigned Club
        # -----------------------------------------

        cursor.execute(
            """
            SELECT
                cm.club_id
            FROM club_moderators cm
            WHERE cm.user_id = %s
            AND cm.is_active = TRUE
            LIMIT 1
            """,
            (session["user_id"],)
        )

        moderator_assignment = cursor.fetchone()

        assigned_club_id = None

        if moderator_assignment:
            assigned_club_id = moderator_assignment["club_id"]

        # -----------------------------------------
        # Get All Active Clubs
        # -----------------------------------------

        cursor.execute(
            """
            SELECT
                club_id,
                name,
                category,
                description,
                status
            FROM clubs
            WHERE status = 'ACTIVE'
            ORDER BY name ASC
            """
        )

        club_list = cursor.fetchall()

        return render_template(
            "moderator_clubs.html",
            clubs=club_list,
            assigned_club_id=assigned_club_id
        )

    except Exception as error:

        return f"Clubs loading failed: {error}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# Student - View All Clubs
# =========================================================

@app.route("/clubs")
def clubs():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") not in ("STUDENT", "CLUB_MODERATOR"):
        return "Access denied!", 403
        

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                club_id,
                name,
                category,
                description,
                status
            FROM clubs
            WHERE status = 'ACTIVE'
            ORDER BY name ASC
            """
        )

        club_list = cursor.fetchall()

        return render_template(
            "clubs.html",
            clubs=club_list
        )

    except Exception as error:
        return f"Clubs loading failed: {error}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# Club Details
# =========================================================

@app.route("/clubs/<int:club_id>")
def club_details(club_id):

    # -----------------------------------------------------
    # Login Required
    # -----------------------------------------------------

    if "user_id" not in session:
        return redirect(url_for("login"))

    # -----------------------------------------------------
    # Student + Club Moderator Access
    # -----------------------------------------------------

    if session.get("role") not in (
        "STUDENT",
        "CLUB_MODERATOR"
    ):
        return "Access denied!", 403


    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        # =====================================================
        # GET CLUB DETAILS
        # =====================================================

        cursor.execute(
            """
            SELECT
                club_id,
                name,
                description,
                category,
                history,
                requirements,
                status,
                website_url,
                facebook_url,
                mission,
                vision,
                motto,
                administered_by
            FROM clubs
            WHERE club_id = %s
            LIMIT 1
            """,
            (club_id,)
        )

        club = cursor.fetchone()

        if club is None:
            return "Club not found!", 404


        # =====================================================
        # STUDENT MEMBERSHIP / APPLICATION STATUS
        # =====================================================

        membership_status = None
        application_status = None
        latest_application = None


        # Only Student needs membership/application status.
        # Moderator should only view the public club page.

        if session.get("role") == "STUDENT":


            # -------------------------------------------------
            # GET CURRENT MEMBERSHIP
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT
                    membership_id,
                    status,
                    requested_at,
                    reviewed_at,
                    joined_at
                FROM club_memberships
                WHERE student_id = %s
                AND club_id = %s
                LIMIT 1
                """,
                (
                    session["user_id"],
                    club_id
                )
            )

            membership = cursor.fetchone()

            if membership:
                membership_status = membership["status"]


            # -------------------------------------------------
            # GET LATEST CLUB APPLICATION
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT
                    application_id,
                    status,
                    submitted_at,
                    withdrawn_at,
                    reviewed_by,
                    reviewed_at,
                    rejection_reason,
                    created_at,
                    updated_at
                FROM club_applications
                WHERE student_user_id = %s
                AND club_id = %s
                ORDER BY
                    application_id DESC
                LIMIT 1
                """,
                (
                    session["user_id"],
                    club_id
                )
            )

            latest_application = cursor.fetchone()

            if latest_application:
                application_status = (
                    latest_application["status"]
                )


        # =====================================================
        # GET PUBLISHED CLUB NOTICES
        # =====================================================

        cursor.execute(
            """
            SELECT
                notice_id,
                title,
                content,
                published_at,
                created_at
            FROM notices
            WHERE notice_type = 'CLUB'
            AND club_id = %s
            AND status = 'PUBLISHED'
            ORDER BY
                created_at DESC
            """,
            (club_id,)
        )

        notices = cursor.fetchall()


        # =====================================================
        # GET UPCOMING CLUB EVENTS
        # =====================================================

        cursor.execute(
            """
            SELECT
                event_id,
                title,
                description,
                event_date,
                start_time,
                end_time,
                location,
                status,
                image_url,
                source_url
            FROM events
            WHERE event_type = 'CLUB'
            AND club_id = %s
            AND status = 'UPCOMING'
            ORDER BY
                event_date ASC,
                start_time ASC
            """,
            (club_id,)
        )

        events = cursor.fetchall()


        # =====================================================
        # GET PAST CLUB ACTIVITIES
        # =====================================================

        cursor.execute(
            """
            SELECT
                event_id,
                title,
                description,
                event_date,
                start_time,
                end_time,
                location,
                status,
                image_url,
                source_url
            FROM events
            WHERE event_type = 'CLUB'
            AND club_id = %s
            AND status = 'COMPLETED'
            ORDER BY
                event_date DESC,
                event_id DESC
            """,
            (club_id,)
        )

        past_activities = cursor.fetchall()


        # =====================================================
        # GET PAST ACTIVITY GALLERY IMAGES
        # =====================================================

        cursor.execute(
            """
            SELECT
                event_gallery.gallery_id,
                event_gallery.event_id,
                event_gallery.image_url,
                event_gallery.caption,
                event_gallery.sort_order
            FROM event_gallery

            JOIN events
                ON event_gallery.event_id = events.event_id

            WHERE events.club_id = %s
            AND events.event_type = 'CLUB'
            AND events.status = 'COMPLETED'
            AND event_gallery.is_active = TRUE

            ORDER BY
                events.event_date DESC,
                event_gallery.sort_order ASC,
                event_gallery.gallery_id ASC
            """,
            (club_id,)
        )

        gallery_rows = cursor.fetchall()

        event_galleries = {}

        for image in gallery_rows:

            event_id = image["event_id"]

            if event_id not in event_galleries:
                event_galleries[event_id] = []

            event_galleries[event_id].append(
                image
            )


        # =====================================================
        # GET CLUB LEADERSHIP
        # =====================================================

        cursor.execute(
            """
            SELECT
                leadership_id,
                name,
                role_title,
                academic_designation,
                department,
                email,
                image_url,
                profile_url,
                sort_order
            FROM club_leadership
            WHERE club_id = %s
            AND is_active = TRUE
            ORDER BY
                sort_order ASC,
                leadership_id ASC
            """,
            (club_id,)
        )

        leadership = cursor.fetchall()


        # =====================================================
        # GET CLUB QUICK STATS
        # =====================================================

        cursor.execute(
            """
            SELECT

                (
                    SELECT COUNT(*)
                    FROM club_memberships
                    WHERE club_id = %s
                    AND status = 'APPROVED'
                ) AS total_members,

                (
                    SELECT COUNT(*)
                    FROM events
                    WHERE club_id = %s
                    AND event_type = 'CLUB'
                    AND status = 'UPCOMING'
                ) AS upcoming_events,

                (
                    SELECT COUNT(*)
                    FROM notices
                    WHERE club_id = %s
                    AND notice_type = 'CLUB'
                    AND status = 'PUBLISHED'
                ) AS published_notices,

                (
                    SELECT COUNT(*)
                    FROM events
                    WHERE club_id = %s
                    AND event_type = 'CLUB'
                ) AS total_events
            """,
            (
                club_id,
                club_id,
                club_id,
                club_id
            )
        )

        club_stats = cursor.fetchone()


        # =====================================================
        # GET CLUB ACHIEVEMENTS
        # =====================================================

        cursor.execute(
            """
            SELECT
                achievement_id,
                title,
                description,
                achievement_date,
                status,
                created_at
            FROM achievements
            WHERE club_id = %s
            AND status = 'PUBLISHED'
            ORDER BY
                achievement_date DESC,
                achievement_id DESC
            """,
            (club_id,)
        )

        achievements = cursor.fetchall()


        # =====================================================
        # LOAD CLUB DETAILS PAGE
        # =====================================================

        return render_template(
            "club_details.html",

            club=club,

            membership_status=membership_status,

            application_status=application_status,

            latest_application=latest_application,

            notices=notices,

            events=events,

            leadership=leadership,

            club_stats=club_stats,

            achievements=achievements,

            past_activities=past_activities,

            event_galleries=event_galleries
        )


    except Exception as error:

        return (
            f"Club details loading failed: {error}",
            500
        )


    finally:

        if cursor:
            cursor.close()

        if (
            connection
            and connection.is_connected()
        ):
            connection.close()
# =========================================================
# Event Gallery - View
# =========================================================

@app.route("/events/<int:event_id>/gallery")
def event_gallery(event_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -----------------------------------------
        # Get Event
        # -----------------------------------------

        cursor.execute(
            """
            SELECT
                event_id,
                club_id,
                title,
                description,
                event_date,
                location,
                status,
                image_url,
                source_url
            FROM events
            WHERE event_id = %s
            AND event_type = 'CLUB'
            """,
            (event_id,)
        )

        event = cursor.fetchone()

        if event is None:
            return "Event not found!"
                # -----------------------------------------
        # Gallery Management Permission
        # -----------------------------------------

        can_manage_gallery = False

        if session.get("role") == "ADMIN":
            can_manage_gallery = True

        elif session.get("role") == "CLUB_MODERATOR":

            cursor.execute(
                """
                SELECT moderator_id
                FROM club_moderators
                WHERE user_id = %s
                AND club_id = %s
                AND is_active = TRUE
                """,
                (
                    session["user_id"],
                    event["club_id"]
                )
            )

            moderator = cursor.fetchone()

            if moderator:
                can_manage_gallery = True

        # -----------------------------------------
        # Get Gallery Images
        # -----------------------------------------

        cursor.execute(
            """
            SELECT
                gallery_id,
                image_url,
                caption,
                sort_order
            FROM event_gallery
            WHERE event_id = %s
            AND is_active = TRUE
            ORDER BY
                sort_order ASC,
                gallery_id ASC
            """,
            (event_id,)
        )

        gallery_images = cursor.fetchall()

        return render_template(
            "event_gallery.html",
            event=event,
            gallery_images=gallery_images,
            can_manage_gallery=can_manage_gallery
        )

    except Exception as error:

        return f"Gallery loading failed: {error}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
# =========================================================
# Event Gallery - Upload Images
# ADMIN / Assigned CLUB_MODERATOR only
# =========================================================

@app.route(
    "/events/<int:event_id>/gallery/upload",
    methods=["POST"]
)
def upload_event_gallery(event_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") not in ("ADMIN", "CLUB_MODERATOR"):
        return "Access denied!"

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -----------------------------------------
        # Check Event
        # -----------------------------------------

        cursor.execute(
            """
            SELECT
                event_id,
                club_id,
                title,
                event_type
            FROM events
            WHERE event_id = %s
            """,
            (event_id,)
        )

        event = cursor.fetchone()

        if event is None:
            return "Event not found!"
                # -----------------------------------------
        # Gallery Management Permission
        # -----------------------------------------

        can_manage_gallery = False

        if session.get("role") == "ADMIN":
            can_manage_gallery = True

        elif session.get("role") == "CLUB_MODERATOR":

            cursor.execute(
                """
                SELECT moderator_id
                FROM club_moderators
                WHERE user_id = %s
                AND club_id = %s
                AND is_active = TRUE
                """,
                (
                    session["user_id"],
                    event["club_id"]
                )
            )

            moderator = cursor.fetchone()

            if moderator:
                can_manage_gallery = True
        if event["event_type"] != "CLUB":
            return "Gallery upload is only available for club events!"

        # -----------------------------------------
        # Moderator Permission Check
        # -----------------------------------------

        if session.get("role") == "CLUB_MODERATOR":

            cursor.execute(
                """
                SELECT moderator_id
                FROM club_moderators
                WHERE user_id = %s
                AND club_id = %s
                AND is_active = TRUE
                """,
                (
                    session["user_id"],
                    event["club_id"]
                )
            )

            moderator = cursor.fetchone()

            if moderator is None:
                return "You are not assigned to this club!"

        # -----------------------------------------
        # Get Uploaded Images
        # -----------------------------------------

        images = request.files.getlist("gallery_images")

        if not images:
            return "No images selected!"

        valid_images = []

        for image in images:

            if not image or not image.filename:
                continue

            if not allowed_image_file(image.filename):
                continue

            valid_images.append(image)

        if not valid_images:
            return "No valid image files selected!"

        # -----------------------------------------
        # Event Specific Upload Folder
        # -----------------------------------------

        event_folder = os.path.join(
            app.config["EVENT_GALLERY_UPLOAD_FOLDER"],
            str(event_id)
        )

        os.makedirs(
            event_folder,
            exist_ok=True
        )

        # -----------------------------------------
        # Current Sort Order
        # -----------------------------------------

        cursor.execute(
            """
            SELECT COALESCE(MAX(sort_order), 0) AS max_sort_order
            FROM event_gallery
            WHERE event_id = %s
            """,
            (event_id,)
        )

        sort_data = cursor.fetchone()

        next_sort_order = (
            sort_data["max_sort_order"] + 1
        )

        uploaded_count = 0

        # -----------------------------------------
        # Save Images
        # -----------------------------------------

        for image in valid_images:

            original_filename = secure_filename(
                image.filename
            )

            extension = original_filename.rsplit(
                ".",
                1
            )[1].lower()

            unique_filename = (
                f"{uuid4().hex}.{extension}"
            )

            absolute_path = os.path.join(
                event_folder,
                unique_filename
            )

            image.save(
                absolute_path
            )

            relative_path = (
                f"uploads/event_gallery/"
                f"{event_id}/"
                f"{unique_filename}"
            )

            cursor.execute(
                """
                INSERT INTO event_gallery
                (
                    event_id,
                    image_url,
                    caption,
                    sort_order,
                    is_active
                )
                VALUES
                (
                    %s,
                    %s,
                    NULL,
                    %s,
                    TRUE
                )
                """,
                (
                    event_id,
                    relative_path,
                    next_sort_order
                )
            )

            next_sort_order += 1
            uploaded_count += 1

        connection.commit()

        return (
            f"{uploaded_count} gallery image(s) "
            f"uploaded successfully!"
        )

    except Exception as error:

        if connection:
            connection.rollback()

        return f"Gallery upload failed: {error}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()



# =========================================================
# Student - My Memberships
# =========================================================

@app.route("/my-memberships")
def my_memberships():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "STUDENT":
        return "Access denied!"

    connection = None
    cursor = None

    try:
        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                club_memberships.membership_id,
                club_memberships.club_id,
                club_memberships.status,
                club_memberships.requested_at,
                club_memberships.joined_at,
                clubs.name,
                clubs.category
            FROM club_memberships
            JOIN clubs
                ON club_memberships.club_id = clubs.club_id
            WHERE club_memberships.student_id = %s
            ORDER BY
                club_memberships.requested_at DESC
            """,
            (
                session["user_id"],
            )
        )

        memberships = cursor.fetchall()

        return render_template(
            "my_memberships.html",
            memberships=memberships
        )

    except Exception as error:
        return f"Memberships loading failed: {error}"

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

# =========================================================
# Student - My Applications
# =========================================================

@app.route("/my-applications")
def my_applications():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "STUDENT":
        return "Access denied!", 403

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # =====================================================
        # GET ALL APPLICATIONS OF LOGGED-IN STUDENT
        # =====================================================

        cursor.execute(
            """
            SELECT
                ca.application_id,
                ca.club_id,
                ca.status,
                ca.submitted_at,
                ca.withdrawn_at,
                ca.reviewed_at,
                ca.rejection_reason,
                ca.created_at,

                c.name AS club_name,
                c.category AS club_category

            FROM club_applications ca

            JOIN clubs c
                ON ca.club_id = c.club_id

            WHERE ca.student_user_id = %s

            ORDER BY
                COALESCE(
                    ca.submitted_at,
                    ca.created_at
                ) DESC,
                ca.application_id DESC
            """,
            (
                session["user_id"],
            )
        )

        applications = cursor.fetchall()


        # =====================================================
        # APPLICATION STATISTICS
        # =====================================================

        application_stats = {
            "total": 0,
            "pending": 0,
            "approved": 0,
            "rejected": 0,
            "withdrawn": 0
        }


        for application in applications:

            application_stats["total"] += 1

            if application["status"] == "PENDING":

                application_stats["pending"] += 1

            elif application["status"] == "APPROVED":

                application_stats["approved"] += 1

            elif application["status"] == "REJECTED":

                application_stats["rejected"] += 1

            elif application["status"] == "WITHDRAWN":

                application_stats["withdrawn"] += 1


        # =====================================================
        # LOAD PAGE
        # =====================================================

        return render_template(
            "my_applications.html",
            applications=applications,
            application_stats=application_stats
        )


    except Exception as error:

        return (
            f"Applications loading failed: {error}",
            500
        )


    finally:

        if cursor:
            cursor.close()

        if (
            connection
            and connection.is_connected()
        ):
            connection.close()
            # =========================================================
# Student - Withdraw Club Application
# =========================================================

@app.route(
    "/applications/<int:application_id>/withdraw",
    methods=["POST"]
)
def withdraw_application(application_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "STUDENT":
        return "Access denied!", 403

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        # =====================================================
        # FIND APPLICATION
        # =====================================================

        cursor.execute(
            """
            SELECT
                application_id,
                student_user_id,
                status
            FROM club_applications
            WHERE application_id = %s
            AND student_user_id = %s
            LIMIT 1
            """,
            (
                application_id,
                session["user_id"]
            )
        )

        application = cursor.fetchone()


        # =====================================================
        # APPLICATION MUST BELONG TO STUDENT
        # =====================================================

        if application is None:

            return (
                "Application not found!",
                404
            )


        # =====================================================
        # ONLY PENDING APPLICATION CAN BE WITHDRAWN
        # =====================================================

        if application["status"] != "PENDING":

            return (
                "Only pending applications can be withdrawn.",
                400
            )


        # =====================================================
        # WITHDRAW APPLICATION
        # =====================================================

        cursor.execute(
            """
            UPDATE club_applications

            SET
                status = 'WITHDRAWN',
                withdrawn_at = CURRENT_TIMESTAMP

            WHERE application_id = %s
            AND student_user_id = %s
            AND status = 'PENDING'
            """,
            (
                application_id,
                session["user_id"]
            )
        )


        connection.commit()


        # =====================================================
        # RETURN TO MY APPLICATIONS
        # =====================================================

        return redirect(
            url_for("my_applications")
        )


    except Exception as error:

        if connection:
            connection.rollback()

        return (
            f"Application withdrawal failed: {error}",
            500
        )


    finally:

        if cursor:
            cursor.close()

        if (
            connection
            and connection.is_connected()
        ):
            connection.close()
# =========================================================
# Logout
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# Run Application
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)