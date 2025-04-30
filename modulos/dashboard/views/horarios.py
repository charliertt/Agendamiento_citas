# horario.py
from .base_importaciones import (
    Horario,
    HorarioForm,
    login_required,
    never_cache,
    messages,
    redirect,
    render,
    get_object_or_404,
    HttpResponseForbidden
)

@never_cache
@login_required
def horarios(request):
    horarios_list = Horario.objects.all()
    
    # Adjuntar formulario de edición a cada horario
    for horario in horarios_list:
        horario.form_editar = HorarioForm(instance=horario)
    
    return render(request, 'horarios.html', {
        'horarios': horarios_list,
        'form': HorarioForm()  # Formulario para crear
    })

@never_cache
@login_required
def crear_editar_horario(request, horario_id):
    horario = get_object_or_404(Horario, id=horario_id) if horario_id != 0 else None
    
    if request.method == 'POST':
        form = HorarioForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Operación exitosa!")
            return redirect('horarios')
        else:
            # Mostrar errores específicos del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    # Si es un error no asociado a un campo específico (como los del clean())
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_name = form[field].label or field
                        messages.error(request, f"{field_name}: {error}")
    
    return redirect('horarios')

@never_cache
@login_required
def eliminar_horario(request, horario_id):
    
    if request.method == 'POST':
        horario = get_object_or_404(Horario, pk=horario_id)
        horario.delete()
        messages.success(request, 'Horario eliminado')
    return redirect('horarios')