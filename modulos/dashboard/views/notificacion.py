from .base_importaciones import (JsonResponse, get_user_model,
                                 Notificacion, Contacto, Cita, Respuesta)

from django.contrib.auth import authenticate, login, get_user_model, logout
from django.db.models.signals import post_save
from django.dispatch import receiver

def marcar_notificacion_leida(request, notificacion_id):
    if request.method == 'POST' and request.is_ajax():
        notificacion = Notificacion.objects.get(id=notificacion_id, usuario=request.user)
        notificacion.leida = True
        notificacion.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
@receiver(post_save, sender=Contacto)
def crear_notificacion_contacto(sender, instance, created, **kwargs):
    if created:
        User = get_user_model()
        
      
        if instance.usuario:  #
            Notificacion.objects.create(
                usuario=instance.usuario,
                destinatario_tipo='estudiante',
                tipo='contacto',
                mensaje=f"Tu solicitud de {instance.get_deseo_display()} fue recibida",
                enlace=f"/contactos/{instance.id}/"
            )
        
        # Notificación para administrativos
        admins = User.objects.filter(rol='administrativo')
        for admin in admins:
            Notificacion.objects.create(
                usuario=admin,
                destinatario_tipo='administrativo',
                tipo='contacto',
                mensaje=f"Nuevo {instance.get_deseo_display()} de {instance.nombre}",
                enlace=f"/admin/contactos/{instance.id}/"
            )

@receiver(post_save, sender=Cita)
def crear_notificacion_cita(sender, instance, created, **kwargs):
    # Notificación para estudiante
    Notificacion.objects.create(
        usuario=instance.estudiante.usuario,
        destinatario_tipo='estudiante',
        tipo='cita',
        mensaje=f"Tu cita del {instance.fecha_hora.strftime('%d/%m/%Y')} está {instance.get_estado_display().lower()}",
        enlace=f"/citas/{instance.id}/"
    )
    
    # Notificación para psicólogo
    Notificacion.objects.create(
        usuario=instance.psicologo.usuario,
        destinatario_tipo='psicologo',
        tipo='cita',
        mensaje=f"Nueva cita con {instance.estudiante.usuario.get_full_name()}",
        enlace=f"/citas/{instance.id}/"
    )



@receiver(post_save, sender=Respuesta)
def crear_notificacion_cuestionario(sender, instance, created, **kwargs):
    if created:
        Notificacion.objects.create(
            usuario=instance.usuario,
            destinatario_tipo='estudiante',
            tipo='cuestionario',
            mensaje=f"¡Cuestionario completado! Calificación: {instance.calificacion:.2f}",
            enlace=f"/respuestas/{instance.id_respuesta}/"
        )