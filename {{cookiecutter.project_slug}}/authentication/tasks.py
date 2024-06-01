from celery import shared_task
from django.core.mail import EmailMultiAlternatives


@shared_task
def send_email(sender, recipient, subject, body):
    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=sender,
        to=recipient,
    )
    email.attach_alternative(body, "text/html")
    email.send()
    return "Email sent successfully"
