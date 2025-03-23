from .base_importaciones import (
    never_cache, login_required, render, get_object_or_404,
    Preguntas, PreguntasForm, messages, redirect
)



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
