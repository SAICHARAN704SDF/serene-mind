from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

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
    mood = db.Column(
        db.Enum(
            'ecstatic',
            'happy',
            'neutral',
            'sad',
            'awful',
            name='mood_enum'
        ),
        nullable=False
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    medical_history = db.Column(db.Text, nullable=False)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    billing_records = db.relationship('BillingRecord', backref='patient', lazy=True)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    license_number = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.Text, nullable=False)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.Enum(
            'scheduled',
            'completed',
            'canceled',
            name='appointment_status_enum'
        ),
        default='scheduled'
    )
    billing_records = db.relationship('BillingRecord', backref='appointment', lazy=True)

class BillingRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    service_description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(
        db.Enum(
            'pending',
            'paid',
            'overdue',
            name='payment_status_enum'
        ),
        default='pending'
    )
    due_date = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
