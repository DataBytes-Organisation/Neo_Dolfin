from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, Regexp

#CLASSES
class SignInForm(FlaskForm): #Used on signin.html
    username = StringField('E-Mail', validators=[DataRequired(), Email(message="This field requires a valid email address")])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class SignInMFAForm(FlaskForm): #Used on signinmfa.html
    otp = PasswordField('One Time Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class SignUpForm(FlaskForm): #Used on signup.html
    given_name = StringField('Given_name',validators=[DataRequired()])
    family_name = StringField('Family_name',validators=[DataRequired()])
    nickname = StringField('Nickname',validators=[DataRequired()])
    username = StringField('E-Mail', validators=[DataRequired(),  Email(message="This field requires a valid email address")])
    password = PasswordField('Password', validators=[DataRequired(), Regexp("(?=[A-Za-z0-9@#$%^&+!=]+$)^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@#$%^&+!=])(?=.{8,}).*$",
                                                                            message="At least 8 characters, Minimum 1 Uppercase, 1 Lowercase, 1 Number, 1 Special Character and only contains symbols from the alphabet")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

class SignUpConfForm(FlaskForm): #Used on signup.html
    signupconf = PasswordField('Confirmation Code', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SignUpMFADForm(FlaskForm): #Used on signupmfad.html
    signupmfadevicename = StringField('MFA Device Name', validators=[DataRequired()])
    signupmfadevicecode = StringField('MFA Device Code', validators=[DataRequired()])
    submit = SubmitField('Register Device')
