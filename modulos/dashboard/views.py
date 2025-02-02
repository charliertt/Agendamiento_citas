from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.contrib import messages
from modulos.dashboard.models import UsuarioPersonalizado
from .forms import UsuarioPersonalizadoCreationForm
from django.contrib import messages


# Create your views here.
def dashboard(request): 
    return render(request, 'dashboard.html')

def usuarios(request): 
    usuarios=UsuarioPersonalizado.objects.all()
    form = UsuarioPersonalizadoCreationForm(request.POST, request.FILES)
    return render(request, 'usuarios.html', {'usuarios': usuarios, 
                                             "form": form})
                                             





def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioPersonalizadoCreationForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Guardar el nuevo usuario
            nuevo_usuario = form.save(commit=False)

            # Obtener el rol seleccionado para validar los campos específicos
            rol = form.cleaned_data.get('rol')

            # Validar los campos específicos según el rol
            if rol == 'psicologo':
                if not form.cleaned_data.get('especializacion'):
                    form.add_error('especializacion', 'Este campo es obligatorio para los psicólogos.')
                if not form.cleaned_data.get('horarios_disponibles'):
                    form.add_error('horarios_disponibles', 'Este campo es obligatorio para los psicólogos.')
            
            # Si no hay errores, guardar el usuario
            if not form.errors:
                nuevo_usuario.save()
                messages.success(request, 'El usuario ha sido creado exitosamente.')
                return redirect('usuarios')  # Redirigir a la lista de usuarios u otra vista

        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')

    else:
        form = UsuarioPersonalizadoCreationForm()

    return render(request, 'usuarios.html', {'form': form})


def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(UsuarioPersonalizado, pk=usuario_id)
    if request.method == 'POST':
        form = UsuarioPersonalizadoCreationForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            usuario_editado = form.save(commit=False)
            usuario_editado.save()
            messages.success(request, 'El usuario ha sido editado exitosamente.')
            return redirect('usuarios')
    else:
        form = UsuarioPersonalizadoCreationForm(instance=usuario)

    return render(request, 'usuarios.html', {
        'form': form,
        'usuario_id': usuario_id
    })
