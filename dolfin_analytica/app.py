from flask import Flask, render_template, request, redirect, url_for
import time

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def landing():
    if request.method == 'POST':
        # Access form data using request.form
        username = request.form['username']
        password = request.form['password']

        if username == 'dsuser':
            if password == 'dolfin123':

        # After processing the data, you can redirect to the /loading route
                return redirect(url_for('loading'))

    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        input_username = request.form['username']
        input_password = request.form['password']

        # Retrieve the user from the database
        user = User.query.filter_by(username=input_username).first()

        # Check if the user exists and the password is correct with stored hash
        if user and bcrypt.checkpw(input_password.encode('utf-8'), user.password):
            # Successful login, set a session variable to indicate that the user is logged in
            session['user_id'] = user.username 

            # If successful, check if test user or real user.
            row = UserTestMap.query.filter_by(userid = input_username).first()
            testId = 0
            if row != None:
                testId = row.testid
                print('######### test id:', testId)

            # Load transactional data
            loadDatabase(testId)            
            # log successful authentication challenge 
            add_user_audit_log(input_username, 'login-success', 'User logged in successfully.')
            # redirect to the dashboard.
            return redirect('/dash')
        
        ## Otherwise:
        # log un-successful authentication challenge
        add_user_audit_log(input_username, 'login-fail', 'User login failed.')
        return 'Login failed. Please check your credentials.'

    return render_template('login.html')  # Create a login form in the HTML template

@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/main')
def main():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True)