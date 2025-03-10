"""This program sends email stock alerts.
Whenever the stock gets below a certain price OR is trending downward,
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

print("check your email now.")
# Then use logging instead of print throughout your script
logging.info("Starting stock check...")

STOCK1 = "ARCC"
STOCK2 = "ET"
STOCK3 = "MPW"
STOCK4 = "EPD"
COMPANY_NAME1 = "Ares Capital Corporation"
COMPANY_NAME2 = "Energy Transfer LP"
COMPANY_NAME3 = "Medical Properties Trust"
COMPANY_NAME4 = "Enterprise Products Partners LP"

#########################STOCK1#####################################################
STOCK = STOCK1
COMPANY_NAME = COMPANY_NAME1

## STEP 1: Use https://www.alphavantage.co

#Collect all the stock information
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={STOCK}&apikey={API_KEY}'
r = requests.get(url)
stock_data = r.json()
# print((stock_data))

low_prices =[]  #Initialize an array

# Iterate over the list, collecting the bits of data we really want
for date, values in stock_data['Time Series (Daily)'].items():
    # high_values.append(float(values['2. high']))
    low_prices.append(float(values['3. low']))
    
latest_low_price = int(low_prices[0])   #Get the most current low price from the list
formatted_low_prices = [f"${float(price):.2f}" for price in low_prices]  #Format the list of string numbers to "$12.34"
# print((latest_low_price))
# Now high_values and low_values arrays contain all 'high' and 'low' values
# print("High values:", high_values)
# print("Low prices:", low_prices)
# print(low_prices)
print(f"The past 3 trading day lows are: {formatted_low_prices[:3]}")
logging.info(f"The past 3 trading day lows for {STOCK} are: {formatted_low_prices[:3]}")

# Calculate the average of the first 20 values
short_sma = sum(low_prices[:20]) / 20
print (f" Short term (20 day) simple moving average: ${short_sma:.2f}")
# Calculate the average of the first 50 values
long_sma = sum(low_prices[:50]) / 50
print (f" Long term (50 day) simple moving average: ${long_sma:.2f}")

#Calculate simple moving average (trending up or downward)
if short_sma > long_sma:
    print("Trending Up")
    trending_condition = "Trending Upward"
else:
    print("Trending Down")
    trending_condition = "Trending Downward"

if latest_low_price < 21:
    print("GET NEWS!")
    logging.info(f"GETTING THE NEWS FOR {STOCK}!")
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(
    # body= f"A new low! The past 3 trading day lows are: {formatted_low_prices[:3]}. {trending_condition}",
    # from_=f"{FROM_NUMBER}",
    # to=f"{TO_NUMBER}",)
    email_message= f"Subject: A new low for {STOCK}!\n\nThe past 3 trading day lows are: {formatted_low_prices[:3]}. {trending_condition}"

    with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as connection:
        connection.login(user= my_email  , password= app_password)
        try:
            connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
        except UnicodeEncodeError:
            email_message = email_message.encode('ascii',errors='ignore')
            connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
    print("check your email now.")
    logging.info("email should have been sent now")
    
## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

    news_url = f'https://newsapi.org/v2/everything?q={COMPANY_NAME}&from=2024-09-13&sortBy=popularity&apiKey={NEWS_API_KEY}'

    response = requests.get(news_url)
    data = response.json()  # Call the method
    # print(data['totalResults']) 
    if 0 < int(data['totalResults']): 
        if int(data['totalResults']) >5:
            max_articles = 4
        for i in range (0, max_articles):
            print(data['articles'][i]["source"]['name']) #Get where the article came from.
            print(data['articles'][i]["title"])    # This will print the parsed JSON data, particularly the title portion
            print(data['articles'][i]["description"])    # This will print the parsed JSON data, particularly the description portion
            # print(data) 
            #Send the news out via Twilio SMS
            news_source = (data['articles'][i]["source"]['name']) #Get where the article came from.
            news_title = (data['articles'][i]["title"])    # This will print the parsed JSON data, particularly the title portion
            news_description = (data['articles'][i]["description"])   
            
            # client = Client(account_sid, auth_token)
            # message = client.messages.create(
            # body= f"News source: {news_source}, Title: {news_title}, Desciption: {news_description}",
            # from_=f"{FROM_NUMBER}",
            # to=f"{TO_NUMBER}",)
            email_message= f"Subject: News related to {STOCK} \n\nNews source: {news_source}, Title: {news_title}, Desciption: {news_description}"

            with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as connection:
                connection.login(user= my_email  , password= app_password)
                try:
                    connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
                except UnicodeEncodeError:
                    email_message = email_message.encode('ascii',errors='ignore')
                    connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
            print("check your email now.")
            logging.info("email should have been recieved now")
    else:
        print(f"There are no news articles found for {COMPANY_NAME}.")  
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        # body= f"There are no news articles found for {COMPANY_NAME}.",
        # from_=f"{FROM_NUMBER}",
        # to=f"{TO_NUMBER}",) 
        email_message= f"Subject: No news for {STOCK}\n\nThere are no news articles found for {COMPANY_NAME}."

        with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as connection:
            connection.login(user= my_email  , password= app_password)
            try:
                connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
            except UnicodeEncodeError:
                email_message = email_message.encode('ascii',errors='ignore')
                connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
        print("check your email now.")
    
    #########################STOCK2#####################################################
STOCK = STOCK2
COMPANY_NAME = COMPANY_NAME2

## STEP 1: Use https://www.alphavantage.co

#Collect all the stock information
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={STOCK}&apikey={API_KEY}'
r = requests.get(url)
stock_data = r.json()
# print((stock_data))

low_prices =[]  #Initialize an array

# Iterate over the list, collecting the bits of data we really want
for date, values in stock_data['Time Series (Daily)'].items():
    # high_values.append(float(values['2. high']))
    low_prices.append(float(values['3. low']))
    
latest_low_price = int(low_prices[0])   #Get the most current low price from the list
formatted_low_prices = [f"${float(price):.2f}" for price in low_prices]  #Format the list of string numbers to "$12.34"
# print((latest_low_price))
# Now high_values and low_values arrays contain all 'high' and 'low' values
# print("High values:", high_values)
# print("Low prices:", low_prices)
# print(low_prices)
print(f"The past 3 trading day lows are: {formatted_low_prices[:3]}")
logging.info(f"The past 3 trading day lows for {STOCK} are: {formatted_low_prices[:3]}")

# Calculate the average of the first 20 values
short_sma = sum(low_prices[:20]) / 20
print (f" Short term (20 day) simple moving average: ${short_sma:.2f}")
# Calculate the average of the first 50 values
long_sma = sum(low_prices[:50]) / 50
print (f" Long term (50 day) simple moving average: ${long_sma:.2f}")

#Calculate simple moving average (trending up or downward)
if short_sma > long_sma:
    print("Trending Up")
    trending_condition = "Trending Upward"
else:
    print("Trending Down")
    trending_condition = "Trending Downward"

if latest_low_price < 16:
    print("GET NEWS!")
    logging.info(f"GETTING THE NEWS FOR {STOCK}!")
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(
    # body= f"A new low! The past 3 trading day lows are: {formatted_low_prices[:3]}. {trending_condition}",
    # from_=f"{FROM_NUMBER}",
    # to=f"{TO_NUMBER}",)
    email_message= f"Subject: A new low for {STOCK}!\n\nThe past 3 trading day lows are: {formatted_low_prices[:3]}. {trending_condition}"

    with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as connection:
        connection.login(user= my_email  , password= app_password)
        try:
            connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
        except UnicodeEncodeError:
            email_message = email_message.encode('ascii',errors='ignore')
            connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
    print("check your email now.")
    logging.info("email should have been sent now")
    
## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

    news_url = f'https://newsapi.org/v2/everything?q={COMPANY_NAME}&from=2024-09-13&sortBy=popularity&apiKey={NEWS_API_KEY}'

    response = requests.get(news_url)
    data = response.json()  # Call the method
    # print(data['totalResults']) 
    if 0 < int(data['totalResults']): 
        if int(data['totalResults']) >5:
            max_articles = 4
        for i in range (0, max_articles):
            print(data['articles'][i]["source"]['name']) #Get where the article came from.
            print(data['articles'][i]["title"])    # This will print the parsed JSON data, particularly the title portion
            print(data['articles'][i]["description"])    # This will print the parsed JSON data, particularly the description portion
            # print(data) 
            #Send the news out via Twilio SMS
            news_source = (data['articles'][i]["source"]['name']) #Get where the article came from.
            news_title = (data['articles'][i]["title"])    # This will print the parsed JSON data, particularly the title portion
            news_description = (data['articles'][i]["description"])   
            
            # client = Client(account_sid, auth_token)
            # message = client.messages.create(
            # body= f"News source: {news_source}, Title: {news_title}, Desciption: {news_description}",
            # from_=f"{FROM_NUMBER}",
            # to=f"{TO_NUMBER}",)
            email_message= f"Subject: News related to {STOCK} \n\nNews source: {news_source}, Title: {news_title}, Desciption: {news_description}"

            with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as connection:
                connection.login(user= my_email  , password= app_password)
                try:
                    connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
                except UnicodeEncodeError:
                    email_message = email_message.encode('ascii',errors='ignore')
                    connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
            print("check your email now.")
            logging.info("email should have been recieved now")
    else:
        print(f"There are no news articles found for {COMPANY_NAME}.")  
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        # body= f"There are no news articles found for {COMPANY_NAME}.",
        # from_=f"{FROM_NUMBER}",
        # to=f"{TO_NUMBER}",) 
        email_message= f"Subject: No news for {STOCK}\n\nThere are no news articles found for {COMPANY_NAME}."

        with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as connection:
            connection.login(user= my_email  , password= app_password)
            try:
                connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
            except UnicodeEncodeError:
                email_message = email_message.encode('ascii',errors='ignore')
                connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
        print("check your email now.")
        
    #########################STOCK3#####################################################
STOCK = STOCK3
COMPANY_NAME = COMPANY_NAME3

## STEP 1: Use https://www.alphavantage.co

#Collect all the stock information
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={STOCK}&apikey={API_KEY}'
r = requests.get(url)
stock_data = r.json()
# print((stock_data))

low_prices =[]  #Initialize an array

# Iterate over the list, collecting the bits of data we really want
for date, values in stock_data['Time Series (Daily)'].items():
    # high_values.append(float(values['2. high']))
    low_prices.append(float(values['3. low']))
    
latest_low_price = int(low_prices[0])   #Get the most current low price from the list
formatted_low_prices = [f"${float(price):.2f}" for price in low_prices]  #Format the list of string numbers to "$12.34"
# print((latest_low_price))
# Now high_values and low_values arrays contain all 'high' and 'low' values
# print("High values:", high_values)
# print("Low prices:", low_prices)
# print(low_prices)
print(f"The past 3 trading day lows are: {formatted_low_prices[:3]}")
logging.info(f"The past 3 trading day lows for {STOCK} are: {formatted_low_prices[:3]}")

# Calculate the average of the first 20 values
short_sma = sum(low_prices[:20]) / 20
print (f" Short term (20 day) simple moving average: ${short_sma:.2f}")
# Calculate the average of the first 50 values
long_sma = sum(low_prices[:50]) / 50
print (f" Long term (50 day) simple moving average: ${long_sma:.2f}")

#Calculate simple moving average (trending up or downward)
if short_sma > long_sma:
    print("Trending Up")
    trending_condition = "Trending Upward"
else:
    print("Trending Down")
    trending_condition = "Trending Downward"

if latest_low_price < 5.70:
    print("GET NEWS!")
    logging.info(f"GETTING THE NEWS FOR {STOCK}!")
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(
    # body= f"A new low! The past 3 trading day lows are: {formatted_low_prices[:3]}. {trending_condition}",
    # from_=f"{FROM_NUMBER}",
    # to=f"{TO_NUMBER}",)
    email_message= f"Subject: A new low for {STOCK}!\n\nThe past 3 trading day lows are: {formatted_low_prices[:3]}. {trending_condition}"

    with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as connection:
        connection.login(user= my_email  , password= app_password)
        try:
            connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
        except UnicodeEncodeError:
            email_message = email_message.encode('ascii',errors='ignore')
            connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
    print("check your email now.")
    logging.info("email should have been sent now")
    
## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

    news_url = f'https://newsapi.org/v2/everything?q={COMPANY_NAME}&from=2024-09-13&sortBy=popularity&apiKey={NEWS_API_KEY}'

    response = requests.get(news_url)
    data = response.json()  # Call the method
    # print(data['totalResults']) 
    if 0 < int(data['totalResults']): 
        if int(data['totalResults']) >5:
            max_articles = 4
        for i in range (0, max_articles):
            print(data['articles'][i]["source"]['name']) #Get where the article came from.
            print(data['articles'][i]["title"])    # This will print the parsed JSON data, particularly the title portion
            print(data['articles'][i]["description"])    # This will print the parsed JSON data, particularly the description portion
            # print(data) 
            #Send the news out via Twilio SMS
            news_source = (data['articles'][i]["source"]['name']) #Get where the article came from.
            news_title = (data['articles'][i]["title"])    # This will print the parsed JSON data, particularly the title portion
            news_description = (data['articles'][i]["description"])   
            
            # client = Client(account_sid, auth_token)
            # message = client.messages.create(
            # body= f"News source: {news_source}, Title: {news_title}, Desciption: {news_description}",
            # from_=f"{FROM_NUMBER}",
            # to=f"{TO_NUMBER}",)
            email_message= f"Subject: News related to {STOCK} \n\nNews source: {news_source}, Title: {news_title}, Desciption: {news_description}"

            with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as connection:
                connection.login(user= my_email  , password= app_password)
                try:
                    connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
                except UnicodeEncodeError:
                    email_message = email_message.encode('ascii',errors='ignore')
                    connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
            print("check your email now.")
            logging.info("email should have been recieved now")
    else:
        print(f"There are no news articles found for {COMPANY_NAME}.")  
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        # body= f"There are no news articles found for {COMPANY_NAME}.",
        # from_=f"{FROM_NUMBER}",
        # to=f"{TO_NUMBER}",) 
        email_message= f"Subject: No news for {STOCK}\n\nThere are no news articles found for {COMPANY_NAME}."

        with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as connection:
            connection.login(user= my_email  , password= app_password)
            try:
                connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
            except UnicodeEncodeError:
                email_message = email_message.encode('ascii',errors='ignore')
                connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
        print("check your email now.")
        
    #########################STOCK4#####################################################
STOCK = STOCK4
COMPANY_NAME = COMPANY_NAME4

## STEP 1: Use https://www.alphavantage.co

#Collect all the stock information
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={STOCK}&apikey={API_KEY}'
r = requests.get(url)
stock_data = r.json()
# print((stock_data))

low_prices =[]  #Initialize an array

# Iterate over the list, collecting the bits of data we really want
for date, values in stock_data['Time Series (Daily)'].items():
    # high_values.append(float(values['2. high']))
    low_prices.append(float(values['3. low']))
    
latest_low_price = int(low_prices[0])   #Get the most current low price from the list
formatted_low_prices = [f"${float(price):.2f}" for price in low_prices]  #Format the list of string numbers to "$12.34"
# print((latest_low_price))
# Now high_values and low_values arrays contain all 'high' and 'low' values
# print("High values:", high_values)
# print("Low prices:", low_prices)
# print(low_prices)
print(f"The past 3 trading day lows are: {formatted_low_prices[:3]}")
logging.info(f"The past 3 trading day lows for {STOCK} are: {formatted_low_prices[:3]}")

# Calculate the average of the first 20 values
short_sma = sum(low_prices[:20]) / 20
print (f" Short term (20 day) simple moving average: ${short_sma:.2f}")
# Calculate the average of the first 50 values
long_sma = sum(low_prices[:50]) / 50
print (f" Long term (50 day) simple moving average: ${long_sma:.2f}")

#Calculate simple moving average (trending up or downward)
if short_sma > long_sma:
    print("Trending Up")
    trending_condition = "Trending Upward"
else:
    print("Trending Down")
    trending_condition = "Trending Downward"

if latest_low_price < 33:
    print("GET NEWS!")
    logging.info(f"GETTING THE NEWS FOR {STOCK}!")
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(
    # body= f"A new low! The past 3 trading day lows are: {formatted_low_prices[:3]}. {trending_condition}",
    # from_=f"{FROM_NUMBER}",
    # to=f"{TO_NUMBER}",)
    email_message= f"Subject: A new low for {STOCK}!\n\nThe past 3 trading day lows are: {formatted_low_prices[:3]}. {trending_condition}"

    with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as connection:
        connection.login(user= my_email  , password= app_password)
        try:
            connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
        except UnicodeEncodeError:
            email_message = email_message.encode('ascii',errors='ignore')
            connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
    print("check your email now.")
    logging.info("email should have been sent now")
    
## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

    news_url = f'https://newsapi.org/v2/everything?q={COMPANY_NAME}&from=2024-09-13&sortBy=popularity&apiKey={NEWS_API_KEY}'

    response = requests.get(news_url)
    data = response.json()  # Call the method
    # print(data['totalResults']) 
    if 0 < int(data['totalResults']): 
        if int(data['totalResults']) >5:
            max_articles = 4
        for i in range (0, max_articles):
            print(data['articles'][i]["source"]['name']) #Get where the article came from.
            print(data['articles'][i]["title"])    # This will print the parsed JSON data, particularly the title portion
            print(data['articles'][i]["description"])    # This will print the parsed JSON data, particularly the description portion
            # print(data) 
            #Send the news out via Twilio SMS
            news_source = (data['articles'][i]["source"]['name']) #Get where the article came from.
            news_title = (data['articles'][i]["title"])    # This will print the parsed JSON data, particularly the title portion
            news_description = (data['articles'][i]["description"])   
            
            # client = Client(account_sid, auth_token)
            # message = client.messages.create(
            # body= f"News source: {news_source}, Title: {news_title}, Desciption: {news_description}",
            # from_=f"{FROM_NUMBER}",
            # to=f"{TO_NUMBER}",)
            email_message= f"Subject: News related to {STOCK} \n\nNews source: {news_source}, Title: {news_title}, Desciption: {news_description}"

            with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as connection:
                connection.login(user= my_email  , password= app_password)
                try:
                    connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
                except UnicodeEncodeError:
                    email_message = email_message.encode('ascii',errors='ignore')
                    connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
            print("check your email now.")
            logging.info("email should have been recieved now")
    else:
        print(f"There are no news articles found for {COMPANY_NAME}.")  
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        # body= f"There are no news articles found for {COMPANY_NAME}.",
        # from_=f"{FROM_NUMBER}",
        # to=f"{TO_NUMBER}",) 
        email_message= f"Subject: No news for {STOCK}\n\nThere are no news articles found for {COMPANY_NAME}."

        with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as connection:
            connection.login(user= my_email  , password= app_password)
            try:
                connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
            except UnicodeEncodeError:
                email_message = email_message.encode('ascii',errors='ignore')
                connection.sendmail(from_addr= my_email, to_addrs= to_email, msg= email_message)
        print("check your email now.")
        
        ##################################################################
        
        logging.info("no errors should have occured with this code if it reaches this message")
