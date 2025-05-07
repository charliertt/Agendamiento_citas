from .base_importaciones import (UsuarioPersonalizado, Psicologo, UsuarioPersonalizadoEditForm, UsuarioPersonalizadoCreationForm 
    , messages, redirect, render, get_object_or_404, Estudiante,  login_required, never_cache)

from .autenticacion import psicologo_required

@psicologo_required
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

@login_required(login_url='/login')
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
@login_required(login_url='/login')
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
  
@login_required(login_url='/login')  
def eliminar_usuario(request, usuario_id):
    usuario = UsuarioPersonalizado.objects.get(pk=usuario_id)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado con éxito')
        return redirect('usuarios')
    return render(request, 'usuarios.html', {'usuario': usuario})
