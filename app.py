from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production

# --- Streams data ---
streams = {
    'bio_maths': {
        'name': 'Bio-Maths Group',
        'description': 'Biology + Mathematics for Medical and Engineering fields',
        'subjects': ['Biology', 'Mathematics', 'Physics', 'Chemistry'],
        'careers': ['Medical Doctor', 'Engineer', 'Research Scientist', 'Biotechnologist'],
        'min_marks': 60
    },
    'pure_science': {
        'name': 'Pure Science Group',
        'description': 'Physics, Chemistry, Mathematics for Engineering and Pure Sciences',
        'subjects': ['Physics', 'Chemistry', 'Mathematics', 'Computer Science'],
        'careers': ['Engineer', 'Scientist', 'Researcher', 'Data Analyst'],
        'min_marks': 70
    },
    'commerce': {
        'name': 'Commerce Group',
        'description': 'Commerce with Accounts, Business Studies and Economics',
        'subjects': ['Accountancy', 'Business Studies', 'Economics', 'Mathematics'],
        'careers': ['Chartered Accountant', 'Company Secretary', 'Business Manager', 'Banker'],
        'min_marks': 55
    }
}

# --- Home page (Dashboard) ---
@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('home.html')  # Renders home.html for logged-in users

# --- Logout ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Login page ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['logged_in'] = True
        return redirect(url_for('student_login'))  # go to student selection page
    return render_template('login.html')

# --- Student selection page (10th/12th) ---
@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        student_type = request.form.get('student_type')
        if student_type in ['10th', '12th']:
            return redirect(url_for('student_form', student_type=student_type))
        else:
            return render_template('studentlogin.html', error="Please select 10th or 12th.")

    return render_template('studentlogin.html')  # matches your file studentlogin.html

# --- Student form page ---
@app.route('/studentform/<student_type>', methods=['GET', 'POST'])
def student_form(student_type):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if student_type not in ['10th', '12th']:
        return redirect(url_for('student_login'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        interest = request.form.get('interest', '').strip()
        department = request.form.get('department', '').strip()
        place = request.form.get('place', '').strip()  # <-- NEW LINE

        if not all([name, email, phone, place]):
            return render_template('studentform.html', student_type=student_type, error="Fill name, email, phone, and place.")

        # Save to CSV
        csv_file = 'tenth_students.csv' if student_type == '10th' else 'twelfth_students.csv'
        file_exists = os.path.isfile(csv_file)
        try:
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['Name', 'Email', 'Phone', 'Interest', 'Department', 'Place'])  # <-- UPDATED HEADER
                writer.writerow([name, email, phone, interest, department, place])  # <-- UPDATED ROW
            flash('Student registered successfully!')
        except Exception as e:
            flash(f'Error saving data: {str(e)}')
            return render_template('studentform.html', student_type=student_type, error="Failed to save data.")

        return redirect(url_for('home'))


    return render_template('studentform.html', student_type=student_type)  # matches your file studentform.html

# --- 10th Recommendation ---
@app.route('/tenth', methods=['GET', 'POST'])
def tenth():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            maths = int(request.form.get('maths_interest', 0))
            science = int(request.form.get('science_interest', 0))
            bio = int(request.form.get('bio_interest', 0))
            commerce = int(request.form.get('commerce_interest', 0))
            marks = int(request.form.get('current_marks', 0))

            if maths >= 4 and science >= 4 and bio >= 4 and marks >= 70:
                recommended = 'bio_maths'
            elif maths >= 4 and science >= 4 and marks >= 65:
                recommended = 'pure_science'
            elif commerce >= 4 and marks >= 55:
                recommended = 'commerce'
            else:
                recommended = 'Need improvement'

            stream_info = streams.get(recommended, {}) if recommended in streams else {}
            return render_template('tenth.html', recommended=recommended, stream_info=stream_info)
        except ValueError:
            return render_template('tenth.html', error="Enter valid numbers.")

    return render_template('tenth.html')

# --- 12th Recommendation ---
@app.route('/twelfth', methods=['GET', 'POST'])
def twelfth():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            physics = int(request.form.get('physics', 0))
            chemistry = int(request.form.get('chemistry', 0))
            maths = int(request.form.get('maths', 0))
            biology = int(request.form.get('biology', 0))
            english = int(request.form.get('english', 0))

            total = physics + chemistry + maths + biology + english
            pcm = physics + chemistry + maths
            pcb = physics + chemistry + biology

            departments = []
            if pcm >= 240 and maths >= 75 and physics >= 70:
                departments.append('Engineering (B.Tech/B.E.)')
            if pcb >= 240 and biology >= 75 and chemistry >= 70:
                departments.append('Medical (MBBS/BDS)')
            if pcm >= 210 or pcb >= 210:
                departments.append('B.Sc. Pure Sciences')
            if maths >= 60 and total >= 350:
                departments.append('B.Com Commerce')
                departments.append('Business Administration')
            if total >= 300:
                departments.append('Arts and Humanities')
                departments.append('Social Sciences')

            return render_template('twelfth.html', departments=departments)
        except ValueError:
            return render_template('twelfth.html', error="Enter valid numbers.")

    return render_template('twelfth.html')

if __name__ == '__main__':
    app.run(debug=True)
