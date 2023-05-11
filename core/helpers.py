import socket
socket.getaddrinfo('127.0.0.1', 8080)
from django.conf import settings 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def sendMail(e_receiver,token):
    # Thông tin tài khoản Gmail của bạn
    sender_email = settings.EMAIL_HOST_USER
    sender_password = settings.EMAIL_HOST_PASSWORD
    # Thông tin email người nhận
    receiver_email = e_receiver

    # Tạo một đối tượng MIMEMultipart để chứa email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    # message["Subject"] = "[MEDICAL_PLANTS] Please verify your device"
    message["Subject"] = 'Reset password'

    # Thêm nội dung email
    text = f'Hi , click on the link to reset your password http://127.0.0.1:8000/change-password/{token}/'
    message.attach(MIMEText(text, "plain"))

    # Tạo kết nối SMTP với máy chủ Gmail
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)

    # Gửi email
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()