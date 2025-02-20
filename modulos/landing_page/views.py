from django.shortcuts import render, redirect
from modulos.dashboard.models import Preguntas, Horario, Psicologo, Cita, Estudiante, UsuarioPersonalizado
from datetime import timedelta, datetime
from .forms import EstudianteForm
from django.http import JsonResponse
from datetime import timedelta
from django.utils import timezone
import pytz
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# Create your views here.

def blog(request):
    
    return render(request, 'blog.html')

def preguntas(request):
    
    preguntas = Preguntas.objects.all()
    return render(request, 'preguntas.html', {'preguntas': preguntas})



def validar_pregunta(request):
    if request.method == 'POST':
        preguntas = Preguntas.objects.all()
        respuestas_correctas = 0
        total_preguntas = preguntas.count()

        for pregunta in preguntas:
            respuesta_usuario = request.POST.get(f"respuesta_{pregunta.id_pregunta}")

            if respuesta_usuario:
                if respuesta_usuario == 'True' and pregunta.respuesta:
                    respuestas_correctas += 1
                elif respuesta_usuario == 'False' and not pregunta.respuesta:
                    respuestas_correctas += 1

        # Calculamos el porcentaje de respuestas correctas
        porcentaje = (respuestas_correctas / total_preguntas) * 100

        # Mostrar los resultados en la consola (para depuración)
        print(f"respuestas correctas: {respuestas_correctas}")
        print(f"total preguntas: {total_preguntas}")
        print(f"porcentaje: {porcentaje}")

        return render(request, 'preguntas.html', {'preguntas': preguntas, 
                                                  'respuestas_correctas': respuestas_correctas, 
                                                  'total_preguntas': total_preguntas, 
                                                  'porcentaje': porcentaje})  
    else:
        return redirect('preguntas')  
    
    
    

def generar_intervalos(hora_inicio, hora_fin):
    intervalos = []
    hora_actual = datetime.combine(datetime.today(), hora_inicio)  # Corregido
    hora_limite = datetime.combine(datetime.today(), hora_fin)  # Corregido
 # Cambiado a datetime.datetime

    while hora_actual <= hora_limite:
        intervalos.append(hora_actual.time())  # Solo guardar la parte de la hora, sin la fecha
        hora_actual += timedelta(hours=1)  # Incrementar en 1 hora

    return intervalos

def index(request):
    psicologos = Psicologo.objects.prefetch_related('horarios').all()
    estudiante_form = EstudianteForm()  # Cambio de nombre
    psicologos_con_horarios = []
    for psicologo in psicologos:
        horarios_con_intervalos = []
        dias_disponibles = set()
        for horario in psicologo.horarios.all():
            if horario.disponible:
                dias_disponibles.add(horario.dia_semana)
                intervalos = generar_intervalos(horario.hora_inicio, horario.hora_fin)
                horarios_con_intervalos.append({
                    'horario': horario,
                    'intervalos': intervalos
                })
        psicologos_con_horarios.append({
            'psicologo': psicologo,
            'horarios_con_intervalos': horarios_con_intervalos,
            'dias_disponibles': list(dias_disponibles)  # Ej: ['Miércoles', 'Viernes']
        })

    context = {
        'psicologos_con_horarios': psicologos_con_horarios,
        'estudiante_form': estudiante_form  # Actualización en el contexto
    }
    return render(request, 'index.html', context)


    
    

def obtener_horarios_disponibles(request):
    psicologo_id = request.GET.get('psicologo_id')
    dia = request.GET.get('dia')
    
    horarios = Horario.objects.filter(psicologo_id=psicologo_id, dia_semana=dia, disponible=True)
    
    horarios_json = [{'hora_inicio': str(h.hora_inicio), 'hora_fin': str(h.hora_fin)} for h in horarios]
    
    return JsonResponse({'horarios': horarios_json})


def agendar_cita(request):
    if request.method == 'POST':
        # Extrae datos de los campos ocultos y otros necesarios
        selected_date = request.POST.get('selected_date')  # ej. "2025-02-20"
        selected_time = request.POST.get('selected_time')  # ej. "07:00 AM"
        psicologo_id = request.POST.get('psicologo_id')
        email = request.POST.get('email')  # Se debe enviar en el formulario

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

        # Obtén el psicólogo; si no se encuentra, retorna error
        try:
            psicologo = Psicologo.objects.get(pk=psicologo_id)
        except Psicologo.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Psicólogo no encontrado.'})

        # Verifica si existe una cita en el intervalo seleccionado
        cita_existente = Cita.objects.filter(
            psicologo=psicologo,
            fecha_hora__gte=fecha_hora_cita,
            fecha_hora__lt=fecha_hora_cita + timedelta(minutes=60),
            estado='agendada'
        ).exists()

        if cita_existente:
            return JsonResponse({'success': False, 'error': 'El horario seleccionado ya está ocupado.'})

        # Verifica si el usuario ya está registrado (por ejemplo, mediante el email)
        try:
            usuario = UsuarioPersonalizado.objects.get(email=email)
            # Asume que ya existe un estudiante relacionado a ese usuario
            estudiante = Estudiante.objects.get(usuario=usuario)
        except UsuarioPersonalizado.DoesNotExist:
            # Si el usuario no existe, procesa el formulario de registro
            form = EstudianteForm(request.POST)
            if form.is_valid():
                usuario = form.save()  # Esto guarda el usuario con rol "estudiante"
                estudiante = Estudiante.objects.create(usuario=usuario)
            else:
                print("Errores en el formulario:", form.errors)
                return JsonResponse({
                    'success': False,
                    'error': 'Datos inválidos',
                    'errors': form.errors,
                })
        except Estudiante.DoesNotExist:
            # Si el usuario existe pero no hay estudiante, lo crea
            estudiante = Estudiante.objects.create(usuario=usuario)

        # Define el asunto y recoge comentarios (puedes obtenerlos de request.POST o del form)
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

        # Construir el contexto para la plantilla del correo de confirmación
        context = {
            'nombre_paciente': usuario.first_name or usuario.username,
            'nombre_psicologo': cita.psicologo.usuario.username,
            'fecha_cita': timezone.localtime(cita.fecha_hora).strftime('%A %d de %B de %Y, %H:%M'),
            'direccion': 'Calle 54 #11d-44, Comuna 8, Cali, Valle del Cauca, Colombia',
            'enlace_modificar': 'https://tusitio.com/modificar-cita/',
            'comentarios': cita.notas,
        }

        # Renderizar la plantilla HTML del correo
        html_content = render_to_string('cita_confirmacion.html', context)
        text_content = strip_tags(html_content)

        subject = "Confirmación de tu cita"
        from_email = "puntomentalcosfacali@gmail.com"  # O settings.DEFAULT_FROM_EMAIL
        recipient_list = [usuario.email]

        msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        # Retorna la respuesta JSON de confirmación
        response_data = {
            'success': True,
            'psychologist': cita.psicologo.usuario.username,
            'datetime': timezone.localtime(cita.fecha_hora).strftime('%A %d de %B a las %H:%M').capitalize(),
            'email': usuario.email,
        }
        return JsonResponse(response_data)
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

