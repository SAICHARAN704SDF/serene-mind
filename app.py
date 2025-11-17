from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import google.generativeai as genai
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', 'Charan@123').replace('@', '%40')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_name = os.getenv('DB_NAME', 'serenemind')
    database_url = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
else:
    # For production (PostgreSQL), ensure we use psycopg3
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define models after db is created
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class MoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mood = db.Column(db.Enum('ecstatic', 'happy', 'neutral', 'sad', 'awful'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    medical_history = db.Column(db.Text, nullable=False)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    billing_records = db.relationship('BillingRecord', backref='patient', lazy=True)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    license_number = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.Text, nullable=False)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('scheduled', 'completed', 'canceled'), default='scheduled')
    billing_records = db.relationship('BillingRecord', backref='appointment', lazy=True)

class BillingRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    service_description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.Enum('pending', 'paid', 'overdue'), default='pending')
    due_date = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    date_created = db.Column(db.DateTime, default=datetime.utcnow)

# AI Chat setup
genai.configure(api_key=os.getenv('API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash', system_instruction="You are Sarah, a compassionate mental health assistant for Serenemind. You ONLY provide information and support related to mental health, wellness, and emotional well-being. You are NOT a medical doctor and cannot provide medical diagnoses, prescribe medications, or give medical advice. You can discuss: coping strategies, mindfulness techniques, emotional support, general wellness tips, meditation guidance, stress management, and positive affirmations. If someone asks about physical health, medical conditions, or anything outside mental health, politely redirect them to consult appropriate healthcare professionals. Keep your responses warm, empathetic, and focused on mental wellness.")

@app.route('/')
def index():
    return render_template('welcome.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Chatbot routes
@app.route('/chatbot')
def chatbot():
    messages = session.get('chat_history', [])
    return render_template('chatbot.html', messages=messages)

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.form['message']
    messages = session.get('chat_history', [])
    messages.append({'id': len(messages), 'text': user_message, 'sender': 'user'})

    # AI response
    try:
        response = model.generate_content(user_message)
        ai_response = response.text
    except Exception as e:
        ai_response = "I'm sorry, I'm having trouble connecting right now. Please try again later."

    messages.append({'id': len(messages), 'text': ai_response, 'sender': 'ai'})
    session['chat_history'] = messages

    return jsonify({'response': ai_response})

# Music routes
@app.route('/music')
def music():
    songs = Song.query.all()
    return render_template('music.html', songs=songs)

# Breathing routes
@app.route('/breathing')
def breathing():
    return render_template('breathing.html')

# Journal routes
@app.route('/journal')
def journal():
    entries = JournalEntry.query.order_by(JournalEntry.timestamp.desc()).limit(5).all()
    moods = MoodLog.query.order_by(MoodLog.timestamp.desc()).limit(5).all()
    return render_template('journal.html', entries=entries, moods=moods)

@app.route('/add_entry', methods=['POST'])
def add_entry():
    text = request.form['text']
    entry = JournalEntry(text=text)
    db.session.add(entry)
    db.session.commit()
    return redirect(url_for('journal'))

@app.route('/edit_entry/<int:id>', methods=['GET', 'POST'])
def edit_entry(id):
    entry = JournalEntry.query.get_or_404(id)
    if request.method == 'POST':
        entry.text = request.form['text']
        db.session.commit()
        return redirect(url_for('journal'))
    return render_template('edit_entry.html', entry=entry)

@app.route('/delete_entry/<int:id>', methods=['POST'])
def delete_entry(id):
    entry = JournalEntry.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('journal'))

# Mood routes
@app.route('/add_mood', methods=['POST'])
def add_mood():
    mood = request.form['mood']
    log = MoodLog(mood=mood)
    db.session.add(log)
    db.session.commit()
    return redirect(url_for('journal'))

@app.route('/edit_mood/<int:id>', methods=['GET', 'POST'])
def edit_mood(id):
    log = MoodLog.query.get_or_404(id)
    if request.method == 'POST':
        log.mood = request.form['mood']
        db.session.commit()
        return redirect(url_for('journal'))
    return render_template('edit_mood.html', log=log)

@app.route('/delete_mood/<int:id>', methods=['POST'])
def delete_mood(id):
    log = MoodLog.query.get_or_404(id)
    db.session.delete(log)
    db.session.commit()
    return redirect(url_for('journal'))

# EMR routes
@app.route('/patients')
def patients():
    patients = Patient.query.all()
    return render_template('patients.html', patients=patients)

@app.route('/add_patient', methods=['POST'])
def add_patient():
    name = request.form['name']
    dob = request.form['dob']
    contact = request.form['contact']
    medical_history = request.form['medical_history']
    patient = Patient(name=name, dob=dob, contact=contact, medical_history=medical_history)
    db.session.add(patient)
    db.session.commit()
    return redirect(url_for('patients'))

@app.route('/edit_patient/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    patient = Patient.query.get_or_404(id)
    if request.method == 'POST':
        patient.name = request.form['name']
        patient.dob = request.form['dob']
        patient.contact = request.form['contact']
        patient.medical_history = request.form['medical_history']
        db.session.commit()
        return redirect(url_for('patients'))
    return render_template('edit_patient.html', patient=patient)

@app.route('/delete_patient/<int:id>', methods=['POST'])
def delete_patient(id):
    patient = Patient.query.get_or_404(id)
    db.session.delete(patient)
    db.session.commit()
    return redirect(url_for('patients'))

@app.route('/doctors')
def doctors():
    doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors)

@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    name = request.form['name']
    specialization = request.form['specialization']
    contact = request.form['contact']
    license_number = request.form['license_number']
    experience = request.form['experience']
    doctor = Doctor(name=name, specialization=specialization, contact=contact, license_number=license_number, experience=experience)
    db.session.add(doctor)
    db.session.commit()
    return redirect(url_for('doctors'))

@app.route('/edit_doctor/<int:id>', methods=['GET', 'POST'])
def edit_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    if request.method == 'POST':
        doctor.name = request.form['name']
        doctor.specialization = request.form['specialization']
        doctor.contact = request.form['contact']
        doctor.license_number = request.form['license_number']
        doctor.experience = request.form['experience']
        db.session.commit()
        return redirect(url_for('doctors'))
    return render_template('edit_doctor.html', doctor=doctor)

@app.route('/delete_doctor/<int:id>', methods=['POST'])
def delete_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    db.session.delete(doctor)
    db.session.commit()
    return redirect(url_for('doctors'))

@app.route('/appointments')
def appointments():
    appointments = Appointment.query.all()
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    return render_template('appointments.html', appointments=appointments, patients=patients, doctors=doctors)

@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    patient_id = request.form['patient_id']
    doctor_id = request.form['doctor_id']
    date = request.form['date']
    time = request.form['time']
    purpose = request.form['purpose']
    appointment = Appointment(patient_id=patient_id, doctor_id=doctor_id, date=date, time=time, purpose=purpose)
    db.session.add(appointment)
    db.session.commit()
    return redirect(url_for('appointments'))

@app.route('/edit_appointment/<int:id>', methods=['GET', 'POST'])
def edit_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    if request.method == 'POST':
        appointment.patient_id = request.form['patient_id']
        appointment.doctor_id = request.form['doctor_id']
        appointment.date = request.form['date']
        appointment.time = request.form['time']
        appointment.purpose = request.form['purpose']
        appointment.status = request.form['status']
        db.session.commit()
        return redirect(url_for('appointments'))
    return render_template('edit_appointment.html', appointment=appointment, patients=patients, doctors=doctors)

@app.route('/delete_appointment/<int:id>', methods=['POST'])
def delete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    db.session.delete(appointment)
    db.session.commit()
    return redirect(url_for('appointments'))

@app.route('/billing')
def billing():
    billing_records = BillingRecord.query.all()
    patients = Patient.query.all()
    appointments = Appointment.query.all()
    return render_template('billing.html', billing_records=billing_records, patients=patients, appointments=appointments)

@app.route('/add_billing', methods=['POST'])
def add_billing():
    appointment_id = request.form['appointment_id']
    patient_id = request.form['patient_id']
    service_description = request.form['service_description']
    amount = float(request.form['amount'])
    payment_status = request.form['payment_status']
    due_date = request.form['due_date']
    notes = request.form.get('notes', '')
    record = BillingRecord(appointment_id=appointment_id, patient_id=patient_id, service_description=service_description, amount=amount, payment_status=payment_status, due_date=due_date, notes=notes)
    db.session.add(record)
    db.session.commit()
    return redirect(url_for('billing'))

@app.route('/edit_billing/<int:id>', methods=['GET', 'POST'])
def edit_billing(id):
    record = BillingRecord.query.get_or_404(id)
    patients = Patient.query.all()
    appointments = Appointment.query.all()
    if request.method == 'POST':
        record.appointment_id = request.form['appointment_id']
        record.patient_id = request.form['patient_id']
        record.service_description = request.form['service_description']
        record.amount = float(request.form['amount'])
        record.payment_status = request.form['payment_status']
        record.due_date = request.form['due_date']
        record.notes = request.form.get('notes', '')
        db.session.commit()
        return redirect(url_for('billing'))
    return render_template('edit_billing.html', record=record, patients=patients, appointments=appointments)

@app.route('/delete_billing/<int:id>', methods=['POST'])
def delete_billing(id):
    record = BillingRecord.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('billing'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)