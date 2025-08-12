import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

# Загружаем переменные окружения
load_dotenv()

# Функция для отправки писем по электронной почте
async def send_reset_password_email(email: str, reset_token: str, reset_url: str):
    """
    Отправляет электронное письмо с ссылкой для сброса пароля.
    """
    try:
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASSWORD")

        # Формируем сообщение
        message = MIMEMultipart()
        message['From'] = "support@example.com"
        message['To'] = email
        message['Subject'] = "Сброс пароля"

        # Текст письма
        body = f"""
        Здравствуйте!\n\n
        Для сброса пароля пройдите по ссылке: {reset_url}?token={reset_token}\n\n
        С уважением,\nКоманда поддержки
        """
        message.attach(MIMEText(body, 'plain'))

        # Подключение к почтовому серверу и отправка письма
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.sendmail(message['From'], message['To'], message.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Ошибка при отправке письма: {str(e)}")
        return False