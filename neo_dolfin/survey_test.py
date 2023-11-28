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
    email = request.form['email']
    response1 = request.form['response1']
    response2 = request.form['response2']

    #email = User.query.filter_by(email=email).first()
    response = Response(email=email, response1=response1, response2=response2)
    db.session.add(response)
    db.session.commit()

    return "Thank you for your Feedback!"
    
if __name__ == "__main__": 
    with app.app_context():
        db.create_all()
    app.run(debug=True)



