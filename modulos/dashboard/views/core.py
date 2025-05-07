import pytz
from django.urls import reverse
from .base_importaciones import (
    login_required, never_cache, messages, redirect, render,
    Q, Avg, CitaForm, Notificacion, Cita, Review, Preguntas,
    Horario, Contacto, Estudiante, UsuarioPersonalizado, timezone, Respuesta
)

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
    

    respuestas = Respuesta.objects.filter(calificacion__gte=4.5).order_by('-id_respuesta')
    # Cálculo de reseñas
    reseñas = Review.objects.all()
    cantidad_reseñas = reseñas.count()
    promedio_reseñas = reseñas.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
    porcentaje_satisfaccion = (promedio_reseñas / 5) * 100  # Convertir a porcentaje
    porcentaje_cambio_citas = 7  
    
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
    
  
    
    
    if request.user.rol == 'estudiante':
    # Obtener el estudiante asociado al usuario
        estudiante = Estudiante.objects.get(usuario=request.user)
        review_estudiante = Review.objects.filter(estudiante=estudiante).count()

        citas = Cita.objects.filter(estudiante=estudiante)
    else:
        citas = Cita.objects.all()

    citas = citas.values(
        'id',
        'fecha_hora',
        'estado',
        'asunto',
        'psicologo__usuario__first_name',  # Añadir datos del psicólogo
        'psicologo__usuario__last_name',
        'psicologo__usuario__imagen',
    
        'estudiante__usuario__first_name',
        'estudiante__usuario__last_name'
    )
        

    citas = citas.order_by('fecha_hora') 
    citas_list = list(citas)
    bogota_tz = pytz.timezone('America/Bogota')
    
    # Corregir la identación y procesamiento de datos de citas
    for cita in citas_list:
        # Convertir datetime a la zona horaria de Bogotá
        fecha_hora_utc = cita['fecha_hora']
        if timezone.is_naive(fecha_hora_utc):
            fecha_hora_utc = timezone.make_aware(fecha_hora_utc)
            
        fecha_hora_bogota = fecha_hora_utc.astimezone(bogota_tz)
        
        # Extraer nombres correctamente
        cita['psicologo_nombre'] = (
            f"{cita.pop('psicologo__usuario__first_name', '')} "
            f"{cita.pop('psicologo__usuario__last_name', '')}"
        ).strip()
        
        cita['estudiante_nombre'] = (
            f"{cita.pop('estudiante__usuario__first_name', '')} "
            f"{cita.pop('estudiante__usuario__last_name', '')}"
        ).strip()
        
        # Guardar la imagen y convertir la fecha
        cita['psicologo_imagen'] = cita.pop('psicologo__usuario__imagen', None)
        cita['fecha_hora'] = fecha_hora_bogota


    # Convertir fecha_hora a string ISO con zona horaria
    
   
    
    
    if request.user.rol == 'estudiante':
        estudiante = Estudiante.objects.get(usuario=request.user)
        
        qs_contactos = Contacto.objects.filter(email=request.user.email)
    else:
        qs_contactos = Contacto.objects.all()
        
        
    contactos_list = list(
    qs_contactos.values(
        'nombre',
        'deseo',
        'mensaje',
        'fecha_creacion',
        'estado'
    )
)
        
   

        
    num_contactos_pendientes = Contacto.objects.filter(estado='pendiente').count()
    
        
    
  

    user = request.user

    if request.user.rol == 'estudiante':
        notificaciones = Notificacion.objects.filter(
            Q(usuario=request.user) | Q(destinatario_tipo='todos'),
            leida=False
        ).order_by('-fecha_creacion')[:5]
    else:
        notificaciones = Notificacion.objects.filter(
            Q(destinatario_tipo=request.user.rol) | Q(destinatario_tipo='todos'),
            leida=False
        ).order_by('-fecha_creacion')[:5]


    
        
        
        
    context = {
        'user': user,
        'num_estudiantes': Estudiante.objects.count(),
        'num_citas_agendadas': Cita.objects.filter(estado='agendada').count(),
        'num_citas_agendadas_estudiante': Cita.objects.filter(estado='agendada', estudiante__usuario=user).count(),
       'num_contactos_pendientes_estudiante':
    (Contacto.objects.filter(usuario=request.user) if request.user.rol=='estudiante'
     else Contacto.objects.all()
    ).filter(estado='pendiente').count(),
        'num_rewiews_estudiante': review_estudiante,
        'num_contactos': Contacto.objects.count(),
        'num_contactos_pendientes': num_contactos_pendientes,
        'num_preguntas': Preguntas.objects.count(),
        'horarios': Horario.objects.all().order_by('dia_semana', 'hora_inicio'),
        'contactos': qs_contactos,                
        'preguntas': Preguntas.objects.all(),
        'citas': citas_list,
        'usuarios': UsuarioPersonalizado.objects.all(),
        'notas': Respuesta.objects.filter(usuario=user),
        'form': form,
        'dashboard_url': reverse('dashboard'),
        'contactos_json': contactos_list,
        'citas_json': citas_list,
        'active_page': 'inicio',  
        'conversion_rate': conversion_rate,
        'promedio_reseñas': promedio_reseñas,
        'porcentaje_satisfaccion': porcentaje_satisfaccion,
        'cantidad_reseñas': cantidad_reseñas,
        'porcentaje_cambio_citas': porcentaje_cambio_citas,  
        'notificaciones': notificaciones,
        'contador_notificaciones': notificaciones.count(),
        'respuesta': Respuesta
        
        
    }
    
    return render(request, 'dashboard.html', context)
    
    