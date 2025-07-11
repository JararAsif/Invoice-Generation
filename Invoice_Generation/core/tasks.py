from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from .models import User, product
from decouple import config

@shared_task
def send_invoice_email(user_id):
    try:
        user = User.objects.get(id=user_id)
        to_email = config('to_email')
        subject = '🧾 Invoice Confirmation'
        from_email = settings.DEFAULT_FROM_EMAIL

        text_content = f"Hello {user.name}, your invoice has been successfully processed."

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f6f8fa; padding: 20px;">
            <div style="background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.05);">
                <h2 style="color: #28a745;">✅ Invoice Confirmation</h2>
                <p>Hello <strong>{user.name}</strong>,</p>
                <p>We’re pleased to let you know that your invoice has been successfully processed.</p>
                <p>If you have any questions, feel free to contact us.</p>
                <br>
                <p style="font-size: 0.9em; color: #888;">— InvoiceApp Team</p>
            </div>
        </body>
        </html>
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return "Invoice email sent successfully"

    except User.DoesNotExist:
        return "User not found"


@shared_task
def send_admin_mail(prod_id):
    try:
        prod = product.objects.get(id=prod_id)
        to_email = config('to_email')
        subject = f"⚠️ Low Stock Alert: {prod.name}"
        from_email = settings.DEFAULT_FROM_EMAIL

        text_content = f"Product '{prod.name}' stock is running low. Current quantity: {prod.quantity}."

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #fefefe; padding: 20px;">
            <div style="background-color: #fff3cd; padding: 20px; border-radius: 10px; border: 1px solid #ffeeba;">
                <h2 style="color: #856404;">⚠️ Low Stock Notification</h2>
                <p>Dear Admin,</p>
                <p>The following product is running low on stock:</p>
                <ul>
                    <li><strong>Product:</strong> {prod.name}</li>
                    <li><strong>Quantity Left:</strong> {prod.quantity}</li>
                    <li><strong>Price:</strong> ${prod.price}</li>
                </ul>
                <p>Please consider restocking it soon.</p>
                <br>
                <p style="font-size: 0.9em; color: #555;">— InvoiceApp System</p>
            </div>
        </body>
        </html>
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return "Admin notification email sent successfully"

    except product.DoesNotExist:
        return "Product does not exist"
