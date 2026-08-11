import smtplib
from email.message import EmailMessage
from app.core.config import get_settings

def send_application_email(
    to_email: str,
    candidate_name: str,
    job_title: str,
    status: str,
    reason: str = "",
) -> str:
    settings = get_settings()

    if not all([settings.smtp_host, settings.smtp_username, settings.smtp_password, settings.smtp_from]):
        return "NOT_CONFIGURED"

    subject = f"TalentGraph application {status.lower()}: {job_title}"

    if status == "SUCCESS":
        body = (
            f"Hello {candidate_name},\n\n"
            f"Your application for '{job_title}' was submitted successfully.\n\n"
            "You can view your application history from your TalentGraph profile.\n\n"
            "Regards,\nTalentGraph"
        )
    else:
        body = (
            f"Hello {candidate_name},\n\n"
            f"Your application for '{job_title}' could not be submitted.\n"
            f"Reason: {reason or 'Please try again later.'}\n\n"
            "Regards,\nTalentGraph"
        )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(msg)
        return "SENT"
    except Exception:
        return "FAILED"
