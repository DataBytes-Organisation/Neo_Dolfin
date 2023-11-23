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

@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/main')
def main():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True)