"""
📧 Email Service

Sends transactional emails: welcome, password reset, etc.
Uses SMTP configured via environment variables.
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import settings

logger = logging.getLogger(__name__)


def _send_email(to_email: str, subject: str, html_body: str) -> bool:
    """
    Send an email via SMTP.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML content of the email

    Returns:
        True if sent successfully, False otherwise
    """
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning("⚠️ SMTP not configured. Email not sent.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.FROM_EMAIL or settings.SMTP_USER
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        if settings.SMTP_USE_TLS:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
            server.starttls()

        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            # Google App Passwords are displayed with spaces (e.g. "xxxx xxxx xxxx xxxx")
            # but must be used without them for SMTP authentication.
            smtp_password = settings.SMTP_PASSWORD.replace(" ", "")
            server.login(settings.SMTP_USER, smtp_password)

        server.sendmail(msg["From"], [to_email], msg.as_string())
        server.quit()
        logger.info(f"✅ Email enviado a {to_email}: {subject}")
        return True

    except Exception as e:
        logger.error(f"❌ Error enviando email a {to_email}: {e}")
        return False


def send_welcome_email(to_email: str, username: str) -> bool:
    """
    Send a welcome email after account creation.

    Args:
        to_email: New user's email
        username: New user's username

    Returns:
        True if sent successfully
    """
    subject = "¡Bienvenido a TimeSeriesLab! 🎉"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Inter, sans-serif; background: #0f172a; color: #e2e8f0; padding: 32px;">
      <div style="max-width: 560px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 32px;">
        <h1 style="color: #2dd4bf; font-size: 24px; margin-bottom: 8px;">¡Bienvenido, {username}! 👋</h1>
        <p style="color: #94a3b8; margin-bottom: 16px;">
          Tu cuenta en <strong style="color: #e2e8f0;">TimeSeriesLab</strong> ha sido creada correctamente.
        </p>
        <p style="color: #94a3b8; margin-bottom: 16px;">
          Ya puedes acceder a la plataforma para:
        </p>
        <ul style="color: #94a3b8; line-height: 1.8; margin-bottom: 24px;">
          <li>📂 Cargar tus series temporales (CSV/XLSX)</li>
          <li>🤖 Entrenar modelos Prophet y ARIMA/SARIMA</li>
          <li>📈 Visualizar predicciones y métricas</li>
          <li>⚖️ Comparar modelos entre sí</li>
        </ul>
        <p style="color: #64748b; font-size: 13px;">
          Si no has creado esta cuenta, ignora este mensaje.
        </p>
      </div>
    </body>
    </html>
    """
    return _send_email(to_email, subject, html_body)


def send_password_reset_email(to_email: str, username: str, reset_token: str, base_url: str) -> bool:
    """
    Send a password reset email with a one-time link.

    Args:
        to_email: User's email address
        username: User's username
        reset_token: Signed JWT token for password reset
        base_url: Base URL of the frontend application

    Returns:
        True if sent successfully
    """
    reset_link = f"{base_url}/reset-password?token={reset_token}"
    subject = "Restablecer contraseña — TimeSeriesLab"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Inter, sans-serif; background: #0f172a; color: #e2e8f0; padding: 32px;">
      <div style="max-width: 560px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 32px;">
        <h1 style="color: #2dd4bf; font-size: 22px; margin-bottom: 8px;">Restablece tu contraseña</h1>
        <p style="color: #94a3b8; margin-bottom: 16px;">
          Hola <strong style="color: #e2e8f0;">{username}</strong>, hemos recibido una solicitud para cambiar la contraseña de tu cuenta.
        </p>
        <p style="color: #94a3b8; margin-bottom: 24px;">
          Pulsa el botón de abajo para crear una contraseña nueva. El enlace es válido durante <strong style="color: #e2e8f0;">1 hora</strong>.
        </p>
        <a href="{reset_link}"
           style="display: inline-block; background: linear-gradient(135deg,#2dd4bf,#0ea5e9);
                  color: #0f172a; font-weight: 700; padding: 12px 28px; border-radius: 8px;
                  text-decoration: none; font-size: 15px; margin-bottom: 24px;">
          Cambiar contraseña
        </a>
        <p style="color: #94a3b8; font-size: 13px; margin-top: 16px;">
          O copia este enlace en tu navegador:<br>
          <span style="color: #2dd4bf; word-break: break-all;">{reset_link}</span>
        </p>
        <hr style="border: none; border-top: 1px solid #334155; margin: 24px 0;">
        <p style="color: #64748b; font-size: 12px;">
          Si no solicitaste este cambio, puedes ignorar este mensaje. Tu contraseña no cambiará.
        </p>
      </div>
    </body>
    </html>
    """
    return _send_email(to_email, subject, html_body)
