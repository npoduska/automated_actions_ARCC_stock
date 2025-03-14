"""
Simple script to test Gmail authentication and sending emails from GitHub Actions
"""

import os
import smtplib
import sys

# Get environment variables
my_email = os.environ.get('MY_EMAIL')
to_email = os.environ.get('TO_EMAIL')
app_password = os.environ.get('APP_EMAIL_PASSWORD')

print("Starting email test")
print(f"Using email: {my_email[:3]}...{my_email[-10:]}")
print(f"Sending to: {to_email[:3]}...{to_email[-10:]}")

try:
    # Connect to Gmail's SMTP server
    print("Connecting to SMTP server...")
    with smtplib.SMTP_SSL('smtp.gmail.com', port=465) as connection:
        # Attempt to login
        print("Attempting login...")
        connection.login(user=my_email, password=app_password)
        print("Login successful!")
        
        # Create and send a test email
        email_message = 'Subject: GitHub Actions Test\n\nThis is a test email from GitHub Actions.'
        print("Sending email...")
        connection.sendmail(from_addr=my_email, to_addrs=to_email, msg=email_message)
        print("Email sent successfully!")
        
except Exception as e:
    print(f"Error: {str(e)}")
    sys.exit(1)

print("Test completed successfully")