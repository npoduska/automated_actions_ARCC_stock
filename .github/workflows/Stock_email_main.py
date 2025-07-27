"""This here program send email stock alerts.
Whenever the stock gets below a certain price OR is trending downward,
an alert is sent, along with a few news clips about that stock."""


import requests, smtplib, os, logging
from datetime import *

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Get environment variables
API_KEY = os.environ.get('API_KEY')
my_email = os.environ.get('MY_EMAIL')
to_email = os.environ.get('TO_EMAIL')
app_password = os.environ.get('APP_EMAIL_PASSWORD')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')

# Log environment variable status (without exposing actual values)
logging.info(f"API_KEY present: {API_KEY is not None}")
logging.info(f"MY_EMAIL present: {my_email is not None}")
logging.info(f"TO_EMAIL present: {to_email is not None}")
logging.info(f"APP_EMAIL_PASSWORD present: {app_password is not None}")
logging.info(f"NEWS_API_KEY present: {NEWS_API_KEY is not None}")

STOCK = "ARCC"
COMPANY_NAME = "Ares Capital Corporation"

logging.info("Starting stock check...")

## STEP 1: Use https://www.alphavantage.co
#Collect all the stock information
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={STOCK}&apikey={API_KEY}'
r = requests.get(url)
stock_data = r.json()

# Check if we got valid data
if 'Time Series (Daily)' not in stock_data:
    logging.error(f"Failed to get stock data. Response: {stock_data}")
    exit(1)

low_prices = []  #Initialize an array

# Iterate over the list, collecting the bits of data we really want
for date, values in stock_data['Time Series (Daily)'].items():
    low_prices.append(float(values['3. low']))
    
latest_low_price = int(low_prices[0])   #Get the most current low price from the list
formatted_low_prices = [f"${float(price):.2f}" for price in low_prices]  #Format the list of string numbers to "$12.34"

logging.info(f"The past 3 trading day lows are: {formatted_low_prices[:3]}")

# Calculate the average of the first 20 values
short_sma = sum(low_prices[:20]) / 20
logging.info(f"Short term (20 day) simple moving average: ${short_sma:.2f}")
# Calculate the average of the first 50 values
long_sma = sum(low_prices[:50]) / 50
logging.info(f"Long term (50 day) simple moving average: ${long_sma:.2f}")

#Calculate simple moving average (trending up or downward)
if short_sma > long_sma:
    logging.info("Trending Up")
    trending_condition = "Trending Upward"
else:
    logging.info("Trending Down")
    trending_condition = "Trending Downward"

def send_email(subject, body):
    """Helper function to send emails and handle errors."""
    try:
        email_message = f"Subject: {subject}\n\n{body}"
        with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as connection:
            logging.info(f"Attempting to login with {my_email}")
            connection.login(user=my_email, password=app_password)
            try:
                connection.sendmail(from_addr=my_email, to_addrs=to_email, msg=email_message)
                logging.info("Email sent successfully")
                return True
            except UnicodeEncodeError:
                logging.warning("UnicodeEncodeError encountered, encoding as ASCII")
                email_message = email_message.encode('ascii', errors='ignore')
                connection.sendmail(from_addr=my_email, to_addrs=to_email, msg=email_message)
                logging.info("Email sent successfully after encoding fix")
                return True
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        return False

if latest_low_price < 23:
    logging.info("GET NEWS!")
    
    # Send price alert email
    alert_body = f"The past 3 trading day lows are: {formatted_low_prices[:3]}. {trending_condition}"
    send_email("A new low!", alert_body)
    
    ## STEP 2: Use https://newsapi.org
    # Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 
    news_url = f'https://newsapi.org/v2/everything?q={COMPANY_NAME}&from=2025-03-01&sortBy=popularity&apiKey={NEWS_API_KEY}'

    try:
        response = requests.get(news_url)
        data = response.json()
        
        # Log the structure of the response to help debug
        logging.info(f"News API response keys: {data.keys()}")
        
        # Check if 'totalResults' exists and is greater than 0
        if 'totalResults' in data and data['totalResults'] > 0:
            max_articles = min(4, len(data['articles']))
            for i in range(0, max_articles):
                news_source = data['articles'][i]["source"]['name']
                news_title = data['articles'][i]["title"]
                news_description = data['articles'][i]["description"] if data['articles'][i]["description"] else "No description available"
                
                logging.info(f"News found: {news_source} - {news_title}")
                
                # Send news email
                news_body = f"News source: {news_source}, Title: {news_title}, Description: {news_description}"
                send_email(f"News related to {STOCK}", news_body)
        else:
            logging.info(f"No news articles found for {COMPANY_NAME}")
            send_email(f"No news for {STOCK}", f"There are no news articles found for {COMPANY_NAME}.")
    except Exception as e:
        logging.error(f"Error fetching or processing news: {str(e)}")
        send_email("Error in Stock Alert Script", f"Error fetching news: {str(e)}")

logging.info("Script completed")
