import requests
import os
import logging
import json
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

# Process stock data
low_prices = []
volume = []
for date, values in stock_data['Time Series (Daily)'].items():
    low_prices.append(float(values['3. low']))
    volume.append(float(values['5. volume']))
    
latest_low_price = (low_prices[0])
latest_volume = int(volume[0])
formatted_low_prices = [f"${(price):.2f}" for price in low_prices]

# Calculate averages
short_sma = sum(low_prices[:20]) / 20
long_sma = sum(low_prices[:50]) / 50
avg_volume = sum(volume[:50]) / 50

# Determine trend
trending_condition = "Trending Upward" if short_sma > long_sma else "Trending Downward"

# Calculate volume change
volume_change = ((latest_volume - avg_volume) / abs(avg_volume)) * 100

# Check all alert conditions
price_alert = latest_low_price < 23
trend_alert = trending_condition == "Trending Downward"
volume_alert = volume_change > 70

# If any alert condition is met, send alert
should_alert = price_alert or trend_alert or volume_alert

# Create alert message with markdown formatting for better display in GitHub
alert_message = f"## Stock Alert for {STOCK} ({COMPANY_NAME})\n\n"
alert_message += f"**Current Price:** {formatted_low_prices[0]}\n\n"
alert_message += f"**Past 3 trading day lows:** {', '.join(formatted_low_prices[:3])}\n\n"
alert_message += f"**Trend:** {trending_condition}\n\n"
alert_message += f"**Volume Change:** {volume_change:.2f}%\n\n"

# Add reason for alert if conditions are met
if should_alert:
    alert_message += "### Alert triggered because:\n\n"
    if price_alert:
        alert_message += f"- Price fell below threshold of $23.00 (current: {formatted_low_prices[0]})\n\n"
    if trend_alert:
        alert_message += f"- Stock is trending downward (20-day SMA: ${short_sma:.2f}, 50-day SMA: ${long_sma:.2f})\n\n"
    if volume_alert:
        alert_message += f"- Unusual trading volume detected ({volume_change:.2f}% above average)\n\n"
    
    # Get news articles
    news_url = f'https://newsapi.org/v2/everything?q={COMPANY_NAME}&from=2025-03-01&sortBy=popularity&apiKey={NEWS_API_KEY}'
    response = requests.get(news_url)
    data = response.json()
    
    # Add news if available
    if int(data.get('totalResults', 0)) > 0:
        alert_message += "### Recent News:\n\n"
        articles = data['articles'][:3]  # Get up to 3 articles
        for i, article in enumerate(articles, 1):
            alert_message += f"{i}. **{article['title']}**\n\n"
            alert_message += f"   Source: {article['source']['name']}\n\n"
            alert_message += f"   {article['description']}\n\n"
    
    # Set GitHub Actions output
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write(f"alert_triggered=true\n")
        # Use delimiter for multiline output (new GitHub Actions syntax)
        f.write("alert_message<<EOF\n")
        f.write(f"{alert_message}\n")
        f.write("EOF\n")
    
    print(f"::warning::{STOCK} Alert - {', '.join(condition for condition, triggered in zip(['Price', 'Trend', 'Volume'], [price_alert, trend_alert, volume_alert]) if triggered)}")
    
    # Log the alert
    logging.info("Stock alert triggered")
    logging.info(alert_message)
else:
    # Set GitHub Actions output - no alert
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write(f"alert_triggered=false\n")
        f.write("alert_message=No alert conditions met for {STOCK}\n")
    
    print(f"::notice::No alert conditions met for {STOCK}")
    
    # Log the non-alert
    logging.info("No stock alert conditions met")
