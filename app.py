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
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))

# --- Login page ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['logged_in'] = True
        return redirect(url_for('student_login'))  # go to student selection page
    # Support GET navigation via query param from templates: /login?type=student
    login_type = request.args.get('type')
    if login_type:
        if login_type == 'student':
            session['logged_in'] = True
            return redirect(url_for('student_login'))
        elif login_type == 'institution':
            return redirect(url_for('institution_login'))
    return render_template('login.html')

# --- Institution Registration ---
@app.route('/institution_register', methods=['GET', 'POST'])
def institution_register():
    if request.method == 'POST':
        institution_name = request.form.get('institution_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Validation
        if not all([institution_name, email, password, phone]):
            return render_template('institution_register.html', error='All fields are required')
        
        if password != confirm_password:
            return render_template('institution_register.html', error='Passwords do not match')
        
        if len(password) < 6:
            return render_template('institution_register.html', error='Password must be at least 6 characters')
        
        # Create data folder if it doesn't exist
        data_folder = 'data'
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        
        # Check if email already exists
        csv_file = os.path.join(data_folder, 'institutions.csv')
        if os.path.isfile(csv_file):
            with open(csv_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['Email'] == email:
                        return render_template('institution_register.html', error='Email already registered')
        
        # Save to CSV in data folder
        file_exists = os.path.isfile(csv_file)
        try:
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['InstitutionName', 'Email', 'Password', 'Phone'])
                writer.writerow([institution_name, email, password, phone])
            
            return render_template('institution_register.html', success='Registration successful! Please login.')
        except Exception as e:
            return render_template('institution_register.html', error=f'Error saving data: {str(e)}')
    
    return render_template('institution_register.html')

# --- Institution Login ---
@app.route('/institution_login', methods=['GET', 'POST'])
def institution_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # Check credentials from CSV file in data folder
        data_folder = 'data'
        csv_file = os.path.join(data_folder, 'institutions.csv')
        
        if os.path.isfile(csv_file):
            with open(csv_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['Email'] == email and row['Password'] == password:
                        session['institution_logged_in'] = True
                        session['institution_email'] = email
                        session['institution_name'] = row['InstitutionName']
                        return redirect(url_for('institution_dashboard'))
        
        return render_template('institution_login.html', error='Invalid email or password')
    
    return render_template('institution_login.html')

# --- Institution Dashboard ---
@app.route('/institution_dashboard')
def institution_dashboard():
    if not session.get('institution_logged_in'):
        return redirect(url_for('institution_login'))
    return render_template('institution_dashboard.html')

# --- View 10th Students ---
@app.route('/view_tenth_students')
def view_tenth_students():
    if not session.get('institution_logged_in'):
        return redirect(url_for('institution_login'))
    
    students = []
    csv_file = 'tenth_students.csv'
    
    if os.path.isfile(csv_file):
        try:
            with open(csv_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                students = list(reader)
        except Exception as e:
            flash(f'Error reading file: {str(e)}')
    
    return render_template('tenth_students_list.html', students=students)

# --- View 12th Students ---
@app.route('/view_twelfth_students')
def view_twelfth_students():
    if not session.get('institution_logged_in'):
        return redirect(url_for('institution_login'))
    
    students = []
    csv_file = 'twelfth_students.csv'
    
    if os.path.isfile(csv_file):
        try:
            with open(csv_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                students = list(reader)
        except Exception as e:
            flash(f'Error reading file: {str(e)}')
    
    return render_template('twelfth_students_list.html', students=students)

# --- Student selection page (10th/12th) ---
@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Support GET navigation: /student_login?student_type=10th|12th
    student_type_q = request.args.get('student_type')
    if student_type_q in ['10th', '12th']:
        return redirect(url_for('student_form', student_type=student_type_q))

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
            department = request.form.get('department', '')
            interests = request.form.getlist('interest')

            # Determine recommendation
            if maths >= 4 and science >= 4 and bio >= 4 and marks >= 70:
                recommended = 'Bio-Maths Group'
                reason = f'Strong interest in Maths({maths}), Science({science}), Biology({bio}) with {marks}% marks'
            elif maths >= 4 and science >= 4 and marks >= 65:
                recommended = 'Pure Science Group'
                reason = f'Strong interest in Maths({maths}) and Science({science}) with {marks}% marks'
            elif commerce >= 4 and marks >= 55:
                recommended = 'Commerce Group'
                reason = f'Strong interest in Commerce({commerce}) with {marks}% marks'
            else:
                recommended = 'Need improvement in marks or interests'
                reason = 'Consider improving your marks or exploring different interest areas'

            return render_template('tenth_result.html', 
                                   maths_interest=maths, 
                                   science_interest=science,
                                   bio_interest=bio, 
                                   commerce_interest=commerce,
                                   current_marks=marks,
                                   recommended=recommended,
                                   reason=reason,
                                   selected_department=department,
                                   selected_interests=', '.join(interests) if interests else 'None')
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
            avg = round(total / 5, 2)
            pcm = physics + chemistry + maths
            pcb = physics + chemistry + biology

            eligible = []
            reasons = []
            
            if pcm >= 240 and maths >= 75 and physics >= 70:
                eligible.append('Engineering (B.Tech/B.E.)')
                reasons.append(f'PCM={pcm}, Maths={maths}, Physics={physics}')
            if pcb >= 240 and biology >= 75 and chemistry >= 70:
                eligible.append('Medical (MBBS/BDS)')
                reasons.append(f'PCB={pcb}, Biology={biology}, Chemistry={chemistry}')
            if pcm >= 210 or pcb >= 210:
                eligible.append('B.Sc. Pure Sciences')
                reasons.append(f'PCM={pcm} or PCB={pcb}')
            if maths >= 60 and total >= 350:
                eligible.append('B.Com Commerce')
                reasons.append(f'Maths={maths}, Total={total}')
                eligible.append('Business Administration')
                reasons.append(f'Maths={maths}, Total={total}')
            if total >= 300:
                eligible.append('Arts and Humanities')
                reasons.append(f'Total={total}')
                eligible.append('Social Sciences')
                reasons.append(f'Total={total}')

            return render_template('twelfth_result.html', 
                                   physics=physics, chemistry=chemistry, 
                                   maths=maths, biology=biology, english=english,
                                   total=total, avg=avg, eligible=eligible, reasons=reasons)
        except ValueError:
            return render_template('twelfth.html', error="Enter valid numbers.")

    return render_template('twelfth.html')

# --- Colleges Page ---
@app.route('/colleges')
def colleges():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('colleges.html')

# --- Schools Page ---
@app.route('/schools')
def schools():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('schools.html')

# --- Stream-specific School Pages ---
@app.route('/biomath_schools')
def biomath_schools():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('biomath_schools.html')

@app.route('/cs_schools')
def cs_schools():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('cs_schools.html')

@app.route('/purescience_schools')
def purescience_schools():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('purescience_schools.html')

@app.route('/accounts_schools')
def accounts_schools():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('accounts_schools.html')

# --- Tenth Result Page (for back navigation) ---
@app.route('/tenth_result')
def tenth_result_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # Redirect to tenth form if accessed directly without data
    return redirect(url_for('tenth'))

# --- Stream-specific College Pages ---
@app.route('/engineering_colleges')
def engineering_colleges():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('engineering_colleges.html')

@app.route('/medical_colleges')
def medical_colleges():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('medical_colleges.html')

@app.route('/commerce_colleges')
def commerce_colleges():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('commerce_colleges.html')

@app.route('/arts_science_colleges')
def arts_science_colleges():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('arts_science_colleges.html')

# --- Twelfth Result Page (for back navigation) ---
@app.route('/twelfth_result')
def twelfth_result_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # Redirect to twelfth form if accessed directly without data
    return redirect(url_for('twelfth'))

if __name__ == '__main__':
    app.run(debug=True)
