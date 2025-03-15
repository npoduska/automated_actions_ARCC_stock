"""This program sends email stock alerts.
Whenever the stock gets below a certain price OR is trending downward OR trading volume level,
an alert is sent, along with a few news clips about that stock."""

import requests, os, logging
from datetime import *

# Setup logging
logging.basicConfig(filename='.github/workflows/script.log', level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s')

API_KEY = os.environ.get('API_KEY')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')

# Stock information
STOCK = "ARCC"
COMPANY_NAME = "Ares Capital Corporation"

# Get stock data
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={STOCK}&apikey={API_KEY}'
r = requests.get(url)
stock_data = r.json()

# Process stock data (same as your original script)
low_prices = []
volume = []

for date, values in stock_data['Time Series (Daily)'].items():
    low_prices.append(float(values['3. low']))
    volume.append(float(values['5. volume']))
    
latest_low_price = int(low_prices[0])
latest_volume = int(volume[0])
formatted_low_prices = [f"${float(price):.2f}" for price in low_prices]

# Calculate averages
short_sma = sum(low_prices[:20]) / 20
long_sma = sum(low_prices[:50]) / 50
avg_volume = sum(volume[:50]) / 50

# Determine trend
trending_condition = "Trending Upward" if short_sma > long_sma else "Trending Downward"

# Calculate volume change
volume_change = ((latest_volume - avg_volume) / abs(avg_volume)) * 100

# Check alert conditions
should_alert = latest_low_price < 23 or volume_change > 70

# If alert needed, save content to file and set output variable
if should_alert:
    # Get news articles
    news_url = f'https://newsapi.org/v2/everything?q={COMPANY_NAME}&from=2025-03-01&sortBy=popularity&apiKey={NEWS_API_KEY}'
    response = requests.get(news_url)
    data = response.json()
    
    # Create email content
    with open('.github/workflows/email_content.txt', 'w') as f:
        f.write(f"Stock Alert for {STOCK} ({COMPANY_NAME})\n\n")
        f.write(f"Current Price: {formatted_low_prices[0]}\n")
        f.write(f"The past 3 trading day lows are: {', '.join(formatted_low_prices[:3])}\n")
        f.write(f"Trend: {trending_condition}\n")
        f.write(f"Volume Change: {volume_change:.2f}%\n\n")
        
        # Add news if available
        if int(data.get('totalResults', 0)) > 0:
            f.write("Recent News:\n")
            articles = data['articles'][:3]  # Get up to 3 articles
            for i, article in enumerate(articles, 1):
                f.write(f"\n{i}. {article['title']}\n")
                f.write(f"Source: {article['source']['name']}\n")
                f.write(f"{article['description']}\n")
    
    # Set output for GitHub Actions
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write("send_alert=true\n")
        logging.info("Alert condition met, email content prepared")
else:
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write("send_alert=false\n")
        logging.info("No alert conditions met")
