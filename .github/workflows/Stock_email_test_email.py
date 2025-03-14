"""
Simple script to test Zoho Mail authentication and sending emails from GitHub Actions
"""

import os
import smtplib
import sys

# Get environment variables
zoho_email = os.environ.get('ZOHO_EMAIL')
to_email = os.environ.get('TO_EMAIL')
zoho_password = os.environ.get('ZOHO_PASSWORD')

print("Starting Zoho Mail test")
print(f"Using Zoho email: {zoho_email}")
print(f"Sending to: {to_email}")

try:
    # Connect to Zoho's SMTP server
    print("Connecting to Zoho SMTP server...")
    with smtplib.SMTP("smtp.zoho.com", port=587) as connection:
        # Start TLS encryption (required for Zoho)
        connection.starttls()
        
        # Attempt to login
        print("Attempting login...")
        connection.login(user=zoho_email, password=zoho_password)
        print("Login successful!")
        
        # Create and send a test email
        email_message = 'Subject: GitHub Actions Test via Zoho\n\nThis is a test email from GitHub Actions using Zoho Mail.'
        print("Sending email...")
        connection.sendmail(from_addr=zoho_email, to_addrs=to_email, msg=email_message)
        print("Email sent successfully!")
        
except Exception as e:
    print(f"Error: {str(e)}")
    sys.exit(1)

print("Test completed successfully")
