import smtplib
from email.message import EmailMessage
from core.config import secret


def mail_configured():
    return all(secret(k) for k in ('SMTP_HOST','SMTP_PORT','SMTP_USERNAME','SMTP_PASSWORD','SMTP_FROM'))


def send_password_reset_email(destination, code, minutes=20):
    if not mail_configured():
        raise RuntimeError('SMTP_NOT_CONFIGURED')
    msg=EmailMessage()
    msg['Subject']='Recuperacion de contrasena de Condo_Smart'
    msg['From']=secret('SMTP_FROM')
    msg['To']=destination
    msg.set_content(
        'Se solicito recuperar la contrasena de tu cuenta Condo_Smart.\n\n'
        f'Codigo temporal: {code}\n'
        f'El codigo vence en {minutes} minutos y solo puede utilizarse una vez.\n\n'
        'Si no solicitaste este cambio, ignora este correo. Tu contrasena actual no fue enviada ni modificada.'
    )
    host=secret('SMTP_HOST'); port=int(secret('SMTP_PORT'))
    use_ssl=str(secret('SMTP_USE_SSL','false')).lower() in ('1','true','yes')
    use_tls=str(secret('SMTP_USE_TLS','true')).lower() in ('1','true','yes')
    cls=smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
    with cls(host,port,timeout=20) as server:
        if use_tls and not use_ssl: server.starttls()
        server.login(secret('SMTP_USERNAME'),secret('SMTP_PASSWORD'))
        server.send_message(msg)
