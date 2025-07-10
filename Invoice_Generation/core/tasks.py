from celery import shared_task
from .models import User
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_invoice_email(user_id):
    try:
        user = User.objects.get(id=user_id)
        email='makofa9015@iamtile.com'
        send_mail(
            subject='Invoice Confirmation',
            message=f'Hello {user.name}, your invoice has been successfully processed.',
            from_email= 'jararvirk10@gmail.com',
            recipient_list=[email],
            fail_silently=True,
        )
        return "Email sent successfully"
    except User.DoesNotExist:
        return "User not found"