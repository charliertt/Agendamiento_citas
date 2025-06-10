from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@shared_task
def enviar_correo_confirmacion(context, recipient_email):
    html_content = render_to_string('cita_confirmacion.html', context)
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(
        subject="Confirmación de tu cita",
        body=text_content,
        from_email="puntomentalcosfacali@gmail.com",
        to=[recipient_email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()