from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

# 
from .base_importaciones import (
    Contacto,
    RespuestaForm,
    login_required,
    never_cache,
    messages,
    render,
    redirect
)


def lista_contactos(request):
    contactos = Contacto.objects.all()
    respuesta_form = RespuestaForm()  # Instancia del formulario
    return render(request, 'lista_contactos.html', {
        'contactos': contactos,
        'respuesta_form': respuesta_form
    })


def responder_contacto(request, contacto_id):
    contacto = get_object_or_404(Contacto, id=contacto_id)
    
    if request.method == "POST":
        form = RespuestaForm(request.POST)
        if form.is_valid():
            respuesta = form.cleaned_data.get('respuesta')
            
            # Preparar el contenido del correo de respuesta
            subject = f"Respuesta a tu {contacto.get_deseo_display()}"
            text_content = "Por favor, visualiza este correo en un cliente que soporte HTML."
            from_email = settings.DEFAULT_FROM_EMAIL  # Asegúrate de tenerlo configurado en settings.py
            recipient_list = [contacto.email]
            
            # Preparar el contexto para la plantilla HTML del correo
            context = {
                'nombre': contacto.nombre,
                'deseo': contacto.get_deseo_display(),
                'respuesta': respuesta,
            }
            
            # Renderizar el contenido HTML usando la plantilla "respuesta.html"
            html_content = render_to_string("respuesta.html", context)
            
            # Crear el mensaje y adjuntar el contenido HTML para que se muestre en el cuerpo del correo
            msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            # Actualizar el estado del contacto a "resuelto"
            contacto.estado = 'resuelto'
            contacto.save()
            
            messages.success(request, "La respuesta ha sido enviada y el contacto marcado como resuelto.")
            return redirect('lista_contactos')
    else:
        form = RespuestaForm()
    
    return render(request, 'responder_contacto.html', {'contacto': contacto, 'form': form})