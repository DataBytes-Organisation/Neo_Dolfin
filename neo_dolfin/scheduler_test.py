from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os 

print("Entered the program...")
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/user_database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db/user_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db= SQLAlchemy(app)

class Response(db.Model):
    __tablename__ = 'SurveyResponses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=False)
    response1 = db.Column(db.String(10), nullable=False)
    response2 = db.Column(db.String(30), nullable=False)
    response3 = db.Column(db.String(50), nullable=False)
    response4 = db.Column(db.String(10), nullable=False)
    response5 = db.Column(db.String(10), nullable=False)
    response6 = db.Column(db.String(25), nullable=False)
    response7 = db.Column(db.String(255), nullable=False)
    response8 = db.Column(db.String(255), nullable=False)
    response9 = db.Column(db.Integer, nullable=False)


    def __repr__(self):
        return f'<Response {self.name}'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)    

@app.route("/")
def survey():
    print("under survey function...")
    return render_template("survey.html")

@app.route("/submit", methods=["POST"])
def submit():
    print("under surveysubmit function...")
    email = "testmail"
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        email = User.query.filter_by(email=email).first()
        print("user email: ", email)
        question_1_yes = data.get('question_1_yes')
        question_1_no = data.get('question_1_no')

        # Assigning response based on the values of question_1_yes and question_1_no
        if question_1_yes is True:
            response_1 = 'Yes'
        elif question_1_no is True:
            response_1 = 'No'
        else:
            response_1 = 'None'
        
        text_box_1_data = data.get('text_box_1')
        response1_2 = str(text_box_1_data) if 'text_box_1' in data else 'None'
        satisfaction_value=data.get('satisfaction_value')
        response_2=str(satisfaction_value) if 'satisfaction_value' in data else 'None'
        ease_of_access_value=data.get('ease_of_access_value')
        response_3=str(ease_of_access_value) if 'ease_of_access_value' in data else 'None'
        
        question_4_yes = data.get('question_4_yes')
        question_4_no = data.get('question_4_no')

        # Assigning response based on the values of question_1_yes and question_1_no
        if question_4_yes is True:
            response_4 = 'Yes'
        elif question_4_no is True:
            response_4 = 'No'
        else:
            response_4 = 'None'
        text_box_2_data = data.get('text_box_2')
        response4_2 = str(text_box_2_data) if 'text_box_2' in data else 'None'
        question_5_yes = data.get('question_5_yes')
        question_5_no = data.get('question_5_no')

        # Assigning response based on the values of question_5_yes and question_5_no
        if question_5_yes is True:
            response_5 = 'Yes'
        elif question_5_no is True:
            response_5 = 'No'
        else:
            response_5 = 'None'
        text_box_3_data = data.get('text_box_3')
        response5_2 = str(text_box_3_data) if 'text_box_3' in data else 'None'
        frequency_value=data.get('frequency_value')
        response_6=str(frequency_value) if 'frequency_value' in data else 'None'
        additional_features = data.get('additional_features')
        response_7=str(additional_features) if 'additional_features' in data else 'None'
        privacy_security_concerns=data.get('privacy_security_concerns')
        response_8=str(privacy_security_concerns) if 'privacy_security_concerns' in data else 'None'
        feelings_question = data.get('feelings_question')
        response_9=str(feelings_question) if 'feelings_question' in data else 'None'
        print("responses:"+response_1+response1_2+response_2+response_3+response_4+response4_2+response_5+response5_2+response_6+response_7+response_8+response_9)
        print("freq value:",response_6)
        return "Feedback received successfully"
    

    #email = User.query.filter_by(email=email).first()
    """response = Response(email=email, response1=response1, response2=response2)
    db.session.add(response)
    db.session.commit()"""

    return "Thank you for your Feedback!"
    
if __name__ == "__main__": 
    with app.app_context():
        db.create_all()
    app.run(debug=True)



