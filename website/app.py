from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'secret-key-change-this'

USERS = {
    'doctor': 'password'
}

COUNTRIES = {
    'Germany': ['Tetanus', 'Measles', 'Influenza'],
    'Brazil': ['Yellow Fever', 'Hepatitis A', 'Dengue'],
    'India': ['Typhoid', 'Hepatitis A', 'Rabies']
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if USERS.get(username) == password:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'Ungültige Anmeldedaten'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    advice = None
    if request.method == 'POST':
        country = request.form['country']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            now = datetime.now()
            diff = (start - now).days
        except ValueError:
            diff = 999
        vaccines = COUNTRIES.get(country, [])
        advice = {
            'country': country,
            'start_date': start_date,
            'end_date': end_date,
            'vaccines': vaccines,
            'quick': diff < 30
        }
    return render_template('dashboard.html', countries=COUNTRIES.keys(), advice=advice)

@app.route('/patient-info')
def patient_info():
    if 'user' not in session:
        return redirect(url_for('login'))
    pdfs = os.listdir(os.path.join('static', 'pdfs'))
    return render_template('patient_info.html', pdfs=pdfs)

if __name__ == '__main__':
    app.run(debug=True)
