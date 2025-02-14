from django.shortcuts import render, redirect
from modulos.dashboard.models import Preguntas, Horario, Psicologo, Cita
from datetime import timedelta, datetime
from django.http import JsonResponse
from datetime import timedelta
import datetime  # Cambiamos esto para usar el módulo completo


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
    hora_actual = datetime.datetime.combine(datetime.datetime.today(), hora_inicio)  # Cambiado a datetime.datetime
    hora_limite = datetime.datetime.combine(datetime.datetime.today(), hora_fin)  # Cambiado a datetime.datetime

    while hora_actual <= hora_limite:
        intervalos.append(hora_actual.time())  # Solo guardar la parte de la hora, sin la fecha
        hora_actual += timedelta(hours=1)  # Incrementar en 1 hora

    return intervalos

def index(request):
    psicologos = Psicologo.objects.prefetch_related('horarios').all()  # prefetch de horarios
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
        'psicologos_con_horarios': psicologos_con_horarios
    }
    return render(request, 'index.html', context)

    
    
def agendar_cita(request):
    psicologos = Psicologo.objects.all()  # Obtener todos los psicólogos

    if request.method == 'POST':
        # Procesar el formulario cuando el usuario seleccione un horario y envíe la cita
        psicologo_id = request.POST.get('psicologo')
        dia = request.POST.get('dia')
        hora = request.POST.get('hora')
        psicologo = Psicologo.objects.get(id=psicologo_id)
        
        # Crear la cita en el horario seleccionado
        cita = Cita.objects.create(
            estudiante=request.user.estudiante,  # Suponiendo que el usuario logueado es un estudiante
            psicologo=psicologo,
            fecha_hora=f"{dia} {hora}",
            asunto="Asunto de la sesión"  # Podrías obtener esto también desde el formulario
        )
        cita.save()

        # Redirigir o enviar un mensaje de éxito
        return redirect('citas_confirmadas')  # Redirigir a una vista de confirmación o lista de citas

    return render(request, 'agendar_cita.html', {'psicologos': psicologos})


def obtener_horarios_disponibles(request):
    psicologo_id = request.GET.get('psicologo_id')
    dia = request.GET.get('dia')
    
    horarios = Horario.objects.filter(psicologo_id=psicologo_id, dia_semana=dia, disponible=True)
    
    horarios_json = [{'hora_inicio': str(h.hora_inicio), 'hora_fin': str(h.hora_fin)} for h in horarios]
    
    return JsonResponse({'horarios': horarios_json})