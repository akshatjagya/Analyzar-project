import smtplib
from flask import Flask, render_template, request, redirect, url_for, session
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Gmail SMTP settings
smtp_server = 'smtp.gmail.com'
smtp_port = 587  # TLS encryption
smtp_username = 'analyzar.autoinvoice@gmail.com'
smtp_password = 'yyhsyyhs@1'

@app.route('/send_email')
def send_email():
    # Create a MIME message
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = 'akshatjagya2003@gmail.com'
    msg['Subject'] = 'Test Email'

    # Add email body
    body = 'This is a test email sent from Flask.'
    msg.attach(MIMEText(body, 'plain'))

    # Connect to Gmail SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        # Start TLS encryption
        server.starttls()
        # Login to Gmail SMTP server
        server.login(smtp_username, smtp_password)
        # Send email
        server.send_message(msg)

    return 'Email sent successfully'

if __name__ == '__main__':
    app.run(debug=True)
