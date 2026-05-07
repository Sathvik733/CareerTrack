from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    date_applied = db.Column(db.String(20), nullable=False)
    job_link = db.Column(db.String(300))
    notes = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.clear()

        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return "Invalid email or password"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    jobs = JobApplication.query.filter_by(
        user_id=session['user_id']
    ).all()

    total_jobs = len(jobs)

    applied_jobs = len([
        job for job in jobs
        if job.status == 'Applied'
    ])

    interview_jobs = len([
        job for job in jobs
        if job.status == 'Interview'
    ])

    rejected_jobs = len([
        job for job in jobs
        if job.status == 'Rejected'
    ])

    offer_jobs = len([
        job for job in jobs
        if job.status == 'Offer'
    ])

    return render_template(
        'dashboard.html',
        jobs=jobs,
        total_jobs=total_jobs,
        applied_jobs=applied_jobs,
        interview_jobs=interview_jobs,
        rejected_jobs=rejected_jobs,
        offer_jobs=offer_jobs
    )

@app.route('/add-job', methods=['GET', 'POST'])
def add_job():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        company = request.form.get('company')
        position = request.form.get('position')
        status = request.form.get('status')
        date_applied = request.form.get('date_applied')
        job_link = request.form.get('job_link')
        notes = request.form.get('notes')

        new_job = JobApplication(
            company=company,
            position=position,
            status=status,
            date_applied=date_applied,
            job_link=job_link,
            notes=notes,
            user_id=session['user_id']
        )

        db.session.add(new_job)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('add_job.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/delete-job/<int:job_id>')
def delete_job(job_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    job = JobApplication.query.filter_by(
        id=job_id,
        user_id=session['user_id']
    ).first_or_404()

    db.session.delete(job)
    db.session.commit()

    return redirect(url_for('dashboard'))

@app.route('/edit-job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    job = JobApplication.query.filter_by(
        id=job_id,
        user_id=session['user_id']
    ).first_or_404()

    if request.method == 'POST':
        job.company = request.form.get('company')
        job.position = request.form.get('position')
        job.status = request.form.get('status')
        job.date_applied = request.form.get('date_applied')
        job.job_link = request.form.get('job_link')
        job.notes = request.form.get('notes')

        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('edit_job.html', job=job)

if __name__ == '__main__':
    app.run(debug=True)