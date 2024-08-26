import random
from celery import shared_task
from signals_auth.models import OneTimePassword
from django.conf import settings

from django.core.mail import send_mail
from django.template.loader import render_to_string


@shared_task
def HandleEmail(user_id, email, first_name, mode):
    try:
        subject = "RellTrader otp"
        otp = str(random.randint(100000, 999999))

        if mode == "create":
            OneTimePassword.objects.create(user_id=user_id, otp=otp)
        else:
            user_token = OneTimePassword.objects.get(user_id=user_id)
            user_token.otp = otp
            user_token.save()
        context = {"subject": subject, "name": first_name, "otp_code": otp}
        html_content = render_to_string("email_template.html", context)
        send_mail(
            subject=subject,
            message="",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
            html_message=html_content,
        )
    except Exception as e:
        print(str(e))
