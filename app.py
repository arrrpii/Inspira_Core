from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import timedelta, datetime
import pytz
from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_mail import Mail, Message
from translation import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://arpi:userarpi@localhost/inspira_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=30)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SECRET_KEY'] = 'inspira_key'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'inspiraprojet@gmail.com'
app.config['MAIL_PASSWORD'] = 'mxjqvskypjwjbhgm'

mail = Mail(app)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    courses = db.relationship('Course', secondary='enrollment', back_populates='students', overlaps='enrollments')
    deleted = db.Column(db.Boolean, default=False)

    def get_token(self, expires_sec=300):
        serial = Serializer(app.config['SECRET_KEY'], expires_in=expires_sec)
        return serial.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        serial = Serializer(app.config['SECRET_KEY'])
        try:
            user_id=serial.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f'<User {self.username}>'

class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.String(100))
    num_courses = db.Column(db.Integer)
    participants = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255))
    instructor = db.Column(db.String(255), nullable=False)
    level = db.Column(db.String(50), nullable=False)
    learn = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, nullable=False)
    recommend = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=False)
    course_url = db.Column(db.Text, nullable=False)
    students = db.relationship('User', secondary='enrollment', back_populates='courses', overlaps='enrollments')
    category = db.Column(db.String(100), nullable=False)

class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.now(pytz.FixedOffset(240)))
    user = db.relationship('User', backref=db.backref('enrollments', lazy='dynamic'), overlaps="courses,students")
    course = db.relationship('Course', backref=db.backref('enrollments', lazy='dynamic'), overlaps="courses,students")

with app.app_context():
    db.create_all()

@app.route('/')
def default():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    username = session.get('username')
    lang = request.args.get("lang", "en")
    return render_template('home_page.html', lang=lang, username=username, t=translations.get(lang, translations["en"]))


@app.route('/search_courses', methods=['GET'])
def search_courses():
    query = request.args.get('query', '').strip()
    category = request.args.get('category', '').strip()  # Get category from form
    page = int(request.args.get('page', 1))  # Get the current page, default to 1
    per_page = 6  # Number of courses per page

    user_id = session.get('user_id')
    user = User.query.get(user_id)
    is_admin = user.role == 'admin' if user else False

    # Base query
    courses_query = Course.query

    # Apply filters based on input
    if query:
        courses_query = courses_query.filter(Course.name.ilike(f'%{query}%'))
    if category:  # Only filter by category if it's not empty
        courses_query = courses_query.filter(Course.category.ilike(f'%{category}%'))

    # Apply ordering and pagination
    courses_query = courses_query.order_by(Course.id)
    total_courses = courses_query.count()  # Total number of courses
    courses = courses_query.offset((page - 1) * per_page).limit(per_page).all()

    courses_found = len(courses) > 0

    # Calculate if there are more courses to load
    has_more = total_courses > page * per_page

    return render_template(
        'course_list.html',
        courses=courses,
        is_admin=is_admin,
        courses_found=courses_found,
        query=query,
        category=category,
        page=page,
        has_more=has_more
    )


@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if not username or not email or not password or not confirm_password:
            return jsonify({'error': 'All fields are required'}), 400

        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        try:
            msg = Message(subject="Registration Successful", sender="inspiraprojet@gmail.com", recipients=[email])
            msg.body=f'''
                Hello {username},
                
                Thank you for registration. We hope you will enjoy you experience with Inspira. Welcome to our platform!
                
                Thank you,
                The Inspira Team
                
                '''

            mail.send(msg)
        except Exception as mail_error:
            print(f"Error sending email: {mail_error}")
            # Optionally, handle the email sending error here

        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Something went wrong'}), 500


@app.route('/login')
def login_page():
    return render_template('login.html')
@app.route('/login', methods=['POST'])
def login():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"success": False, "message": "Email and password are required"}), 400

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['email'] = user.email
            session['username'] = user.username
            return jsonify({"success": True, "message": "Login successful", "email": user.email, "username": user.username}), 200
        else:
            return jsonify({"success": False, "message": "Invalid email or password"}), 401
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred"}), 500


class ResetRequestForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired()])
    submit = SubmitField(label='Reset Password', validators=[DataRequired()])

class ResetPasswordForm(FlaskForm):
    password = PasswordField(label='Password', validators=[DataRequired()])
    confirm_password = PasswordField(label='Confirm Password', validators=[DataRequired()])
    submit = SubmitField(label='Change Password', validators=[DataRequired()])

def send_email(user):
    token=user.get_token()
    msg = Message('Password Reset Request', recipients=[user.email], sender='noreply@inspira.com')
    msg.body=f'''
    Hello {user.username},

    We received a request to reset your password. To reset it, please visit the link below:
    
    {url_for('reset_token', token=token, _external=True)}
    
    If you did not request this, please ignore this email.
    
    Thank you,
    The Inspira Team
    
    '''

    mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_email(user)
            flash('Reset request sent. Check your email.','success')
            return redirect(url_for('login_page'))
    return render_template('reset_request.html', title='Reset Request', form=form, legend="Reset Password")


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_token(token)
    if user is None:
        flash('That is invalid or expired token. Please try again', 'warning')
        return redirect(url_for('reset_request'))

    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_password
        db.session.commit()
        flash('Password changed. Please log in!','success')
        return redirect(url_for('login_page'))
    return render_template('change_password.html', title='Change Password', legend='Change Password', form=form)

@app.route('/about_us')
def about_us_page():
    username = session.get('username')
    return render_template('about_us.html', username=username)

@app.route('/contact')
def contact():
    username = session.get('username')
    return render_template('contact.html', username=username)

@app.route('/course_home')
def course_home_page():
    username = session.get('username')
    return render_template('course_home.html', username=username)

@app.route('/course_list', methods=['GET'])
def course_list_page():
    username = session.get('username')
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    is_admin = user.role == 'admin' if user else False

    # Get the number of courses already displayed (default 6 for the first load)
    displayed_courses = int(request.args.get('displayed', 6))  # Default to 6 on first load
    per_page = 6  # Number of courses to load per batch

    # Fetch all courses up to the current display count
    courses_query = Course.query.order_by(Course.id.asc())
    total_courses = courses_query.count()
    courses = courses_query.limit(displayed_courses).all()

    # Check if more courses are available to load
    has_more = displayed_courses < total_courses


    return render_template('course_list.html', username=username, is_admin=is_admin, courses=courses, displayed_courses=displayed_courses, per_page=per_page, has_more=has_more)

@app.route('/api/courses', methods=['GET'])
def load_courses():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 6))

    courses_query = Course.query.order_by(Course.id.asc())
    total_courses = courses_query.count()
    courses = courses_query.offset(offset).limit(limit).all()

    has_more = (offset + limit) < total_courses

    # Return the data as JSON for the frontend
    return {
        "courses": [
            {
                "id": course.id,
                "name": course.name,
                "duration": course.duration,
                "num_courses": course.num_courses,
                "participants": course.participants,
                "image_url": course.image_url,
            }
            for course in courses
        ],
        "has_more": has_more
    }

@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    if not user or user.role != 'admin':
        flash("You are not authorized to add courses.", "error")
        return redirect(url_for('course_list'))

    if request.method == 'POST':
        name = request.form.get('name')
        duration = request.form.get('duration')
        category = request.form.get('category')
        num_courses = request.form.get('num_courses')
        image_url = request.form.get('image_url')
        instructor = request.form.get('instructor')
        level = request.form.get('level')
        learn = request.form.get('learn')
        details = request.form.get('details')
        recommend = request.form.get('recommend')
        skills = request.form.get('skills')
        course_url = request.form.get('course_url')

        if not name:
            flash("Course name is required.", "error")
            return redirect(url_for('add_course'))

        new_course = Course(
            name=name,
            duration=duration,
            num_courses=num_courses,
            category=category,
            image_url=image_url,
            instructor=instructor,
            level=level,
            learn=learn,
            details=details,
            recommend=recommend,
            skills=skills,
            course_url=course_url

        )
        db.session.add(new_course)
        db.session.commit()
        flash("Course added successfully.", "success")
        return redirect(url_for('course_list_page'))

    return render_template('add_course.html')


@app.route('/edit_course/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    if not user or user.role != 'admin':
        flash("You are not authorized to edit courses.", "error")
        return redirect(url_for('course_list_page'))

    course = Course.query.get(course_id)

    if not course:
        flash("Course not found.", "error")
        return redirect(url_for('course_list_page'))

    if request.method == 'POST':
        course.name = request.form.get('name')
        course.duration = request.form.get('duration')
        course.category = request.form.get('category')
        course.num_courses = request.form.get('num_courses')
        course.image_url = request.form.get('image_url')
        course.instructor = request.form.get('instructor')
        course.level = request.form.get('level')
        course.learn = request.form.get('learn')
        course.details = request.form.get('details')
        course.recommend = request.form.get('recommend')
        course.skills = request.form.get('skills')
        course.course_url = request.form.get('course_url')

        db.session.commit()
        flash("Course updated successfully.", "success")
        return redirect(url_for('course_list_page'))

    return render_template('edit_course.html', course=course)


@app.route('/delete_course/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    if not user or user.role != 'admin':
        flash("You are not authorized to delete courses.", "error")
        return redirect(url_for('course_list_page'))

    course = Course.query.get(course_id)
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    for enrollment in enrollments:
        if enrollment:
            db.session.delete(enrollment)
    if course:
        db.session.delete(course)
        db.session.commit()
        flash("Course deleted successfully.", "success")
    else:
        flash("Course not found.", "error")

    return redirect(url_for('course_list_page'))

@app.route('/course_main/<int:course_id>')
def course_main_page(course_id):
    course = Course.query.get(course_id)
    if not course:
        flash("Course not found.", "error")
        return redirect(url_for('course_list_page'))

    username = session.get('username')
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    enrolled = user and course in user.courses if user else False
    return render_template('course_main.html', username=username, course=course, enrolled=enrolled)


@app.route('/enroll/<int:course_id>', methods=['POST'])
def enroll(course_id):
    # Check if user is logged in
    if 'user_id' not in session:
        flash("You need to log in to enroll in this course.", "warning")
        return redirect(url_for('login_page'))

    # Get the logged-in user and the course
    user = User.query.get(session['user_id'])
    course = Course.query.get(course_id)

    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for('course_home_page'))

    # Check if user is already enrolled in the course
    if course in user.courses:
        flash("You are already enrolled in this course.", "info")
        return redirect(url_for('course_main_page', course_id=course_id))

    # Enroll the user in the course
    enrollment = Enrollment(user_id=user.id, course_id=course.id)
    db.session.add(enrollment)

    # Update course participants
    course.participants += 1
    db.session.commit()

    msg = Message('Course Enrollment', recipients=[user.email], sender='noreply@inspira.com')
    msg.body = f'''
        Hello {user.username},

        Welcome to {course.name} course! We hope you will enjoy this. You can find course in your account. Also you can access it by the link below.
        
        {url_for('course_main_page', course_id=course_id, _external=True)}

        Thank you,
        The Inspira Team

        '''

    mail.send(msg)

    flash("Successfully enrolled in the course!", "success")
    return redirect(url_for('course_main_page', course_id=course.id))

@app.route('/leave_course/<int:course_id>', methods=['POST'])
def leave_course(course_id):
    # user_id = session.get('user_id')  # This should be the logged-in user's ID
    user = User.query.get(session['user_id'])
    course = Course.query.get(course_id)
    # Check if the user is already enrolled in the course
    enrollment = Enrollment.query.filter_by(user_id=user.id, course_id=course_id).first()

    db.session.delete(enrollment)
    course.participants -= 1
    db.session.commit()
    success_message = "Successfully deactivated the course."
    flash(success_message, 'success')
    msg = Message('We are sad to see you go', recipients=[user.email], sender='noreply@inspira.com')
    msg.body = f'''
            Hello {user.username},

            You have left {course.name} course! We hope you will find another course in Inspira.

            Thank you,
            The Inspira Team

            '''

    mail.send(msg)


    # Redirect back to the course details page with the success message
    return redirect(url_for('course_main_page', course_id=course_id, success_message=success_message))


@app.route('/account')
def my_account():
    user_id = session.get('user_id')  # Get the logged-in user's ID

    if not user_id:
        flash("You need to log in to see your courses.", "warning")
        return redirect(url_for('login_page'))

    # Retrieve the user from the database
    user = User.query.get(user_id)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('home'))

    # Get the list of courses the user is enrolled in
    enrolled_courses = user.courses  # This gives a list of Course objects
    username = session.get('username')
    return render_template('account.html',username=username, courses=enrolled_courses)

@app.route('/delete_account', methods=['POST'])
def delete_account():
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        if not user_id:
            flash("You need to be logged in to delete your account.", "warning")
            return redirect(url_for('login_page'))

        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('home'))

        if user:
            enrollments = Enrollment.query.filter_by(user_id=user_id).all()
            for enrollment in enrollments:
                course = Course.query.get(enrollment.course_id)
                if course:
                    course.participants -= 1
                    db.session.delete(enrollment)

        # Delete the user account
            db.session.delete(user)
            db.session.commit()
            # send_confirmation_email(user.email, enrolled_courses)
            send_confirmation_email(user.email, user.username)
            # Clear session
            session.clear()
        # flash("Your account has been scheduled for deletion. A recovery email has been sent.", "success")
        flash("Your account has been scheduled for deletion.", "success")
        return redirect(url_for('home'))
    except Exception as e:
        print(f"Error deleting account: {e}")
        flash("An error occurred while deleting your account. Please try again.", "danger")
        return redirect(url_for('my_account'))


# def send_confirmation_email(user_email, username, enrolled_courses):
def send_confirmation_email(user_email, username):
    message = Message("Account Deletion Confirmation", recipients=[user_email], sender='inspira.projet@gmailcom')
    message.body = f"""
    Hi {username},

    We're sorry to see you go! Your account has been scheduled for deletion.
    
    Best regards,
    The Inspira Team
    """
    # Send the email
    try:
        mail.send(message)
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route('/quiz_home')
def quiz_home():
    username = session.get('username')
    return render_template('quiz_home.html', username=username)

@app.route('/quiz_page')
def quiz_page():
    username = session.get('username')
    return render_template('quiz_page.ejs', username=username)

def get_course_by_name(course_name):
    # Query your database to get the course details
    courses = Course.query.filter_by(name=course_name).all()  # Retrieves all courses with the same name
    return courses


@app.route('/quiz_result')
def quiz_result():
    username = session.get('username')

    # Get the recommended course name from the query string or session
    recommended_course_name = request.args.get('recommended_course', session.get('recommended_course'))
    if not recommended_course_name:
        recommended_course_name = "No course recommended"

    # Fetch course details from the database based on the recommended course name
    courses = get_course_by_name(recommended_course_name)  # Returns a list of courses

    # Pass the course details to the template
    return render_template('quizz_result.ejs', username=username, courses=courses)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
