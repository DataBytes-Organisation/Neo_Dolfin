import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set up the SMTP connection
server = smtplib.SMTP('your_smtp_server_address', port_number)
server.starttls()
server.login('your_username', 'your_password')


# Compose the email message
message = MIMEMultipart()
message['From'] = 'your_email_address'
message['To'] = 'user_email_address'
message['Subject'] = 'DolFin MFA Code'

# Add MFA code and instructions to the email body
mfa_code = generate_mfa_code()
body = f"Your DolFin MFA code is: {mfa_code}. Use this code to complete the login process."
message.attach(MIMEText(body, 'plain'))
# Send the email
server.sendmail('your_email_address', 'user_email_address', message.as_string())
# Close the SMTP connection
server.quit()
#
