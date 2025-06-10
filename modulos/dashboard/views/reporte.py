# En tu_app/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
import os


from weasyprint import HTML

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
            return redirect('citas') # O donde quieras redirigir, ej., una vista de detalle del reporte
    else:
        form = HistorialClinicoForm(instance=historial)

    return render(request, 'formularios/formulario_historial_clinico.html', { # Crea esta plantilla
        'form': form,
        'cita': cita,
        'historial': historial if historial_id or 'existing_historial' in locals() else None,
        'form_title': form_title
    })


def ver_pdf_historial(request, cita_id, historial_id):
    # 1. Recupera el HistorialClinico (o como se llame tu modelo) asegurándote 
    #    de que pertenece a la cita indicada.
    cita = get_object_or_404(Cita, id=cita_id, estado='completada')
    historial = get_object_or_404(
        HistorialClinico,
        id=historial_id,
        cita=cita
    )

    # 2. Renderiza un template HTML con los datos del historial
    #    Crea un archivo template llamado "historial_pdf.html" (ver sección 3).
    html_string = render_to_string('pdf/pdf_template_historial_clinico.html', {
        'historial': historial,
        'cita': cita,
    })

    # 3. Genera el PDF a partir de ese HTML
    #    El parámetro base_url es útil para que WeasyPrint resuelva rutas estáticas (CSS, imágenes).
    pdf_bytes = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

    # 4. Devuelve una HttpResponse con content_type='application/pdf'
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    # inline = lo abre en el navegador; si quisieras forzar descarga, usa attachment
    response['Content-Disposition'] = f'inline; filename="historial_{historial_id}.pdf"'
    return response


def lista_reportes(request):
    """
    Muestra dos secciones:
      1) Citas completadas que aún NO tienen HistorialClinico
      2) Historiales Clínicos creados (con sus datos)
    """

    # 1. Todas las citas que ya estén en estado 'completada'
    citas_completadas = Cita.objects.filter(estado='completada')

    # 2. De esas, filtramos las que NO tienen historial_clinico asociado
    #    (historial_clinico es el related_name en tu OneToOneField).
    citas_sin_historial = citas_completadas.filter(historial_clinico__isnull=True)

    # 3. Obtenemos todos los HistorialClinico que ya se hayan creado,
    #    usando select_related para evitar consultas N+1 al iterar
    historiales = HistorialClinico.objects.select_related(
        'cita__estudiante__usuario',
        'cita__psicologo__usuario'
    ).order_by('-ultima_actualizacion_reporte')

    # 4. Pasamos ambas listas al contexto
    return render(request, 'lista_reportes.html', {
        'citas_sin_historial': citas_sin_historial,
        'historiales': historiales,
    })

