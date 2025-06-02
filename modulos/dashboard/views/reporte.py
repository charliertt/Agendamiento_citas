# En tu_app/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required #, user_passes_test (para verificaciones de rol)
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from weasyprint import HTML, CSS # Para generación de PDF
from django.conf import settings # Para archivos estáticos en PDF si es necesario
import os # Para unir rutas



from .base_importaciones import (
    messages,  timezone, CitaForm, Cita,  EmailMultiAlternatives,
    Cita, HistorialClinico, Estudiante, HistorialClinicoForm
)


# Función auxiliar para verificación de rol (opcional, puedes hacerlo directamente en las vistas)
def es_psicologo(user):
    return user.is_authenticated and user.rol == 'psicologo' #

@login_required
def crear_editar_historial_clinico(request, cita_id, historial_id=None):
    cita = get_object_or_404(Cita, id=cita_id, estado='completada') #
    
    # Asegurar que el usuario logueado es el psicólogo asociado con la cita
    if not (es_psicologo(request.user) and request.user.psicologo == cita.psicologo): #
        # messages.error(request, "No tiene permiso para editar este historial.")
        return redirect('dashboard') # Reemplaza con tu redirección deseada

    if historial_id:
        historial = get_object_or_404(HistorialClinico, id=historial_id, cita=cita)
        form_title = "Editar Historial Clínico"
    else:
        # Verificar si ya existe un historial para esta cita para prevenir duplicados mediante manipulación de URL
        existing_historial = HistorialClinico.objects.filter(cita=cita).first()
        if existing_historial:
            historial = existing_historial
            form_title = "Editar Historial Clínico"
        else:
            historial = HistorialClinico(cita=cita) # Pre-asociar con la cita
            form_title = "Crear Nuevo Historial Clínico"

    if request.method == 'POST':
        form = HistorialClinicoForm(request.POST, instance=historial)
        if form.is_valid():
            historial_guardado = form.save(commit=False)
            # El campo 'cita' ya está establecido si se está creando o se recuperó correctamente si se está editando.
            # No es necesario establecer psicologo o estudiante ya que se derivan de la cita
            historial_guardado.save()
            # messages.success(request, "Historial clínico guardado exitosamente.")
            return redirect('citas', cita_id=cita.id) # O donde quieras redirigir, ej., una vista de detalle del reporte
    else:
        form = HistorialClinicoForm(instance=historial)

    return render(request, 'formularios/formulario_historial_clinico.html', { # Crea esta plantilla
        'form': form,
        'cita': cita,
        'historial': historial if historial_id or 'existing_historial' in locals() else None,
        'form_title': form_title
    })


@login_required
def generar_pdf_historial_clinico(request, historial_id):
    historial = get_object_or_404(HistorialClinico, id=historial_id)
    cita = historial.cita

    # Verificación de permisos: solo el psicólogo asignado o el estudiante (si está finalizado)
    # Por ahora, solo el psicólogo
    if not (es_psicologo(request.user) and request.user.psicologo == cita.psicologo): #
        # Potencialmente permitir al estudiante si historial.reporte_finalizado es True en el futuro
        # messages.error(request, "No tiene permiso para ver este reporte.")
        raise Http404 # O redirigir

    # Datos para la plantilla PDF
    context = {
        'historial': historial,
        'cita': cita,
        'estudiante': cita.estudiante, #
        'psicologo_reporte': cita.psicologo, # Renombrado para evitar conflicto si 'psicologo' está en el contexto general #
        'usuario_estudiante': cita.estudiante.usuario, #
        'usuario_psicologo': cita.psicologo.usuario, #
    }
    
    # Renderizar plantilla HTML a una cadena
    html_string = render_to_string('pdf/pdf_template_historial_clinico.html', context) # Crea esta plantilla
    
    # CSS básico para el PDF (considera un archivo CSS separado para estilos más complejos)
    # Ejemplo de enlazar un archivo CSS estático:
    # css_path = os.path.join(settings.STATIC_ROOT, 'css/pdf_styles.css') # Asegúrate de que STATIC_ROOT esté configurado
    # if not os.path.exists(css_path): # Alternativa o error si no se encuentra el CSS
    #    css_path = None
    # stylesheets = [CSS(css_path)] if css_path else None

    base_url = request.build_absolute_uri('/') # Necesario para que WeasyPrint encuentre archivos estáticos como imágenes si se referencian en la plantilla

    html = HTML(string=html_string, base_url=base_url)
    pdf_file = html.write_pdf(
        # stylesheets=stylesheets # Descomenta si usas CSS externo
    )
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="historial_clinico_cita_{cita.id}_{cita.estudiante.usuario.username}.pdf"' #
    # Para mostrar en el navegador:
    # response['Content-Disposition'] = f'inline; filename="historial_clinico_cita_{cita.id}.pdf"'
    return response

@login_required
def listar_reportes_psicologo(request):
    if not es_psicologo(request.user): #
        # messages.error(request, "Acceso denegado.")
        return redirect('dashboard') # O alguna otra página apropiada

    psicologo_actual = request.user.psicologo #
    # Obtener todos los historiales clínicos creados por este psicólogo
    historiales = HistorialClinico.objects.filter(cita__psicologo=psicologo_actual).order_by('-fecha_creacion_reporte')
    
    # También obtener citas completadas por este psicólogo que AÚN NO tienen un historial clínico
    citas_sin_historial = Cita.objects.filter(
        psicologo=psicologo_actual, #
        estado='completada' #
    ).exclude(historial_clinico__isnull=False).order_by('-fecha_hora') #

    return render(request, 'psicologo/lista_reportes.html', { # Crea esta plantilla
        'historiales': historiales,
        'citas_sin_historial': citas_sin_historial,
        'psicologo_actual': psicologo_actual
    })

@login_required
def listar_reportes_estudiante_para_psicologo(request, estudiante_id):
    if not es_psicologo(request.user): #
        # messages.error(request, "Acceso denegado.")
        return redirect('dashboard') 

    estudiante = get_object_or_404(Estudiante, id=estudiante_id) #
    psicologo_actual = request.user.psicologo #

    # Asegurar que el psicólogo esté viendo reportes de estudiantes con los que ha tenido citas, o implementar otra lógica
    # Para simplificar, mostraremos todos los reportes del estudiante si el psicólogo lo solicita.
    # Agrega lógica más restrictiva si es necesario (ej., el psicólogo solo puede ver reportes de *sus* citas con el estudiante).
    historiales_estudiante = HistorialClinico.objects.filter(
        cita__estudiante=estudiante #
        # Opcionalmente, agrega: cita__psicologo=psicologo_actual si el psicólogo solo puede ver reportes que él creó
    ).order_by('-cita__fecha_hora') #

    return render(request, 'psicologo/reportes_por_estudiante.html', { # Crea esta plantilla
        'historiales_estudiante': historiales_estudiante,
        'estudiante_seleccionado': estudiante,
    })