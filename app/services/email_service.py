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


def send_password_reset_email(to_email: str, username: str) -> bool:
    """
    Send a password change confirmation email.

    Args:
        to_email: User's email
        username: User's username or email

    Returns:
        True if sent successfully
    """
    subject = "Contraseña modificada - TimeSeriesLab 🔑"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Inter, sans-serif; background: #0f172a; color: #e2e8f0; padding: 32px;">
      <div style="max-width: 560px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 32px;">
        <h1 style="color: #2dd4bf; font-size: 24px; margin-bottom: 8px;">Contraseña modificada ✅</h1>
        <p style="color: #94a3b8; margin-bottom: 16px;">
          Hola <strong>{username}</strong>,
        </p>
        <p style="color: #94a3b8; margin-bottom: 24px;">
          Tu contraseña en <strong>TimeSeriesLab</strong> ha sido modificada correctamente.
        </p>
        <p style="color: #94a3b8; margin-bottom: 24px;">
          Si no realizaste este cambio, contacta inmediatamente con nuestro equipo de soporte.
        </p>
        <p style="color: #64748b; font-size: 13px;">
          Por tu seguridad, no compartimos contraseñas por correo electrónico.
        </p>
      </div>
    </body>
    </html>
    """
    return _send_email(to_email, subject, html_body)


def send_password_reset_link_email(to_email: str, username: str, reset_token: str, base_url: str) -> bool:
    """
    Send a password reset link via email.

    Args:
        to_email: User's email
        username: User's username or email
        reset_token: Password reset token
        base_url: Frontend base URL for the reset link

    Returns:
        True if sent successfully
    """
    reset_link = f"{base_url}/reset-password?token={reset_token}"
    subject = "Restablecer contraseña - TimeSeriesLab 🔑"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Inter, sans-serif; background: #0f172a; color: #e2e8f0; padding: 32px;">
      <div style="max-width: 560px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 32px;">
        <h1 style="color: #2dd4bf; font-size: 24px; margin-bottom: 8px;">Restablecer contraseña</h1>
        <p style="color: #94a3b8; margin-bottom: 16px;">
          Hola <strong>{username}</strong>,
        </p>
        <p style="color: #94a3b8; margin-bottom: 24px;">
          Hemos recibido una solicitud para restablecer tu contraseña. 
          Haz clic en el botón de abajo para crear una nueva contraseña.
        </p>
        <div style="text-align: center; margin-bottom: 24px;">
          <a href="{reset_link}" style="display: inline-block; background: #2dd4bf; color: #0f172a; padding: 12px 32px; border-radius: 8px; text-decoration: none; font-weight: bold;">
            Restablecer contraseña
          </a>
        </div>
        <p style="color: #64748b; font-size: 13px; margin-bottom: 16px;">
          O copia y pega este enlace en tu navegador:<br>
          <code style="background: #0f172a; padding: 8px; border-radius: 4px; word-break: break-all;">{reset_link}</code>
        </p>
        <p style="color: #64748b; font-size: 13px; margin-bottom: 8px;">
          <strong>Este enlace expira en 1 hora.</strong>
        </p>
        <p style="color: #64748b; font-size: 13px;">
          Si no solicitaste el restablecimiento de contraseña, ignora este mensaje.
        </p>
      </div>
    </body>
    </html>
    """
    return _send_email(to_email, subject, html_body)

