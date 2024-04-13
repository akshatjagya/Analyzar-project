import os
import random
import string
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import cv2
import pytesseract
import psycopg2
from openai import OpenAI

app = Flask(__name__)
app.config['SECRET_KEY'] = '1223Akshat'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Database connection details
connection_config = {
    'dsn': "postgres://analyzar_db_e8ou_user:oNSbiWJurpryUxZNIjjorWwUJPq4I0e4@dpg-co7ek8cf7o1s73cm96rg-a.singapore-postgres.render.com/analyzar_db_e8ou"
}

# Initialize OpenAI client
client = OpenAI(api_key="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")

# Generate unique code
def generate_unique_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(10))

# Process OCR using pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
def process_ocr(filename):
    image = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    text = pytesseract.image_to_string(image).lower()
    return text

# Process OCR and extract data using OpenAI API
def extract_data_from_ocr(text):
    prompt = f"You're an expert summarizer. From the provided OCR text, extract only the following information: Title:(summary of what item purchased like food), Platform: (online from Amazon, Flipkart and more or offline using cash or counter or upi from where)), Date (in dd-mm-yyyy format), Time (in hh:mm am/pm format), Place/City, Total Amount (using currency symbols only). If any information is available in a different format, please convert it to the desirable format before displaying.\n{text}"
    
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        temperature=0,
        max_tokens=200
    )
    
    return response.choices[0].text.strip()

# Save invoice data to database
def save_invoice_data(invoice_data, user_id):
    connection = psycopg2.connect(**connection_config)
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO invoice_details (title, platform, transaction_time, place, total_cost, category, unique_code) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (invoice_data['title'], invoice_data['platform'], invoice_data['transaction_time'], invoice_data['place'], invoice_data['total_cost'], invoice_data['category'], user_id))
        connection.commit()
    finally:
        connection.close()

# Login logic
def login_user(email, unique_code):
    connection = psycopg2.connect(**connection_config)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id FROM user_details WHERE email = %s AND unique_code = %s"
            cursor.execute(sql, (email, unique_code))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]
                return True
            else:
                return False
    finally:
        connection.close()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        # Check if email already exists
        connection = psycopg2.connect(**connection_config)
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM public.user_details WHERE email = %s"
                cursor.execute(sql, (email,))
                existing_user = cursor.fetchone()
            
            if existing_user:
                return render_template('register.html', error='Email already exists. Please enter a new email.')
        finally:
            connection.close()
        
        unique_code = generate_unique_code()
        
        # Save user details to database
        connection = psycopg2.connect(**connection_config)
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO public.user_details(name, email, unique_code) VALUES (%s, %s, %s)"
                cursor.execute(sql, (name, email, unique_code))
            connection.commit()
        finally:
            connection.close()
        
        return render_template('register.html', unique_code=unique_code, success=True)
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        unique_code = request.form['unique_code']
        
        if login_user(email, unique_code):
            return redirect(url_for('upload_invoice'))
        else:
            return render_template('login.html', error='Invalid email or unique code')
    
    return render_template('login.html')

@app.route('/upload_invoice', methods=['GET', 'POST'])
def upload_invoice():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        uploaded_file = request.files['invoice']
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Process OCR and extract data
        ocr_text = process_ocr(filename)
        invoice_data = extract_data_from_ocr(ocr_text)
        
        # Save invoice data to database
        save_invoice_data(invoice_data, session['user_id'])
        
        return 'Invoice uploaded successfully'
    
    return render_template('upload_invoice.html')

if __name__ == '__main__':
    app.run(debug=True)

import os
import random
import string
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import cv2
import pytesseract
import psycopg2
from openai import OpenAI

app = Flask(__name__)
app.config['SECRET_KEY'] = '1223Akshat'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Database connection details
connection_config = {
    'dsn': "postgres://analyzar_db_e8ou_user:oNSbiWJurpryUxZNIjjorWwUJPq4I0e4@dpg-co7ek8cf7o1s73cm96rg-a.singapore-postgres.render.com/analyzar_db_e8ou"
}

# Initialize OpenAI client
openai_client = OpenAI(api_key="your_openai_api_key")

# Generate unique code
def generate_unique_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(10))

# Process OCR using pytesseract
def process_ocr(filename):
    image = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    text = pytesseract.image_to_string(image).lower()
    return text

# Process OCR and extract data using OpenAI API
def extract_data_from_ocr(text):
    prompt = f"You're an expert summarizer. From the provided OCR text, extract only the following information: Title:(summary of what item purchased like food), Platform: (online from Amazon, Flipkart and more or offline using cash or counter or upi from where)), Date (in dd-mm-yyyy format), Time (in hh:mm am/pm format), Place/City, Total Amount (using currency symbols only). If any information is available in a different format, please convert it to the desirable format before displaying.\n{text}"
    
    response = openai_client.completions.create(
        model="text-davinci-002",
        prompt=prompt,
        temperature=0,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    return response.choices[0].text.strip()

# Save invoice data to database
def save_invoice_data(invoice_data, user_id):
    connection = psycopg2.connect(**connection_config)
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO invoice_details (title, platform, transaction_time, place, total_cost, category, unique_code) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (invoice_data['title'], invoice_data['platform'], invoice_data['transaction_time'], invoice_data['place'], invoice_data['total_cost'], invoice_data['category'], user_id))
        connection.commit()
    finally:
        connection.close()

# Login logic
def login_user(email, unique_code):
    connection = psycopg2.connect(**connection_config)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id FROM user_details WHERE email = %s AND unique_code = %s"
            cursor.execute(sql, (email, unique_code))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]
                return True
            else:
                return False
    finally:
        connection.close()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        # Check if email already exists
        connection = psycopg2.connect(**connection_config)
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM public.user_details WHERE email = %s"
                cursor.execute(sql, (email,))
                existing_user = cursor.fetchone()
            
            if existing_user:
                return render_template('register.html', error='Email already exists. Please enter a new email.')
        finally:
            connection.close()
        
        unique_code = generate_unique_code()
        
        # Save user details to database
        connection = psycopg2.connect(**connection_config)
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO public.user_details(name, email, unique_code) VALUES (%s, %s, %s)"
                cursor.execute(sql, (name, email, unique_code))
            connection.commit()
        finally:
            connection.close()
        
        return render_template('register.html', unique_code=unique_code, success=True)
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Initialize error variable
    
    if request.method == 'POST':
        email = request.form['email']
        unique_code = request.form['unique_code']
        
        # Check if the email and unique code pair exist in the database
        connection = psycopg2.connect(**connection_config)
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM public.user_details WHERE email = %s AND unique_code = %s"
                cursor.execute(sql, (email, unique_code))
                user = cursor.fetchone()
            
            if user:
                session['user_id'] = user['id']
                return redirect(url_for('upload_invoice'))
            else:
                error = 'Invalid email or unique code.'
        finally:
            connection.close()
    
    # Pass error to the template
    return render_template('login.html', error=error)


@app.route('/upload_invoice', methods=['GET', 'POST'])
def upload_invoice():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        uploaded_files = request.files.getlist('invoice')  # Get list of uploaded files
        
        for uploaded_file in uploaded_files:
            filename = secure_filename(uploaded_file.filename)
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Process OCR and extract data
            ocr_text = process_ocr(filename)
            invoice_data = extract_data_from_ocr(ocr_text)
            
            # Save invoice data to database
            save_invoice_data(invoice_data, session['user_id'])
        
        return 'Invoices uploaded successfully'
    
    return render_template('upload_invoice.html')


if __name__ == '__main__':
    app.run(debug=True)
