# Bibliotecas estándar
import pytz
from sqlite3 import IntegrityError
from itsdangerous import URLSafeSerializer, BadSignature
# Importaciones de Django
from django.conf import settings
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.serializers import serialize
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.template.loader import get_template, render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy, reverse
from django.db.models import Avg  
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
# Importaciones de la aplicación
from modulos.dashboard.models import UsuarioPersonalizado, Horario, Psicologo, Preguntas, Cita, Estudiante, Contacto, Review,Contacto, Cita, Notificacion
from .forms import UsuarioPersonalizadoCreationForm, UsuarioPersonalizadoEditForm, HorarioForm, PreguntasForm, EmailAuthenticationForm, CitaForm, EstudianteForm, RespuestaForm, ReviewForm

# Create your views here.

    return render(request, 'dashboard.html', context)
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
        
        # Notificación para el estudiante (si aplica)
        if instance.usuario:  # Asumiendo que Contacto tiene relación con usuario
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





    



#preguntas


#buzon:

#citas:

def generar_token(cita_id):
    serializer = URLSafeSerializer(settings.SECRET_KEY)
    return serializer.dumps(cita_id)
    
class CrearReviewView(FormView):
    template_name = 'formularios/review_form.html'
    form_class = ReviewForm  
    success_url = reverse_lazy('gracias_review')
    

    def get_cita(self):
        try:
            token = self.kwargs['token']
            print(f"\n--- DEBUG GET_CITA ---")
            print(f"Token recibido: {token}")
            
            serializer = URLSafeSerializer(settings.SECRET_KEY)
            cita_id = serializer.loads(token)
            print(f"ID deserializado: {cita_id} (tipo: {type(cita_id)})")
            
            cita = Cita.objects.get(id=cita_id)
            print(f"Cita encontrada: {cita}")
            return cita
            
        except BadSignature as e:
            print(f"Error BadSignature: {str(e)}")
            return None
        except Cita.DoesNotExist:
            print(f"Error: Cita no existe en DB")
            return None
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token'] = self.kwargs['token']
        cita = self.get_cita()
        
        if not cita:
            context['error'] = "Enlace inválido o expirado"
            return context
            
        if Review.objects.filter(cita=cita).exists():
            context['error'] = "Ya has calificado esta sesión."
        else:
            context['cita'] = cita
            
        return context
    def form_valid(self, form):
        print("\n--- DEBUG FORM_VALID ---")
        cita = self.get_cita()
        
        if not cita:
            print("Error: Cita no existe en form_valid")
            form.add_error(None, "Enlace inválido o expirado")
            return self.form_invalid(form)
            
        if Review.objects.filter(cita=cita).exists():
            print("Error: Reseña ya existe")
            form.add_error(None, "Ya has calificado esta sesión.")
            return self.form_invalid(form)
        
        try:
            print("Intentando crear reseña...")
            Review.objects.create(
                cita=cita,
                psicologo=cita.psicologo,
                estudiante=cita.estudiante,
                puntuacion=form.cleaned_data['puntuacion'],
                comentario=form.cleaned_data['comentario']
            )
            print("¡Reseña creada exitosamente!")
        except IntegrityError as e:
            print(f"Error IntegrityError: {str(e)}")
            form.add_error(None, "Error al crear la reseña")
            return self.form_invalid(form)
            
        return super().form_valid(form)
class CitaDeleteView(DeleteView):
    model = Cita
    # Esta plantilla se usa para confirmar la eliminación; también podrías hacer la confirmación mediante un modal.
    template_name = "citas.html"
    success_url = reverse_lazy("citas")

    def post(self, request, *args, **kwargs):
        messages.success(request, "¡Cita eliminada correctamente!")
        print("Mensaje de eliminación añadido")  # Verifica esto en la consola
        return self.delete(request, *args, **kwargs)
    
class GraciasReviewView(TemplateView):
    template_name = 'gracias_review.html'    
    