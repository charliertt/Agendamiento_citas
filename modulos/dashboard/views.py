from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from modulos.dashboard.models import UsuarioPersonalizado, Horario, Psicologo, Preguntas, Cita, Estudiante
from .forms import UsuarioPersonalizadoCreationForm, UsuarioPersonalizadoEditForm, HorarioForm, PreguntasForm, EmailAuthenticationForm, CitaForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login

# Create your views here.
def dashboard(request): 
    return render(request, 'dashboard.html')

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
    
    return render(request, 'usuarios.html', {'form': form, 'usuario': usuario})

    
def eliminar_usuario(request, usuario_id):
    usuario = UsuarioPersonalizado.objects.get(pk=usuario_id)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado con éxito')
        return redirect('usuarios')
    return render(request, 'usuarios.html', {'usuario': usuario})


#login:

def login_vista(request):
    if request.method == "POST":
        print("POST request received")
        print(f"Request Data: {request.POST}")
        form = EmailAuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            print("Form is valid")
            user = form.get_user()
            print(f"Authenticated User: {user}")
            login(request, user)
            print(f"User {user} logged in")
            return redirect('dashboard')
        else:
            print("Form is invalid")
            print(f"Form Errors: {form.errors}")
            messages.error(request, "El email o la contraseña son incorrectos")
    else: 
        print("GET request received")
        form = EmailAuthenticationForm()

    return render(request, "login.html", {"form": form})
    
    
    

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
    
    

def eliminar_pregunta(request, pregunta_id):
    pregunta = get_object_or_404(Preguntas, id_pregunta=pregunta_id)
    if request.method == 'POST':
        pregunta.delete()
        messages.success(request, 'Pregunta eliminada con éxito')
        return redirect('preguntas_tabla')
    return render(request, 'preguntas_tabla.html', {'pregunta': pregunta})


#citas:
class CitaListView(ListView):
    model = Cita
    template_name = "citas.html"  # Plantilla para listar las citas
    context_object_name = "citas"
    ordering = ['-fecha_hora']  
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Formulario para la creación de una nueva cita
        context['form'] = CitaForm()
        # Para cada cita en la lista, asignamos un formulario de edición
        for cita in context['citas']:
            cita.form_editar = CitaForm(instance=cita)
        return context
    


class CitaUpdateView(UpdateView):
    model = Cita
    form_class = CitaForm
    # Puedes utilizar una plantilla es pecífica para el formulario; si usas modales, quizás la plantilla sea idéntica a la que usas en el modal.
    template_name = "citas.html"  
    success_url = reverse_lazy("citas ")

    def form_valid(self, form):
        messages.success(self.request, "¡Cita editada correctamente!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Hubo un error al editar la cita. Verifica los datos ingresados.")
        return super().form_invalid(form)

class CitaDeleteView(DeleteView):
    model = Cita
    # Esta plantilla se usa para confirmar la eliminación; también podrías hacer la confirmación mediante un modal.
    template_name = "cita_confirm_delete.html"
    success_url = reverse_lazy("cita_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "¡Cita eliminada correctamente!")
        return super().delete(request, *args, **kwargs)