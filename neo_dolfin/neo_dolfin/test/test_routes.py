import inspect
import app

def test_signin_route_logic():
    route_handler = app.signin
    source_lines = inspect.getsourcelines(route_handler)[0]

    # Extract return statements from the source lines and preprocess them for comparison
    return_statements = [line.strip().split("#")[0].strip().lower() for line in source_lines if line.strip().startswith("return ")]

    expected_return_statements = [
        "return redirect('/signinmfa')".lower(),
        "return redirect('/signupmfad')".lower(),
        "return redirect('/home/')".lower(),
        "return redirect('/signupconf')".lower(),
        "return render_template('signin.html', form=form, error='invalid credentials. please try again.')".lower(),
        "return render_template('signin.html', form=form, error='an error occurred. please try again.')".lower(),
        "return render_template('signin.html', form=form)".lower()
    ]
    # Check if the beginnings of the actual return statements match the beginnings of the expected beginnings
    assert all(return_statement.startswith(expected_statement.split('(')[0].strip()) for return_statement, expected_statement in zip(return_statements, expected_return_statements))


def test_signinmfa_route_logic():
    route_handler = app.signinmfa
    source_lines = inspect.getsourcelines(route_handler)[0]
    expected_return_statements = [
        "return redirect('/home/')",
        "return render_template('signinmfa.html', form=form, error=e)",
        "return render_template('signinmfa.html', form=form)"
    ]
    return_statements = [line.strip() for line in source_lines if line.strip().startswith("return ")]
    assert return_statements == expected_return_statements

def test_signup_route_logic():
    route_handler = app.signup
    source_lines = inspect.getsourcelines(route_handler)[0]
    expected_return_statements = [
        "return redirect('/signupconf')",
        "return render_template('signup.html', form=form, error='Username already exists. Please choose a different one.')",
        "return render_template('signup.html', form=form, error='An error occurred. Please try again.')",
        "return render_template('signup.html', form=form)"
    ]
    return_statements = [line.strip() for line in source_lines if line.strip().startswith("return ")]
    assert return_statements == expected_return_statements

def test_signupconf_route_logic():
    route_handler = app.signupconf
    source_lines = inspect.getsourcelines(route_handler)[0]
    expected_return_statements = [
        "return redirect('/signin')",
        "return render_template('signupconf.html', form=form, error='Code has expired, please generate a new one')",
        "return render_template('signupconf.html', form=form, error='An error occurred. Please try again.')",
        "return render_template('signupconf.html', form=form)"
    ]
    return_statements = [line.strip() for line in source_lines if line.strip().startswith("return ")]
    assert return_statements == expected_return_statements

def test_resendconfemail_route_logic():
    route_handler = app.resendconfemail
    source_lines = inspect.getsourcelines(route_handler)[0]
    expected_return_statements = [
    "return redirect('signupconf.html', form=form)",
    "return render_template('signupconf.html', form=form, error='An error occurred. Please try again.')"
    ]
    # Extract return statements from the source lines and preprocess them for comparison
    return_statements = [line.strip().split("#")[0].strip() for line in source_lines if line.strip().startswith("return ")]

    # Check if the actual return statements match the expected return statements
    assert return_statements == expected_return_statements

def test_signupmfad_route_logic():
    route_handler = app.signupmfadevice
    source_lines = inspect.getsourcelines(route_handler)[0]
    expected_return_statements = [
        "return redirect('/signin')",
        "return render_template('signupmfad.html', form=form, error='There was an error registering your device. Please try again.')",
        "return render_template('signupmfad.html', form=form)"
    ]
    return_statements = [line.strip() for line in source_lines if line.strip().startswith("return ")]
    assert return_statements == expected_return_statements
