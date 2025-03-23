# Bibliotecas estándar
import pytz
from sqlite3 import IntegrityError
from itsdangerous import URLSafeSerializer, BadSignature

# Importaciones de Django
from django.conf import settings
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

# Importaciones de la aplicación
from modulos.dashboard.models import UsuarioPersonalizado, Horario, Psicologo, Preguntas, Cita, Estudiante, Contacto, Review
from .forms import UsuarioPersonalizadoCreationForm, UsuarioPersonalizadoEditForm, HorarioForm, PreguntasForm, EmailAuthenticationForm, CitaForm, EstudianteForm, RespuestaForm, ReviewForm


# Create your views here.
@never_cache
@login_required(login_url='/login')
def dashboard(request):
    notificaciones = Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).order_by('-fecha_creacion')[:5]
    total_citas = Cita.objects.count()
    citas_completadas = Cita.objects.filter(estado='completada').count()
    conversion_rate = (citas_completadas / total_citas * 100) if total_citas > 0 else 0
    
    # Cálculo de reseñas
    reseñas = Review.objects.all()
    cantidad_reseñas = reseñas.count()
    promedio_reseñas = reseñas.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
    porcentaje_satisfaccion = (promedio_reseñas / 5) * 100  # Convertir a porcentaje
    
    
    # Cálculo de tendencia (ejemplo: cambio porcentual último mes)
    # Necesitarías implementar lógica específica según tus datos históricos
    porcentaje_cambio_citas = 7  # Ejemplo estático, reemplazar con cálculo real
    
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Cita creada correctamente!")
            return redirect('dashboard')
        else:
            messages.error(request, "Hubo un error al crear la cita. Verifica los datos ingresados.")
    else:
        form = CitaForm()
    
    citas = Cita.objects.all().values(
    'id',
    'fecha_hora',
    'estado',
    'asunto',
    'estudiante__usuario__first_name',
    'estudiante__usuario__last_name'
    )
    citas_list = list(citas)
    bogota_tz = pytz.timezone('America/Bogota')


    for cita in citas_list:
        # Convertir datetime a la zona horaria de Bogotá
        fecha_hora_utc = cita['fecha_hora']
        if timezone.is_naive(fecha_hora_utc):
            fecha_hora_utc = timezone.make_aware(fecha_hora_utc)
            
        fecha_hora_bogota = fecha_hora_utc.astimezone(bogota_tz)
        cita['nombre_completo'] = f"{cita.pop('estudiante__usuario__first_name')} {cita.pop('estudiante__usuario__last_name')}"
        cita['fecha_hora'] = fecha_hora_bogota.isoformat()

    # Convertir fecha_hora a string ISO con zona horaria
    
        contactos = Contacto.objects.all().values(
            'nombre', 
            'deseo', 
            'fecha_creacion'
        )
    contactos_list = list(contactos)
    
    # Convertir datetime a string ISO
    for contacto in contactos_list:
        contacto['fecha_creacion'] = contacto['fecha_creacion'].isoformat()

    user = request.user
    context = {
        'user': user,
        'num_estudiantes': Estudiante.objects.count(),
        'num_citas_agendadas': Cita.objects.filter(estado='agendada').count(),
        'num_contactos': Contacto.objects.count(),
        'num_preguntas': Preguntas.objects.count(),
        'horarios': Horario.objects.all().order_by('dia_semana', 'hora_inicio'),
        'contactos': Contacto.objects.all(),
        'preguntas': Preguntas.objects.all(),
        'citas': Cita.objects.all(),
        'usuarios': UsuarioPersonalizado.objects.all(),
        'form': form,
        'dashboard_url': reverse('dashboard'),
        'contactos_json': contactos_list,
        'citas_json': citas_list,
        'conversion_rate': conversion_rate,
        'promedio_reseñas': promedio_reseñas,
        'porcentaje_satisfaccion': porcentaje_satisfaccion,
        'cantidad_reseñas': cantidad_reseñas,
        'porcentaje_cambio_citas': porcentaje_cambio_citas,  
        'notificaciones': notificaciones,
        'contador_notificaciones': notificaciones.count(),
        
        
    }
    
    return render(request, 'dashboard.html', context)



def verificar_email(request):
    email = request.GET.get('email', '')
    User = get_user_model()
    existe = User.objects.filter(email=email).exists()
    return JsonResponse({'existe': existe})


def verificar_username(request):
    username = request.GET.get('username', '')
    User = get_user_model()
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

def verificar_identificacion(request):
    identificacion = request.GET.get('identificacion', '')
    exists = UsuarioPersonalizado.objects.filter(identificacion=identificacion).exists()
    return JsonResponse({'exists': exists})

def usuarios(request):
    usuarios_list = list(UsuarioPersonalizado.objects.all())
    
    estudiantes = UsuarioPersonalizado.objects.filter(rol='estudiante')
    print(estudiantes)
    
    psicologos = Psicologo.objects.all()
    print(psicologos)

    # Formulario de creación
    creation_form = UsuarioPersonalizadoCreationForm()

    # Asignar el formulario de edición a cada usuario
    for usuario in usuarios_list:
        usuario.form_editar = UsuarioPersonalizadoEditForm(instance=usuario)

    return render(request, 'usuarios.html', {
        'usuarios': usuarios_list,
        'form': creation_form,  # Formulario de creación
    })
    


def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioPersonalizadoCreationForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Guardar el usuario usando el método save() del formulario
            nuevo_usuario = form.save()  # ¡commit=True por defecto!
            
            messages.success(request, 'Usuario creado exitosamente')
            return redirect('usuarios')
        else:
            messages.error(request, 'Corrige los errores en el formulario')
    else:
        form = UsuarioPersonalizadoCreationForm()
    
    return render(request, 'usuarios.html', {'form': form})


def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(UsuarioPersonalizado, id=usuario_id)
    
    if request.method == 'POST':
        form = UsuarioPersonalizadoEditForm(request.POST, request.FILES, instance=usuario)
        
        if form.is_valid():
            usuario_actualizado = form.save(commit=False)
            nuevo_rol = form.cleaned_data['rol']
            especializacion = form.cleaned_data.get('especializacion', '').strip()

            # Manejo explícito del psicólogo
            if nuevo_rol == 'psicologo':
                Psicologo.objects.update_or_create(
                    usuario=usuario_actualizado,
                    defaults={'especializacion': especializacion}
                )
            else:
                # Si el rol no es psicólogo, eliminamos cualquier registro de Psicologo asociado
                Psicologo.objects.filter(usuario=usuario_actualizado).delete()
            
            # Manejo explícito del estudiante
            if nuevo_rol == 'estudiante':
                # En este caso, el modelo Estudiante no tiene campos adicionales, por lo que se puede crear sin defaults
                Estudiante.objects.update_or_create(
                    usuario=usuario_actualizado,
                    defaults={}
                )
            else:
                # Si el rol no es estudiante, eliminamos el registro si existe
                Estudiante.objects.filter(usuario=usuario_actualizado).delete()
            
            usuario_actualizado.save()  # Guardar los cambios del usuario
            messages.success(request, '¡Usuario actualizado!')
            return redirect('usuarios')
        else:
            messages.error(request, 'Corrige los errores')
    else:
        form = UsuarioPersonalizadoEditForm(instance=usuario)
    
    return render(request, 'usuarios.html', {'form': form, 'usuario': usuario})

    
def eliminar_usuario(request, usuario_id):
    usuario = UsuarioPersonalizado.objects.get(pk=usuario_id)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado con éxito')
        return redirect('usuarios')
    return render(request, 'usuarios.html', {'usuario': usuario})


#perfil
def perfil(request):
    context = {'usuario': request.user}
    print( "hola", get_template('registration/password_change.html').origin)
    

    return render(request, 'perfil.html', context)


@never_cache
@login_required
def editar_perfil(request):
    usuario = request.user
    
    if request.method == 'POST':
        try:
            # Obtener nuevos valores del formulario
            nueva_identificacion = request.POST.get('identificacion')
            nuevo_email = request.POST.get('email', usuario.email)

            # Validar identificación única (excluyendo al usuario actual)
            if nueva_identificacion != usuario.identificacion:
                if UsuarioPersonalizado.objects.exclude(id=usuario.id).filter(identificacion=nueva_identificacion).exists():
                    messages.error(request, 'Esta identificación ya está registrada por otro usuario')
                    return redirect('editar_perfil')

            # Validar email único (excluyendo al usuario actual)
            if nuevo_email != usuario.email:
                if UsuarioPersonalizado.objects.exclude(id=usuario.id).filter(email=nuevo_email).exists():
                    messages.error(request, 'Este correo electrónico ya está registrado')
                    return redirect('editar_perfil')

            # Actualizar campos del usuario
            usuario.first_name = request.POST.get('first_name', usuario.first_name)
            usuario.last_name = request.POST.get('last_name', usuario.last_name)
            usuario.tipo_identificacion = request.POST.get('tipo_identificacion')
            usuario.identificacion = nueva_identificacion  # Usamos el valor ya validado
            usuario.eps = request.POST.get('eps', usuario.eps)
            usuario.alergias = request.POST.get('alergias', usuario.alergias)
            usuario.enfermedades = request.POST.get('enfermedades', usuario.enfermedades)
            usuario.email = nuevo_email  # Usamos el valor ya validado

            # Manejo de la imagen de perfil
            if 'imagen-clear' in request.POST:
                usuario.imagen.delete(save=True) 
            
            usuario.save()

            # Actualizar especialización para psicólogos
            if usuario.rol == 'psicologo':
                psicologo, created = Psicologo.objects.get_or_create(usuario=usuario)
                psicologo.especializacion = request.POST.get('especializacion')
                psicologo.save()
            
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('perfil')
        
        except IntegrityError as e:
            messages.error(request, 'Error al guardar los cambios')
            return redirect('editar_perfil')
    
    context = {
        'usuario': usuario,
        'psicologo': getattr(usuario, 'psicologo', None)
    }
    
    return render(request, 'perfil.html', context)
#login:

def login_vista(request):
    # Capturamos el parámetro 'next' tanto en GET como en POST
    next_url = request.GET.get('next') or request.POST.get('next') or '/dashboard/'
    
    if request.method == "POST":
        form = EmailAuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirige a la URL indicada en 'next'
            return redirect(next_url)
        else:
            messages.error(request, "El email o la contraseña son incorrectos")
    else: 
        form = EmailAuthenticationForm()

    return render(request, "login.html", {"form": form, "next": next_url})


def logout_vista(request):
    # Finaliza la sesión del usuario
    logout(request)
    print("El usuario ha cerrado sesión")
    
    return redirect('login')
    
#registro_estudiante


    

def registro_estudiante(request):
    # Por defecto, muestra el Paso 1
    step = 1

    if request.method == 'POST':
        estudiante_form = EstudianteForm(request.POST)
        
        # Si el usuario viene del botón "Siguiente Paso 2" o "Siguiente Paso 3"
        # (ver más abajo en el template los name="step" value="2" / "3")
        step = int(request.POST.get('step', 1))
        
        # Si el paso actual es 3 y se presionó "Crear cuenta", intentamos validar todo
        if step == 3:
            if estudiante_form.is_valid():
                estudiante_form.save()
                return redirect('dashboard')
            else:
                # Si hay errores en contraseña, forzamos a que se muestre step=3
                if estudiante_form.errors.get('password1') or estudiante_form.errors.get('password2'):
                    step = 3
                # Si hay errores en campos del Paso 2, volvemos al Paso 2
                elif any(field in estudiante_form.errors for field in [
                    'username','first_name','last_name','tipo_identificacion','identificacion'
                ]):
                    step = 2
                # Si hay errores en el email, volvemos al Paso 1
                elif estudiante_form.errors.get('email'):
                    step = 1
        else:
            # En pasos 1 o 2 podrías hacer validaciones parciales, 
            # o simplemente dejar que el usuario pase y al final se valide todo en step=3.
            # Si quieres validación parcial, puedes hacer algo como:
            
            if estudiante_form.is_valid():
                # Si no hay errores, avanzamos de paso
                step += 1
            else:
                # Dependiendo de qué campos fallan, retrocedes al paso que corresponda
                if any(field in estudiante_form.errors for field in ['email']):
                    step = 1
                elif any(field in estudiante_form.errors for field in [
                    'username','first_name','last_name','tipo_identificacion','identificacion'
                ]):
                    step = 2
                # Y si las contraseñas fallan (raro que pase en step 1/2, pero por si acaso)
                elif estudiante_form.errors.get('password1') or estudiante_form.errors.get('password2'):
                    step = 3

    else:
        # Si es GET, sólo inicializa el formulario
        estudiante_form = EstudianteForm()

    return render(request, 'registro_estudiante.html', {
        'estudiante_form': estudiante_form,
        'step': step
    })

    

#horarios

def horarios(request):
    horarios_list = list(Horario.objects.all())

    # Formulario de creación
    creation_form = HorarioForm()

    # Asignar el formulario de edición a cada horario
    for horario in horarios_list:
        horario.form_editar = HorarioForm(instance=horario)

    return render(request, 'horarios.html', {
        'horarios': horarios_list,
        'form': creation_form,  # Formulario de creación
    })

def crear_editar_horario(request, horario_id):
    """
    Si horario_id == 0: se crea un nuevo Horario.
    Si horario_id != 0: se edita el Horario correspondiente.
    """
    if horario_id == 0:
        horario_instance = None
    else:
        horario_instance = get_object_or_404(Horario, id=horario_id)
    
    if request.method == 'POST':
        form = HorarioForm(request.POST, instance=horario_instance)
        if form.is_valid():
            form.save()
            if horario_id == 0:
                messages.success(request, "¡Horario creado correctamente!")
            else:
                messages.success(request, "¡Horario editado correctamente!")
        else:
            messages.error(request, "Hubo un error al guardar el horario. Verifica los datos ingresados.")
        
        return redirect('horarios')  # Asegúrate de que 'horarios' sea el nombre correcto en tus URLs
    else:
        return redirect('horarios')
    
    
def eliminar_horario(request, horario_id):
    horario = Horario.objects.get(pk=horario_id)
    if request.method == 'POST':
        horario.delete()
        messages.success(request, 'Horario eliminado con éxito')
        return redirect('horarios')
    return render(request, 'horarios.html', {'horario': horario})


    


#horarios
def horarios(request):
    horarios_list = list(Horario.objects.all())
    
    # Formulario de creación
    creation_form = HorarioForm()
    
    # Asignar el formulario de edición a cada horario
    for horario in horarios_list:
        horario.form_editar = HorarioForm(instance=horario)
    
    return render(request, 'horarios.html', {
        'horarios': horarios_list,
        'form': creation_form,  # Formulario de creación
    })
#preguntas
def preguntas_tabla(request):
    preguntas_list = list(Preguntas.objects.all())  # Asegúrate de que cada objeto Preguntas tenga un ID válido.

    # Formulario de creación
    creation_form = PreguntasForm()

    # Asignar el formulario de edición a cada pregunta
    for pregunta in preguntas_list:
        pregunta.form_editar = PreguntasForm(instance=pregunta)

    return render(request, 'preguntas_tabla.html', {
        'preguntas': preguntas_list,
        'form': creation_form,  # Formulario de creación
    })


def crear_editar_pregunta(request, pregunta_id):
    """
    Si pregunta_id == 0: se crea una nueva Pregunta.
    Si pregunta_id != 0: se edita la Pregunta correspondiente.
    """
    if pregunta_id == 0:
        pregunta_instance = None
    else:
        pregunta_instance = get_object_or_404(Preguntas, id_pregunta=pregunta_id)
 
    
    if request.method == 'POST':
        form = PreguntasForm(request.POST, instance=pregunta_instance)
        if form.is_valid():
            form.save()
            if pregunta_id == 0:
                messages.success(request, "¡Pregunta creada correctamente!")
            else:
                messages.success(request, "¡Pregunta editada correctamente!")
        else:
            messages.error(request, "Hubo un error al guardar la pregunta. Verifica los datos ingresados.")
        
        return redirect('preguntas_tabla')  
    else:
        return redirect('preguntas_tabla')
    
    

def eliminar_pregunta(request, pregunta_id):
    pregunta = get_object_or_404(Preguntas, id_pregunta=pregunta_id)
    if request.method == 'POST':
        pregunta.delete()
        messages.success(request, 'Pregunta eliminada con éxito')
        return redirect('preguntas_tabla')
    return render(request, 'preguntas_tabla.html', {'pregunta': pregunta})


#buzon:
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




#citas:

class CitaCreateView(CreateView):
    model = Cita
    form_class = CitaForm
    template_name = "citas.html"
    success_url = reverse_lazy("citas")

    def form_valid(self, form):
        # Obtén el valor de la fecha/hora ingresado en el formulario
        fecha_hora = form.instance.fecha_hora
        # Si la fecha/hora es naive (sin información de zona horaria), la hacemos "aware"
        if fecha_hora and timezone.is_naive(fecha_hora):
            # Esto utiliza la zona horaria configurada en settings (America/Bogota)
            form.instance.fecha_hora = timezone.make_aware(fecha_hora, timezone.get_current_timezone())
        
        messages.success(self.request, "¡Cita creada correctamente!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Hubo un error al crear la cita. Verifica los datos ingresados.")
        return super().form_invalid(form)
    
class CitaListView(ListView):
    model = Cita
    template_name = "citas.html"  # Plantilla para listar las citas
    context_object_name = "citas"
    ordering = ['-fecha_hora']  
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Formulario para la creación de una nueva cita
        context['form'] = CitaForm()
        # Para cada cita en la lista, asignamos un formulario de edición
        for cita in context['citas']:
            cita.form_editar = CitaForm(instance=cita)
        # Agregar la URL para crear cita
        context['crear_cita_url'] = reverse('crear_cita')
        return context

    


class CitaUpdateView(UpdateView):
    model = Cita
    form_class = CitaForm
    template_name = "citas.html"  
    success_url = reverse_lazy("citas")

    def form_valid(self, form):
        # Obtener instancia antes de guardar cambios
        old_estado = self.get_object().estado
        new_estado = form.cleaned_data.get('estado')

        response = super().form_valid(form)
        
        # Solo si cambió el estado
        if old_estado != new_estado:
            cita = self.object
            
            # Enviar correo de cancelación
            if new_estado == 'cancelada':
                self.enviar_correo_cancelacion(cita)
                
            # Enviar correo de completado con enlace
            elif new_estado == 'completada':
                self.enviar_correo_completada(cita)

        messages.success(self.request, "¡Cita editada correctamente!")
        return response

    def enviar_correo_cancelacion(self, cita):
        context = {
            'nombre_paciente': cita.estudiante.usuario.first_name,
            'nombre_psicologo': cita.psicologo.usuario.get_full_name(),
            'fecha_cita': cita.fecha_hora.strftime('%d/%m/%Y'),
            'hora_cita': cita.fecha_hora.strftime('%H:%M'),
            'citas_url': self.request.build_absolute_uri(reverse('citas'))
        }
        
        html_content = render_to_string('cita_cancelada.html', context)
        
        msg = EmailMultiAlternatives(
            subject="Tu cita ha sido cancelada ❌",
            body=html_content,  # Versión texto plano opcional
            from_email='puntomentalcosfacali@gmail.com',
            to=[cita.estudiante.usuario.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def enviar_correo_completada(self, cita):
        serializer = URLSafeSerializer(settings.SECRET_KEY)
        token = serializer.dumps(cita.id)

        print(f"\n--- DEBUG GENERACIÓN TOKEN ---")
        print(f"Cita ID: {cita.id} (tipo: {type(cita.id)})")
        print(f"Token generado: {token}")

        
        context = {
            'nombre_paciente': cita.estudiante.usuario.first_name,
            'nombre_psicologo': cita.psicologo.usuario.get_full_name(),
            'fecha_cita': cita.fecha_hora.strftime('%d/%m/%Y'),
            'enlace_review': self.request.build_absolute_uri(
                reverse('crear_review', kwargs={'token': token})
            )
            }
        
        html_content = render_to_string('cita_completada.html', context)
        
        msg = EmailMultiAlternatives(
            subject="¡Califica tu sesión ⭐",
            body=html_content,
            from_email='puntomentalcosfacali@gmail.com',
            to=[cita.estudiante.usuario.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        


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
    
    