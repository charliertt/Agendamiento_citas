from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.contrib import messages
from modulos.dashboard.models import UsuarioPersonalizado, Horario, Psicologo, Preguntas
from .forms import UsuarioPersonalizadoCreationForm, UsuarioPersonalizadoEditForm, HorarioForm, PreguntasForm
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def dashboard(request): 
    return render(request, 'dashboard.html')

def usuarios(request):
    usuarios_list = list(UsuarioPersonalizado.objects.all())

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
                # Forzar creación/actualización
                psicologo, created = Psicologo.objects.update_or_create(
                    usuario=usuario_actualizado,
                    defaults={'especializacion': especializacion}
                )
            else:
                # Eliminar si existe
                Psicologo.objects.filter(usuario=usuario_actualizado).delete()
            
            usuario_actualizado.save()  # Guardar cambios del usuario
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
    
    
    
