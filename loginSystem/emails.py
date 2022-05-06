import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "uweflixesd@gmail.com"
password = "uweflixesdA1?"

acceptance = """
<html>
  <body>
    <p>This is an automated email from UWEFlix (In HTML)<br>
       Your registration has been approved by a manager.<br>
       You can now log in!
    </p>
  </body>
</html>
"""

registration = """
<html>
  <body>
    <p>This is an automated email from UWEFlix (In HTML)<br>
       Your registration has been submitted and awaits manager approval.<br>
    </p>
  </body>
</html>
"""

refusal = """
<html>
  <body>
    <p>This is an automated email from UWEFlix (In HTML)<br>
       Your registration has been declined by a manager.<br>
       Please try again in the future.
    </p>
  </body>
</html>
"""


def booking_confirmation(booking_id):
    print(f'Booking ID: {booking_id}')
    print(type(booking_id))
    booking_id = str(booking_id)[2:len(booking_id)-4]
    print(f'String booking ID: {booking_id}')
    bc = f"""
    <html>
      <body>
        <p>This is an automated email from UWEFlix (In HTML)<br>
           Thank you for your booking with UWEFlix.<br>
           Booking ID: {booking_id}
        </p>
      </body>
    </html>
    """
    return bc

def cancellation_request(booking_id):
    print(f'Booking ID: {booking_id}')
    print(type(booking_id))
    booking_id = str(booking_id)[2:len(booking_id)-4]
    print(f'String booking ID: {booking_id}')
    bc = f"""
    <html>
      <body>
        <p>This is an automated email from UWEFlix (In HTML)<br>
           Your cancellation request has been submitted and awaits manager approval.<br>
           Booking ID: {booking_id}.
        </p>
      </body>
    </html>
    """
    return bc

def cancellation_reject(booking_id):
    print(f'Booking ID: {booking_id}')
    print(type(booking_id))
    booking_id = str(booking_id)[2:len(booking_id)-4]
    print(f'String booking ID: {booking_id}')
    bc = f"""
    <html>
      <body>
        <p>This is an automated email from UWEFlix (In HTML)<br>
           Your cancellation request has been rejected.<br>
           Please try again another time <br>
           Booking ID: {booking_id}.
        </p>
      </body>
    </html>
    """
    return bc

def booking_cancellation(booking_id):
    print(f'Booking ID: {booking_id}')
    print(type(booking_id))
    booking_id = str(booking_id)[2:len(booking_id)-4]
    # booking_id = str(booking_id[7:(len(booking_id)-4)])
    print(f'String booking ID: {booking_id}')
    bc = f"""
    <html>
      <body>
        <p>This is an automated email from UWEFlix (In HTML)<br>
           Your booking (reference number: {booking_id}) has been successfully cancelled.<br>
           If you have paid with credits, your account has been successfully refunded.<br>
           You are welcome to book with us again anytime.
        </p>
      </body>
    </html>
    """
    return bc


def emailBuilder(requestType, receiver_email, *booking_id):
    message = MIMEMultipart("alternative")
    message["From"] = sender_email

    if requestType == "registration":
        acceptText = registration
        message["Subject"] = "UWEFlix Registration"
    elif requestType == "acceptance":
        acceptText = acceptance
        message["Subject"] = "UWEFlix Registration Approval"
    elif requestType == "rejection":
        acceptText = refusal
        message["Subject"] = "UWEFlix Registration Rejection"
    elif requestType == "booking":
        acceptText = booking_confirmation(booking_id)
        message["Subject"] = "UWEFlix Booking Confirmation"
    elif requestType == "cancellation":
        acceptText = booking_cancellation(booking_id)
        message["Subject"] = "UWEFlix Booking Cancellation"
    elif requestType == "cancellationRequest":
        acceptText = cancellation_request(booking_id)
        message["Subject"] = "UWEFlix Booking Cancellation Request"
    elif requestType == "cancellationReject":
        acceptText = cancellation_reject(booking_id)
        message["Subject"] = "UWEFlix Booking Cancellation Rejection"


    part1 = MIMEText(acceptText, "html")
    message.attach(part1)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        try:
            print(f'Request type: {requestType}\n {message.as_string()}')
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
            print("Email has been sent")
        except smtplib.SMTPRecipientsRefused:
            print("No email sent, erroneous email provided")
    server.close()
