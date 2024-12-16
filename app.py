from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import timedelta

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://arpi:userarpi@localhost/inspira_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'inspira_key'
app.permanent_session_lifetime = timedelta(minutes=30)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


translations = {
    "en": {
        "title": "The Smart Choice For Future",
        "subtitle": "Take the next step in your career with top-tier courses...",
        "search_placeholder": "Search for a course...",
        "all_categories": "All Categories",
        "programming": "Programminng",
        "business": "Business",
        "design": "Design",
        "continue": "Continue",
        "buttons": {
                    "log_in": "Log In",
                    "sign_up": "Sign Up"
                }
    },
    "hy": {
        "title": "ԼԱՎԱԳՈՒՅՆ ԸՆՏՐՈՒԹՅՈՒՆԸ ՁԵՐ ԱՊԱԳԱՅԻ ՀԱՄԱՐ",
        "subtitle": "Նախորդ քայլը դեպի ձեր կարիերան՝ բարձրորակ դասընթացներով...",
        "search_placeholder": "Որոնել դասընթաց...",
        "all_categories": "Բոլոր բաժինները",
        "programming": "Ծրագրավորում",
        "business": "Բիզնես",
        "design": "Դիզայն",
        "continue": "Շարունակել",
        "buttons": {
                    "log_in": "Մուտք գործել",
                    "sign_up": "Գրանցվել"
                }
    },
}

@app.route('/')
def default():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    username = session.get('username')
    lang = request.args.get("lang", "en")
    return render_template('home_page.html', lang=lang, username=username, t=translations.get(lang, translations["en"]))

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

@app.route('/course_list')
def course_list_page():
    username = session.get('username')
    return render_template('course_list.html', username=username)

@app.route('/course_main')
def course_main_page():
    username = session.get('username')
    return render_template('course_main.html', username=username)


@app.route('/quiz_home')
def quiz_home():
    username = session.get('username')
    return render_template('quiz_home.html', username=username)

@app.route('/quiz_page')
def quiz_page():
    username = session.get('username')
    return render_template('quiz_page.ejs', username=username)


@app.route('/quiz_result')
def quiz_result():
    username = session.get('username')

    recommended_course = request.args.get('recommended_course', session.get('recommended_course'))
    if not recommended_course:
        recommended_course = "No course recommended"

    return render_template('quizz_result.ejs', username=username, recommended_course=recommended_course)

@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('home'))  


@app.route('/quiz_page')
def quiz_page():
    username = session.get('username')
    return render_template('quiz_page.ejs', username=username)

@app.route('/quiz_result')
def quiz_result():
    username = session.get('username')  
    
    recommended_course = request.args.get('recommended_course', session.get('recommended_course'))
    if not recommended_course:
        recommended_course = "No course recommended"
    
    return render_template('quizz_result.ejs', username=username, recommended_course=recommended_course)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)