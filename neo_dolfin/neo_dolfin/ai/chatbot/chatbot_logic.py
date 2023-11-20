# chatbot_logic.py
import os
import random
import json
import pickle
import numpy as np
import nltk
import speech_recognition as sr
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import sqlite3
from ai.chatbot.query_bankdata import *

# Establish a new SQLite database connection
conn = sqlite3.connect('transactions_ut.db')

# Initialize a variable to store the last bot reply
last_bot_reply = ""

# Initialize counts and list to store negative conversations
positive_count = 0
negative_count = 0
neutral_count = 0
total_count = 0
negative_conversations = []

# Get the current directory where the script is located
current_directory = os.path.dirname(__file__)

# Combine the current directory with the filename 'intents.json'
intents_file_path = os.path.join(current_directory, 'intents.json')
words_file_path = os.path.join(current_directory, 'words.pkl')
labels_file_path = os.path.join(current_directory, 'labels.pkl')
model_file_path = os.path.join(current_directory, 'chatbotmodel.h5')

# load intents and saved model output files
lemmatizer = WordNetLemmatizer()
intents = json.loads(open(intents_file_path).read())
words = pickle.load(open(words_file_path, 'rb'))
labels = pickle.load(open(labels_file_path, 'rb'))
model = load_model(model_file_path)

# separate input words from input sentence
def clean_up_sentences(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

# determine if input words in saved model words list
def bagw(sentence):
    sentence_words = clean_up_sentences(sentence)
    bag = [0]*len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

# predict label of sentence based on input words
def predict_class(sentence):
    bow = bagw(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [{'intent': labels[i], 'probability': str(res[i])}
               for i in range(len(res)) if res[i] > ERROR_THRESHOLD]
    results.sort(key=lambda x: x['probability'], reverse=True)
    return results

# Capture the user's speech input
def listen_to_user():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
            voice_input = r.recognize_google(audio)
            print("You said: {}".format(voice_input))
            return voice_input
        except sr.WaitTimeoutError:
            print("No command received in 10 seconds.")
            return ""
        except sr.UnknownValueError:
            print("Sorry, I didn't get that. Could you say it again?")
            return listen_to_user()
        except sr.RequestError:
            print("Sorry, my speech service is down. Please try again later.")
            return ""

# Determine sentiment of user's reply
def determine_sentiment(message, last_bot_reply):
    global positive_count, negative_count, neutral_count, total_count, negative_conversations
    analyzer = SentimentIntensityAnalyzer()
    sentiment = "neutral"
    
    sentiment_scores = analyzer.polarity_scores(message)
    compound_score = sentiment_scores["compound"]
    
    if compound_score >= 0.05:
        positive_count += 1
        sentiment = 'positive'
    elif compound_score <= -0.05:
        negative_count += 1
        sentiment = 'negative'
        negative_conversation = f"Bot: {last_bot_reply}\nYou: {message}"
        negative_conversations.append(negative_conversation)
    else:
        neutral_count += 1
    
    return sentiment

def process_sentiment(message):
    global total_count, last_bot_reply
    total_count += 1
    sentiment = determine_sentiment(message, last_bot_reply)
    # print(f"Sentiment: {sentiment}")

    # if total_count > 0:
    #     print(f"Positive: {(positive_count/total_count)*100}%")
    #     print(f"Negative: {(negative_count/total_count)*100}%")
    #     print(f"Neutral: {(neutral_count/total_count)*100}%")

    if sentiment == 'negative' and (negative_count/total_count)*100 >= 50:
        # print("Storing negative conversation for review.")
        negative_conversations.append({
            'User': message,
            'Bot': last_bot_reply
        })
    
        with open('negative_conversations.txt', 'a') as f:
            f.write(f"Bot: {last_bot_reply}\n")
            f.write(f"User: {message}\n")
            f.write("---\n")

def extract_month_year(message):

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_dict = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                  "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    month_list = []
    year_list = []

    # Match abbreviated and full month names
    month_matches = re.findall(
        r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b', message, re.IGNORECASE)
    for match in month_matches:
        abbreviated_month = match[:3].capitalize()
        month_list.append(month_dict[abbreviated_month])

    # Match years
    year_matches = re.findall(r'\b\d{4}\b', message)
    year_list = [int(year) for year in year_matches]
    return month_list, year_list

# print random response from appropriate responses for label

def get_response(intents_list, intents_json, message):
    global last_bot_ans
    conn = sqlite3.connect('transactions_ut.db')
    tag = intents_list[0]['intent']
    probability = float(intents_list[0]['probability'])
    list_of_intents = intents_json['intents']
    result = ""

    if probability < 0.2:
        result = "I'm sorry, but I'm not sure how to help with that. Could you please provide more information?"
    else:
        for i in list_of_intents:
            if i['tag'] == tag:
                if tag == "check_balance":
                    months, years = extract_month_year(message)
                    if len(months) == 1 and len(years) == 1:
                        month = months[0]
                        year = years[0]
                        balance = get_last_balance_for_month_year(
                            conn, month, year)
                        if balance:
                            result = f"Your balance for {month} {year} was {balance}."
                        else:
                            result = "Data not found for the specified month and year."
                    else:
                        result = "Couldn't extract a single month and year from your message."

                elif tag == "check_spending" or tag == "check_income":
                    month_list, year_list = extract_month_year(message)
                    # if len(month_list) == 2 and len(year_list) == 2:

                    #     plot_total_amount_for_range(

                    #         conn, 'debit' if tag == "check_spending" else 'credit', month_list[0], year_list[0], month_list[1], year_list[1])

                    #     result = "Here's the data you requested."
                    if len(month_list) == 1 and len(year_list) == 1:
                        amount, final_balance = get_total_amount_for_month_year(
                            conn, 'debit' if tag == "check_spending" else 'credit', month_list[0], year_list[0])
                        if amount:
                            result = f"Your {'spending' if tag == 'check_spending' else 'income'} for {month_list[0]} {year_list[0]} was {amount} and your balance at the end of the month was {final_balance}."
                        else:
                            result = "Data not found for the specified month and year."

                    elif len(month_list) == 0 and len(year_list) == 1:
                        plot_total_amount_for_year(
                            conn, 'debit' if tag == "check_spending" else 'credit', year_list[0])
                        result = "Here's the data you requested."
                    else:
                        result = "Couldn't extract the required month and year information from your message."

                elif tag == "highest_spending":
                    months, years = extract_month_year(message)
                    if len(months) == 1 and len(years) == 1:
                        month = months[0]
                        year = years[0]
                        highest_spending = get_highest_spending_last_period(
                            conn, 'month', month, year)
                        if highest_spending:
                            result = highest_spending
                        else:
                            result = "Data not found for the specified month and year."
                    else:
                        result = "Couldn't extract a single month and year from your message."
                else:
                    result = random.choice(i['responses'])
                break
 
    last_bot_ans = result
    return result

# Define a function to initialize and run the chatbot logic
# def initialize_chatbot_logic():
#     global last_bot_reply, positive_count, negative_count, neutral_count, total_count

#     # Reset chatbot variables
#     last_bot_reply = ""
#     positive_count = 0
#     negative_count = 0
#     neutral_count = 0
#     total_count = 0

    # Create an infinite loop that prompts for input
    # print("Chatbot live. Say or type 'end' to stop the conversation.")
    # while True:
    #     message = chat_input_method()
    #     if message.lower() == "end":
    #         print("Bot: Goodbye! Have a nice day!")
    #         break
    #     elif message != "":
    #         ints = predict_class(message)
    #         res = get_response(ints, intents)

    #         sentiment = determine_sentiment(message)
    #         print(f"Sentiment: {sentiment}")
    #         # Calculate sentiment percentages
    #         if total_count > 0:
    #             print(f"Positive: {(positive_count/total_count)*100}%")
    #             print(f"Negative: {(negative_count/total_count)*100}%")
    #             print(f"Neutral: {(neutral_count/total_count)*100}%")
            
    #         if sentiment == 'negative' and (negative_count/total_count)*100 >= 50:
    #             print("Storing negative conversation for review.")
    #             with open('negative_conversations.txt', 'a') as f:
    #                 f.write(f"Bot: {last_bot_reply}\n")
    #                 f.write(f"User: {message}\n")
    #                 f.write("---\n")

    #         # Overwrite the last_bot_reply with the current response of the bot
    #         last_bot_reply = res

    #         if res.startswith("I'm sorry"):
    #             print("Bot:", res)
    #         else:
    #             print("Bot:", res)

# Determine user input method
#def chat_input_method():
#    print("How would you like to communicate with the bot?")
#    print("1. Type\n2. Speak")
#    method = input("Enter the number associated with your preferred method: ")
#    
#    if method == "1":
#        user_input = input("You: ")
#        print("You said: ", user_input)
#        return user_input
#    elif method == "2":
#        return listen_to_user()
#    else:
#        print("Invalid input. Please enter 1 for Typing or 2 for Speaking.")
#        return chat_input_method()
