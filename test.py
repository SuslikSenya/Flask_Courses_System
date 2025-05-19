import smtplib
import os
from email.mime.text import MIMEText  # Исправлено: было MINEText


def send_email(message):
    sender = "alexslkarate@gmail.com"  # Замените на ваш email
    password = "hzhmmodmticnpwxl"  # Или укажите пароль напрямую

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Исправлено: было startts()

        server.login(sender, password)

        msg = MIMEText(message)  # Исправлено: было MINEText
        msg['Subject'] = 'CLICK ME PLEASE!'

        server.sendmail(sender, sender, msg.as_string())
        # server.quit()

        return "The message was sent successfully!"
    except Exception as _ex:
        return f"{_ex}\nCheck your login or password please!"


def main():
    message = input("Type your message: ")
    print(send_email(message=message))


if __name__ == "__main__":
    main()