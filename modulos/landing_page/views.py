import json
from django.shortcuts import render, redirect
from modulos.dashboard.models import Preguntas, Horario, Psicologo, Cita, Estudiante, UsuarioPersonalizado, Contacto, Respuesta
from datetime import timedelta, datetime
from .forms import EstudianteForm, ContactoForm
from django.http import JsonResponse
from datetime import timedelta
from django.utils import timezone
import pytz
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, get_user_model, logout
from .envio import enviar_correo_confirmacion

# Create your views here.

def blog(request):
    
    return render(request, 'blog.html')
def preguntas(request):
    if not request.user.is_authenticated:
        return redirect(f'/login/?next={request.path}')
    
    preguntas_list = list(Preguntas.objects.all().order_by('id_pregunta'))
    total = len(preguntas_list)
    current_index = request.session.get('current_index', 0)

    if current_index >= total:
        respuestas_correctas = request.session.get('respuestas_correctas', 0)
        porcentaje = (respuestas_correctas / total) * 100 if total > 0 else 0

        # Mapear el porcentaje a una calificación de 1 a 5 y asignar la nota correspondiente
        if porcentaje >= 90:
            nota = "Excelente"
            calificacion = 5
        elif porcentaje >= 70:
            nota = "Muy Bien"
            calificacion = 4
        elif porcentaje >= 50:
            nota = "Regular"
            calificacion = 3
        elif porcentaje >= 30:
            nota = "Necesita mejorar"
            calificacion = 2
        else:
            nota = "Insuficiente"
            calificacion = 1

        # Guarda la respuesta en el modelo Respuesta
        Respuesta.objects.create(
            usuario=request.user,
            calificacion=calificacion,
            nota=nota
        )

        # Reinicia el contador de sesión para un nuevo intento
        request.session['current_index'] = 0
        request.session['respuestas_correctas'] = 0

        return render(request, 'resultados.html', {
            'respuestas_correctas': respuestas_correctas,
            'total_preguntas': total,
            'porcentaje': porcentaje
        })

    pregunta_actual = preguntas_list[current_index]
    return render(request, 'preguntas.html', {
        'pregunta': pregunta_actual,
        'current_index': current_index,
        'total': total
    })




def validar_pregunta(request):
    if request.method == 'POST':
        preguntas_list = list(Preguntas.objects.all().order_by('id_pregunta'))
        total = len(preguntas_list)

        # Recuperamos el índice actual y la cantidad de respuestas correctas desde la sesión
        current_index = request.session.get('current_index', 0)
        respuestas_correctas = request.session.get('respuestas_correctas', 0)

        # Obtenemos la pregunta actual
        if current_index < total:
            pregunta_actual = preguntas_list[current_index]
            # El nombre del input se genera con el id de la pregunta, por ejemplo: respuesta_1, respuesta_2, etc.
            respuesta_usuario = request.POST.get(f"respuesta_{pregunta_actual.id_pregunta}")

            if respuesta_usuario:
                # Comparamos la respuesta enviada con la respuesta correcta almacenada en la pregunta
                if respuesta_usuario == 'True' and pregunta_actual.respuesta:
                    respuestas_correctas += 1
                elif respuesta_usuario == 'False' and not pregunta_actual.respuesta:
                    respuestas_correctas += 1

        # Actualizamos la sesión: aumentamos el índice y guardamos la cantidad de respuestas correctas
        request.session['current_index'] = current_index + 1
        request.session['respuestas_correctas'] = respuestas_correctas

    return redirect('preguntas')  
    


def resultados(request):
    
    
    return render(request, 'resultados.html')
    
    

def generar_intervalos(hora_inicio, hora_fin):
    intervalos = []
    hora_actual = datetime.combine(datetime.today(), hora_inicio)  # Corregido
    hora_limite = datetime.combine(datetime.today(), hora_fin)  # Corregido
 # Cambiado a datetime.datetime

    while hora_actual <= hora_limite:
        intervalos.append(hora_actual.time())  # Solo guardar la parte de la hora, sin la fecha
        hora_actual += timedelta(hours=1)  # Incrementar en 1 hora

    return intervalos


def obtener_horarios_disponibles(request):
    psicologo_id = request.GET.get('psicologo_id')
    dia = request.GET.get('dia')
    
    horarios = Horario.objects.filter(psicologo_id=psicologo_id, dia_semana=dia, disponible=True)
    
    horarios_json = [{'hora_inicio': str(h.hora_inicio), 'hora_fin': str(h.hora_fin)} for h in horarios]
    
    return JsonResponse({'horarios': horarios_json})

def index(request):
    psicologos = Psicologo.objects.prefetch_related('horarios').all()
    estudiante_form = EstudianteForm()
    contact_form=ContactoForm()
    psicologos_con_horarios = []
    for psicologo in psicologos:
        horarios_con_intervalos = []
        dias_disponibles = set()
        for horario in psicologo.horarios.all():
            if horario.disponible:
                dias_disponibles.add(horario.dia_semana)
                print(">>> Generando intervalos para:", horario.dia_semana, 
                      "hora_inicio =", horario.hora_inicio, 
                      "hora_fin =", horario.hora_fin)
                
                intervalos = generar_intervalos(horario.hora_inicio, horario.hora_fin)
                print(">>> Intervalos obtenidos:", intervalos)
                
                horarios_con_intervalos.append({
                    'horario': horario,
                    'intervalos': intervalos
                })
        psicologos_con_horarios.append({
            'psicologo': psicologo,
            'horarios_con_intervalos': horarios_con_intervalos,
            'dias_disponibles': list(dias_disponibles),
    
        })

    context = {
        'psicologos_con_horarios': psicologos_con_horarios,
        'estudiante_form': estudiante_form,
        "contact_form": contact_form
    }
    return render(request, 'index.html', context)





def verificar_usuario(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            if not email:
                return JsonResponse({'exists': False, 'error': 'No se proporcionó correo.'}, status=400)
        except Exception:
            return JsonResponse({'exists': False, 'error': 'Solicitud inválida.'}, status=400)
        
        try:
            usuario = UsuarioPersonalizado.objects.get(email=email)
            # Envía los datos que quieras usar para precargar el formulario
            user_data = {
                 'first_name': usuario.first_name,
                'last_name': usuario.last_name,
                'username': usuario.username,
                'tipo_identificacion': usuario.tipo_identificacion,
                'identificacion': usuario.identificacion,
                'eps': usuario.eps,
                'alergias': usuario.alergias,
                'enfermedades': usuario.enfermedades,
                'email': usuario.email,
                
            }
            return JsonResponse({'exists': True, 'user_data': user_data})
        except UsuarioPersonalizado.DoesNotExist:
            return JsonResponse({'exists': False})
    
    return JsonResponse({'error': 'Método no permitido.'}, status=405)



def agendar_cita(request):
    if request.method == 'POST':
        # Extrae datos de los campos ocultos y otros necesarios
        selected_date = request.POST.get('selected_date')  # ej. "2025-02-20"
        selected_time = request.POST.get('selected_time')  # ej. "07:00 AM"
        psicologo_id = request.POST.get('psicologo_id')
        email = request.POST.get('email')  # El correo ya se habrá precargado si el usuario existe

        # Convierte la hora seleccionada en un objeto datetime
        time_part, period = selected_time.strip().split()
        hours, minutes = map(int, time_part.split(':'))
        if period == 'PM' and hours != 12:
            hours += 12
        elif period == 'AM' and hours == 12:
            hours = 0

        datetime_str = f"{selected_date} {hours:02d}:{minutes}"
        fecha_hora_cita = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        tz = pytz.timezone('America/Bogota')
        fecha_hora_cita = tz.localize(fecha_hora_cita)

        # Obtiene el psicólogo; si no se encuentra, retorna error
        try:
            psicologo = Psicologo.objects.get(pk=psicologo_id)
        except Psicologo.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Psicólogo no encontrado.'})

        # Verifica si ya existe una cita en el intervalo seleccionado
        cita_existente = Cita.objects.filter(
            psicologo=psicologo,
            fecha_hora__gte=fecha_hora_cita,
            fecha_hora__lt=fecha_hora_cita + timedelta(minutes=60),
            estado='agendada'
        ).exists()
        if cita_existente:
            return JsonResponse({'success': False, 'error': 'El horario seleccionado ya está ocupado.'})

        # Verifica si el usuario ya está registrado (por su correo)
        try:
            usuario = UsuarioPersonalizado.objects.get(email=email)
            estudiante = Estudiante.objects.get(usuario=usuario)
        except UsuarioPersonalizado.DoesNotExist:
            # Usuario nuevo: se procesa el formulario de registro completo
            form = EstudianteForm(request.POST)
            if form.is_valid():
                usuario = form.save()  # Crea el usuario con rol "estudiante"
                estudiante = Estudiante.objects.create(usuario=usuario)
            else:
                print("Errores en el formulario:", form.errors)
                return JsonResponse({
                    'success': False,
                    'error': 'Datos inválidos',
                    'errors': form.errors,
                })
        except Estudiante.DoesNotExist:
            # Si el usuario existe pero no tiene un registro de estudiante, se crea
            estudiante = Estudiante.objects.create(usuario=usuario)

        # Define el asunto y recoge comentarios
        asunto = "Consulta de Psicología"
        comentarios = request.POST.get('comentarios', '')

        # Crea la cita
        cita = Cita.objects.create(
            fecha_hora=fecha_hora_cita,
            estudiante=estudiante,
            psicologo=psicologo,
            asunto=asunto,
            estado='agendada',
            notas=comentarios
        )

        # Construye el contexto para el correo de confirmación
        context = {
            'nombre_paciente': usuario.first_name or usuario.username,
            'nombre_psicologo': cita.psicologo.usuario.username,
            'fecha_cita': timezone.localtime(cita.fecha_hora).strftime('%A %d de %B de %Y, %H:%M'),
            'direccion': 'Calle 54 #11d-44, Comuna 8, Cali, Valle del Cauca, Colombia',
            'enlace_modificar': 'https://tusitio.com/modificar-cita/',
            'comentarios': cita.notas,
        }
        enviar_correo_confirmacion.delay(context, usuario.email)

        # Retorna la respuesta JSON de confirmación
        response_data = {
            'success': True,
            'psychologist': cita.psicologo.usuario.username,
            'datetime': timezone.localtime(cita.fecha_hora).strftime('%A %d de %B a las %H:%M').capitalize(),
            'email': usuario.email,
        }
        return JsonResponse(response_data)
    return JsonResponse({'success': False, 'error': 'Método no permitido'})




def procesar_contacto(request):
    if request.method == 'POST':
        contact_form = ContactoForm(request.POST)
        if contact_form.is_valid():
            # Extraer datos del formulario
            nombre = contact_form.cleaned_data.get('nombre')
            email = contact_form.cleaned_data.get('email')
            deseo = contact_form.cleaned_data.get('deseo')
            mensaje = contact_form.cleaned_data.get('mensaje')

            User = get_user_model()
            email = contact_form.cleaned_data['email']

            try:
                usuario = User.objects.get(email=email)
                Contacto.usuario = usuario
            except User.DoesNotExist:
                pass

            # Contexto para renderizar el template del correo
            context = {
                'nombre': nombre,
                'email': email,
                'deseo': deseo,
                'mensaje': mensaje,
            }

            # Asunto y direcciones
            subject = f"Nuevo mensaje de contacto: {deseo}"
            from_email = "puntomentalcosfacali@gmail.com"  # O settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]  # Asegúrate de tener configurado DEFAULT_FROM_EMAIL
            

            # Renderizar el contenido HTML usando el template 'emails/contacto_email.html'
            html_content = render_to_string('contacto_email.html', context)
            # También se puede definir una versión en texto plano
            text_content = f"Nombre: {nombre}\nEmail: {email}\nTipo de solicitud: {deseo}\nMensaje:\n{mensaje}"

            # Crear el mensaje y adjuntar la versión HTML
            msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            # Opcional: guardar el formulario en la base de datos
            contact_form.save()

            # Redireccionar a una página de éxito o mostrar un mensaje
            return redirect('index')  # Asegúrate de tener configurada esta URL
    else:
        contact_form = ContactoForm()

    return render(request, 'index.html', {'contact_form': contact_form})

