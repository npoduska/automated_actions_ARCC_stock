"""This program sends email stock alerts.
Whenever the stock gets below a certain price OR is trending downward OR trading volume level,
an alert is sent, along with a few news clips about that stock."""

import requests, smtplib, os, logging
# from config import MY_EMAIL, TO_EMAIL, APP_EMAIL_PASSWORD, API_KEY, NEWS_API_KEY #Get your own API Keys!
from datetime import *

logging.basicConfig(filename='.github/workflows/script.log', level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s')

API_KEY= os.environ.get('API_KEY')
my_email = os.environ.get('MY_EMAIL')
to_email = os.environ.get('TO_EMAIL')
app_password= os.environ.get('APP_EMAIL_PASSWORD')
NEWS_API_KEY= os.environ.get('NEWS_API_KEY')
# zoho_email = os.environ.get('ZOHO_EMAIL')
# my_email = MY_EMAIL
# to_email = TO_EMAIL
# app_password= APP_EMAIL_PASSWORD

#Verify that environment variables are being loaded
print(f"Email: {my_email}")
print(f"Password: {(app_password) if app_password else 'Not set'}")

print("check your email now.")
# Then use logging instead of print throughout your script
logging.info("Starting stock check...")

STOCK = "ARCC"
COMPANY_NAME = "Ares Capital Corporation"

## STEP 1: Use https://www.alphavantage.co

#Collect all the stock information
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={STOCK}&apikey={API_KEY}'
r = requests.get(url)
stock_data = r.json()
# print((stock_data))

low_prices =[]  #Initialize the low price array
volume = []  #Initialize the trading volume array

# Iterate over the list, collecting the bits of data we really want
for date, values in stock_data['Time Series (Daily)'].items():
    # high_values.append(float(values['2. high']))
    low_prices.append(float(values['3. low']))
    volume.append(float(values['5. volume']))
    
latest_low_price = int(low_prices[0])   #Get the most current low price from the list
latest_volume = int(volume[0])   #Get the most current trading volume from the list

formatted_low_prices = [f"${float(price):.2f}" for price in low_prices]  #Format the list of string numbers to "$12.34"
# print((latest_low_price))
# Now high_values and low_values arrays contain all 'high' and 'low' values
# print("High values:", high_values)
# print("Low prices:", low_prices)
# print(low_prices)
print(f"The past 3 trading day lows are: {formatted_low_prices[:3]}")
logging.info(f"The past 3 trading day lows are: {formatted_low_prices[:3]}")
print(f"The past 3 trading day volumes are: {volume[:3]}")
logging.info(f"The past 3 trading day volumes are: {volume[:3]}")

# Calculate the average of the first 20 values
short_sma = sum(low_prices[:20]) / 20
print(f" Short term (20 day) simple moving average: ${short_sma:.2f}")
# Calculate the average of the first 50 values
long_sma = sum(low_prices[:50]) / 50
print(f" Long term (50 day) simple moving average: ${long_sma:.2f}")
# Calculate the average of the first 50 values
avg_volume = sum(volume[:50]) / 50
print(f" Long term (50 day) average trading volume is: {avg_volume}")

#Calculate simple moving average (trending up or downward)
if short_sma > long_sma:
    print("Trending Up")
    trending_condition = "Trending Upward"
else:
    print("Trending Down")
    trending_condition = "Trending Downward"

#Calculate if the latest trading volume is 75% greater then the average from the past 50 trading days.
volume_change = ((latest_volume - avg_volume) / abs(avg_volume)) * 100
print(f"% Volume Change: {volume_change:.2f}%")

if latest_low_price < 23 or volume_change > 70:
    print("GETTING THE NEWS!")
    logging.info("GETTING THE NEWS!")
    email_message= f"Subject: A new low or high trading volume!\n\nThe past 3 trading day lows are: {formatted_low_prices[:3]}.\n\n {trending_condition} \n\n Trading Volume Change: {volume_change:.2f}% "

    # Connect to Zoho's SMTP server using SSL
    print("Connecting to Zoho SMTP server via SSL...")

    try:
        connection = smtplib.SMTP_SSL("smtp.zoho.com", port=465, timeout=30)
        print("Connected to SMTP server")
        connection.login(user=my_email, password=app_password)
        print("Login successful")
        
        try:
            connection.sendmail(from_addr=my_email, to_addrs=to_email, msg=email_message)
            print("Basic email sent successfully")
        except UnicodeEncodeError:
            email_message = email_message.encode('ascii', errors='ignore')
            connection.sendmail(from_addr=my_email, to_addrs=to_email, msg=email_message)
            print("Basic email sent successfully after encoding fix")
        except Exception as e:
            print(f"Error sending basic email: {type(e).__name__}: {e}")
            logging.error(f"Error sending basic email: {type(e).__name__}: {e}")
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"Authentication error: {e}")
        logging.error(f"SMTP Authentication Error: {e}")
    except Exception as e:
        print(f"Connection error: {type(e).__name__}: {e}")
        logging.error(f"SMTP Connection Error: {type(e).__name__}: {e}")
    
    print("check your email now.")
    logging.info("email should have been sent now")
    
    ## STEP 2: Use https://newsapi.org
    # Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

    news_url = f'https://newsapi.org/v2/everything?q={COMPANY_NAME}&from=2025-03-01&sortBy=popularity&apiKey={NEWS_API_KEY}'

    response = requests.get(news_url)
    data = response.json()  # Call the method
    
    # Initialize an empty list to store articles
    articles_list = []

    if 0 < int(data['totalResults']):
        # Determine how many articles to process
        max_articles = min(4, int(data['totalResults']))
        
        # Collect all articles first
        for i in range(0, max_articles):
            news_source = data['articles'][i]["source"]['name']
            news_title = data['articles'][i]["title"]
            news_description = data['articles'][i]["description"]
            
            # Store article info in a dictionary
            article = {
                'source': news_source,
                'title': news_title,
                'description': news_description
            }
            
            articles_list.append(article)
        
        # Create a formatted email with all articles
        email_subject = f"News Update for {COMPANY_NAME}"
        
        # Build the email body with HTML formatting
        email_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333366; }}
                h2 {{ color: #666699; margin-top: 20px; }}
                .article {{ margin-bottom: 20px; padding: 10px; border-bottom: 1px solid #cccccc; }}
                .source {{ color: #666666; font-style: italic; }}
                .description {{ margin-top: 5px; }}
            </style>
        </head>
        <body>
            <h1>News Updates for {COMPANY_NAME}</h1>
            <p>Here are the top {len(articles_list)} news articles about {COMPANY_NAME}:</p>
        """
        
        # Add each article to the email body
        for i, article in enumerate(articles_list, 1):
            email_body += f"""
            <div class="article">
                <h2>{i}. {article['title']}</h2>
                <p class="source">Source: {article['source']}</p>
                <p class="description">{article['description']}</p>
            </div>
            """
        
        # Close the HTML
        email_body += """
        </body>
        </html>
        """
        
        # Create the email message with both plain text and HTML versions
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        
        message = MIMEMultipart("alternative")
        message["Subject"] = email_subject
        message["From"] = my_email
        message["To"] = to_email
        
        # Create plain text version as fallback
        plain_text = f"News Updates for {COMPANY_NAME}\n\n"
        for i, article in enumerate(articles_list, 1):
            plain_text += f"{i}. {article['title']}\n"
            plain_text += f"Source: {article['source']}\n"
            plain_text += f"Description: {article['description']}\n\n"
        
        # Attach both versions to the email
        message.attach(MIMEText(plain_text, "plain"))
        message.attach(MIMEText(email_body, "html"))
        
        # Send the email
        try:
            with smtplib.SMTP_SSL("smtp.zoho.com", port=465, timeout=30) as connection:
                connection.login(user=my_email, password=app_password)
                connection.send_message(message)
                print("HTML email sent successfully")
        except smtplib.SMTPAuthenticationError as e:
            print(f"Authentication error for HTML email: {e}")
            logging.error(f"SMTP Authentication Error for HTML email: {e}")
        except Exception as e:
            print(f"Connection error for HTML email: {type(e).__name__}: {e}")
            logging.error(f"SMTP Connection Error for HTML email: {type(e).__name__}: {e}")
