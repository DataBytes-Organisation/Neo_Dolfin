from flask import Flask, render_template, request, jsonify
import requests
import urllib.parse
import pandas as pd
import creds
import os 
from sqlalchemy import Integer, String
from flask_sqlalchemy import SQLAlchemy
import app


print("Entered Address Validation program")


##### code for client-side test

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db= SQLAlchemy(app)

#@app.route("/")
#def addressvalidationclient():
#    print("under addressvalidation function...")
#    return render_template("addressValidation_CS.html")





# importing creds
API_KEY=creds.AddFind_API_KEY
SECRET=creds.AddFind_SECRET

address = "30 mullland crescent, Grovedale, VIC"
encoded_address = urllib.parse.quote(address)
#print(encoded_address)

"""headers = {
    'accept' : "*/*",
    'Accept-Encoding' : "gzip, deflate, br",
    'Content-Type': "application/json"
}"""
#response = requests.post('https://api.addressfinder.io/api/au/address/v2/verification/', params=params, headers=headers)

try:
    fullurl=f"https://api.addressfinder.io/api/au/address/v2/verification/?key={API_KEY}&secret={SECRET}&format=json&q={encoded_address}&gnaf=1&paf=1&domain=localhost"
    response =requests.get(fullurl)
    print(response.status_code)
    # prints the int of the status code. Find more at httpstatusrappers.com :)
except requests.ConnectionError:
    print("failed to connect, response code: ", response.status_code)

print(response.url)
result = response.json()
print("result of json req:", result )


   
#print(result['success'])
def process_response(responsedata):
    # Check if the response contains valid address information
    if result['success']:
        if result['matched']: # Address is valid
            print("Address Validated")
        else:
        # Address is not valid
            print("invalid address...")
    else:
        print("Connection Failed...")
           
    
process_response(result)

# Including DB elements to write user details into database

id = 1
addressline_1 = "30 Mulholland crescent"
addressline_2 = ""
suburb = "Grovedale"
state = "Vic"
postcode = 3216

class User(db.Model):
    __tablename__ = 'user_address'
    id = db.Column(Integer, primary_key=True)
    addressline_1 = db.Column(String(120), nullable=False)
    addressline_2 = db.Column(String(60), nullable=True)
    suburb = db.Column(String(120), nullable=False)
    state = db.Column(String(30), nullable=False)
    postcode = db.Column(Integer, nullable=False)
   
    def __repr__(self):
        return f"User('{self.id}', '{self.addressline_1}', '{self.addressline_2}', '{self.suburb}', '{self.state}','{self.postcode}')"
 
if __name__ == "__main__": 
    with app.app_context():
        db.create_all()
    app.run(debug=True)
