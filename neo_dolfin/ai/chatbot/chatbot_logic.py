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

# print random response from appropriate responses for label
def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    probability = float(intents_list[0]['probability'])
    list_of_intents = intents_json['intents']
    result = ""
    if probability < 0.2:  # Adjust the threshold as needed
        result = "I'm sorry, but I'm not sure how to help with that. Could you please provide more information?"
    else:
        for i in list_of_intents:
            if i['tag'] == tag:
                result = random.choice(i['responses'])
                break
    return result

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
def determine_sentiment(message):
    global positive_count, negative_count, neutral_count, total_count
    analysis = TextBlob(message)
    total_count += 1
    sentiment = "neutral"
    
    if analysis.sentiment.polarity > 0:
        positive_count += 1
        sentiment = 'positive'
    elif analysis.sentiment.polarity < 0:
        negative_count += 1
        sentiment = 'negative'
    else:
        neutral_count += 1
    
    return sentiment

# Define a function to initialize and run the chatbot logic
def initialize_chatbot_logic():
    global last_bot_reply, positive_count, negative_count, neutral_count, total_count

    # Reset chatbot variables
    last_bot_reply = ""
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    total_count = 0

    # Create an infinite loop that prompts for input
    print("Chatbot live. Say or type 'end' to stop the conversation.")
    while True:
        message = chat_input_method()
        if message.lower() == "end":
            print("Bot: Goodbye! Have a nice day!")
            break
        elif message != "":
            ints = predict_class(message)
            res = get_response(ints, intents)

            sentiment = determine_sentiment(message)
            print(f"Sentiment: {sentiment}")
            # Calculate sentiment percentages
            if total_count > 0:
                print(f"Positive: {(positive_count/total_count)*100}%")
                print(f"Negative: {(negative_count/total_count)*100}%")
                print(f"Neutral: {(neutral_count/total_count)*100}%")
            
            if sentiment == 'negative' and (negative_count/total_count)*100 >= 50:
                print("Storing negative conversation for review.")
                with open('negative_conversations.txt', 'a') as f:
                    f.write(f"Bot: {last_bot_reply}\n")
                    f.write(f"User: {message}\n")
                    f.write("---\n")

            # Overwrite the last_bot_reply with the current response of the bot
            last_bot_reply = res

            if res.startswith("I'm sorry"):
                print("Bot:", res)
            else:
                print("Bot:", res)

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
