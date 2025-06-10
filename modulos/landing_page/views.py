import json
from django.shortcuts import render, redirect
from modulos.dashboard.models import Preguntas, Horario, Psicologo, Cita, Estudiante, UsuarioPersonalizado, Contacto, Respuesta, Blog

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.conf import settings


from modulos.dashboard.forms import BlogForm
from datetime import timedelta, datetime
from .forms import EstudianteForm, ContactoForm
from django.http import JsonResponse
from datetime import timedelta
from django.utils import timezone
import pytz
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, get_user_model, logout
from .envio import enviar_correo_confirmacion

# Create your views here.


def preguntas(request):
    if not request.user.is_authenticated:
        return redirect(f'/login/?next={request.path}')
    
    preguntas_list = list(Preguntas.objects.all().order_by('id_pregunta'))
    total = len(preguntas_list)
    current_index = request.session.get('current_index', 0)

    if current_index >= total:
        respuestas_correctas = request.session.get('respuestas_correctas', 0)
        porcentaje = (respuestas_correctas / total) * 100 if total > 0 else 0

        # Mapear el porcentaje a una calificación de 1 a 5 y asignar la nota correspondiente
        if porcentaje >= 90:
            nota = "Excelente"
            calificacion = 5
        elif porcentaje >= 70:
            nota = "Muy Bien"
            calificacion = 4
        elif porcentaje >= 50:
            nota = "Regular"
            calificacion = 3
        elif porcentaje >= 30:
            nota = "Necesita mejorar"
            calificacion = 2
        else:
            nota = "Insuficiente"
            calificacion = 1

        # Guarda la respuesta en el modelo Respuesta
        Respuesta.objects.create(
            usuario=request.user,
            calificacion=calificacion,
            nota=nota
        )

        # Reinicia el contador de sesión para un nuevo intento
        request.session['current_index'] = 0
        request.session['respuestas_correctas'] = 0

        return render(request, 'resultados.html', {
            'respuestas_correctas': respuestas_correctas,
            'total_preguntas': total,
            'porcentaje': porcentaje
        })

    pregunta_actual = preguntas_list[current_index]
    return render(request, 'preguntas.html', {
        'pregunta': pregunta_actual,
        'current_index': current_index,
        'total': total
    })




def validar_pregunta(request):
    if request.method == 'POST':
        preguntas_list = list(Preguntas.objects.all().order_by('id_pregunta'))
        total = len(preguntas_list)

        # Recuperamos el índice actual y la cantidad de respuestas correctas desde la sesión
        current_index = request.session.get('current_index', 0)
        respuestas_correctas = request.session.get('respuestas_correctas', 0)

        # Obtenemos la pregunta actual
        if current_index < total:
            pregunta_actual = preguntas_list[current_index]
            # El nombre del input se genera con el id de la pregunta, por ejemplo: respuesta_1, respuesta_2, etc.
            respuesta_usuario = request.POST.get(f"respuesta_{pregunta_actual.id_pregunta}")

            if respuesta_usuario:
                # Comparamos la respuesta enviada con la respuesta correcta almacenada en la pregunta
                if respuesta_usuario == 'True' and pregunta_actual.respuesta:
                    respuestas_correctas += 1
                elif respuesta_usuario == 'False' and not pregunta_actual.respuesta:
                    respuestas_correctas += 1

        # Actualizamos la sesión: aumentamos el índice y guardamos la cantidad de respuestas correctas
        request.session['current_index'] = current_index + 1
        request.session['respuestas_correctas'] = respuestas_correctas

    return redirect('preguntas')  
    


def resultados(request):
    
    
    return render(request, 'resultados.html')
    
    

def generar_intervalos(hora_inicio, hora_fin):
    intervalos = []
    hora_actual = datetime.combine(datetime.today(), hora_inicio)  # Corregido
    hora_limite = datetime.combine(datetime.today(), hora_fin)  # Corregido
 # Cambiado a datetime.datetime

    while hora_actual <= hora_limite:
        intervalos.append(hora_actual.time())  # Solo guardar la parte de la hora, sin la fecha
        hora_actual += timedelta(hours=1)  # Incrementar en 1 hora

    return intervalos


def obtener_horarios_disponibles(request):
    psicologo_id = request.GET.get('psicologo_id')
    dia = request.GET.get('dia')
    
    horarios = Horario.objects.filter(psicologo_id=psicologo_id, dia_semana=dia, disponible=True)
    
    horarios_json = [{'hora_inicio': str(h.hora_inicio), 'hora_fin': str(h.hora_fin)} for h in horarios]
    
    return JsonResponse({'horarios': horarios_json})

def index(request):
    blogs = Blog.objects.filter(publicado=True).order_by('-fecha_creacion')[:6]
    psicologos = Psicologo.objects.prefetch_related('horarios').all()
    estudiante_form = EstudianteForm()
    contact_form=ContactoForm()
    psicologos_con_horarios = []
    for psicologo in psicologos:
        horarios_con_intervalos = []
        dias_disponibles = set()
        for horario in psicologo.horarios.all():
            if horario.disponible:
                dias_disponibles.add(horario.dia_semana)
                print(">>> Generando intervalos para:", horario.dia_semana, 
                      "hora_inicio =", horario.hora_inicio, 
                      "hora_fin =", horario.hora_fin)
                
                intervalos = generar_intervalos(horario.hora_inicio, horario.hora_fin)
                print(">>> Intervalos obtenidos:", intervalos)
                
                horarios_con_intervalos.append({
                    'horario': horario,
                    'intervalos': intervalos
                })
        psicologos_con_horarios.append({
            'psicologo': psicologo,
            'horarios_con_intervalos': horarios_con_intervalos,
            'dias_disponibles': list(dias_disponibles),
    
        })

    context = {
        'psicologos_con_horarios': psicologos_con_horarios,
        'estudiante_form': estudiante_form,
        "contact_form": contact_form,
        'blogs': blogs,
    }
    return render(request, 'index.html', context)





def verificar_usuario(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            if not email:
                return JsonResponse({'exists': False, 'error': 'No se proporcionó correo.'}, status=400)
        except Exception:
            return JsonResponse({'exists': False, 'error': 'Solicitud inválida.'}, status=400)
        
        try:
            usuario = UsuarioPersonalizado.objects.get(email=email)
            # Envía los datos que quieras usar para precargar el formulario
            user_data = {
                 'first_name': usuario.first_name,
                'last_name': usuario.last_name,
                'username': usuario.username,
                'tipo_identificacion': usuario.tipo_identificacion,
                'identificacion': usuario.identificacion,
                'eps': usuario.eps,
                'alergias': usuario.alergias,
                'enfermedades': usuario.enfermedades,
                'email': usuario.email,
                
            }
            return JsonResponse({'exists': True, 'user_data': user_data})
        except UsuarioPersonalizado.DoesNotExist:
            return JsonResponse({'exists': False})
    
    return JsonResponse({'error': 'Método no permitido.'}, status=405)



def agendar_cita(request):
    if request.method == 'POST':
        # Extrae datos de los campos ocultos y otros necesarios
        selected_date = request.POST.get('selected_date')  # ej. "2025-02-20"
        selected_time = request.POST.get('selected_time')  # ej. "07:00 AM"
        psicologo_id = request.POST.get('psicologo_id')
        email = request.POST.get('email')  # El correo ya se habrá precargado si el usuario existe

        # Convierte la hora seleccionada en un objeto datetime
        time_part, period = selected_time.strip().split()
        hours, minutes = map(int, time_part.split(':'))
        if period == 'PM' and hours != 12:
            hours += 12
        elif period == 'AM' and hours == 12:
            hours = 0

        datetime_str = f"{selected_date} {hours:02d}:{minutes}"
        fecha_hora_cita = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        tz = pytz.timezone('America/Bogota')
        fecha_hora_cita = tz.localize(fecha_hora_cita)

        # Obtiene el psicólogo; si no se encuentra, retorna error
        try:
            psicologo = Psicologo.objects.get(pk=psicologo_id)
        except Psicologo.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Psicólogo no encontrado.'})

        # Verifica si ya existe una cita en el intervalo seleccionado
        cita_existente = Cita.objects.filter(
            psicologo=psicologo,
            fecha_hora__gte=fecha_hora_cita,
            fecha_hora__lt=fecha_hora_cita + timedelta(minutes=60),
            estado='agendada'
        ).exists()
        if cita_existente:
            return JsonResponse({'success': False, 'error': 'El horario seleccionado ya está ocupado.'})

        # Verifica si el usuario ya está registrado (por su correo)
        try:
            usuario = UsuarioPersonalizado.objects.get(email=email)
            estudiante = Estudiante.objects.get(usuario=usuario)
        except UsuarioPersonalizado.DoesNotExist:
            # Usuario nuevo: se procesa el formulario de registro completo
            form = EstudianteForm(request.POST)
            if form.is_valid():
                usuario = form.save()
                estudiante = Estudiante.objects.create(usuario=usuario)
            else:
    # Procesa los errores en un string legible
                error_messages = []
                for field, errors in form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                
                error_string = ", ".join(error_messages)
                
                return JsonResponse({
                    'success': False,
                    'error': error_string,
                    'errors': form.errors.as_json()
                })
              

                
        except Estudiante.DoesNotExist:
            # Si el usuario existe pero no tiene un registro de estudiante, se crea
            estudiante = Estudiante.objects.create(usuario=usuario)

        # Define el asunto y recoge comentarios
        asunto = "Consulta de Psicología"
        comentarios = request.POST.get('comentarios', '')

        # Crea la cita
        cita = Cita.objects.create(
            fecha_hora=fecha_hora_cita,
            estudiante=estudiante,
            psicologo=psicologo,
            asunto=asunto,
            estado='agendada',
            notas=comentarios
        )

        # Construye el contexto para el correo de confirmación
        context = {
            'nombre_paciente': usuario.first_name or usuario.username,
            'nombre_psicologo': cita.psicologo.usuario.username,
            'fecha_cita': timezone.localtime(cita.fecha_hora).strftime('%A %d de %B de %Y, %H:%M'),
            'direccion': 'Calle 54 #11d-44, Comuna 8, Cali, Valle del Cauca, Colombia',
            'enlace_modificar': 'https://tusitio.com/modificar-cita/',
            'comentarios': cita.notas,
        }
        enviar_correo_confirmacion.delay(context, usuario.email)

        # Retorna la respuesta JSON de confirmación
        response_data = {
            'success': True,
            'psychologist': cita.psicologo.usuario.username,
            'datetime': timezone.localtime(cita.fecha_hora).strftime('%A %d de %B a las %H:%M').capitalize(),
            'email': usuario.email,
        }
        return JsonResponse(response_data)
    return JsonResponse({'success': False, 'error': 'Método no permitido'})




def procesar_contacto(request):
    if request.method == 'POST':
        contact_form = ContactoForm(request.POST)
        if contact_form.is_valid():
            # Crear instancia sin guardar para asignar usuario
            contacto = contact_form.save(commit=False)  # Clave para modificar datos
            
            # Asignar usuario (prioridad a usuario autenticado)
            if request.user.is_authenticated:
                contacto.usuario = request.user
            else:
                # Buscar usuario por email solo si no está autenticado
                User = get_user_model()
                email = contact_form.cleaned_data['email']
                try:
                    usuario = User.objects.get(email=email)
                    contacto.usuario = usuario
                except User.DoesNotExist:
                    pass  # Contacto sin usuario asociado
            
            contacto.save()  # Guardar en BD con usuario asignado

            # Preparar datos para el correo
            context = {
                'nombre': contacto.nombre,
                'email': contacto.email,
                'deseo': contacto.get_deseo_display(),
                'mensaje': contacto.mensaje,
            }

            # Configurar y enviar email
            subject = f"Nuevo mensaje de contacto: {contacto.deseo}"
            from_email = "puntomentalcosfacali@gmail.com" # Mejor usar configuración
            recipient_list = ["puntomentalcosfacali@gmail.com"]  # Email del administrador
            
            html_content = render_to_string('contacto_email.html', context)
            text_content = f"Nombre: {contacto.nombre}\nEmail: {contacto.email}\nTipo: {contacto.deseo}\nMensaje:\n{contacto.mensaje}"
            
            msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            messages.success(request, "¡Tu mensaje se ha enviado correctamente!")
            return redirect('index')
        
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        contact_form = ContactoForm()

    return render(request, 'index.html', {'contact_form': contact_form})




#_______________BLOG____________________________________________________________


@method_decorator(login_required, name='dispatch')
class PsicologoBlogListView(ListView):
    """Vista para mostrar los blogs del psicólogo actual"""
    model = Blog
    template_name = 'blog/psicologo/blog_list.html'
    context_object_name = 'blogs'
    
    def get_queryset(self):
        # Filtrar blogs por el psicólogo actual
        try:
            psicologo = Psicologo.objects.get(usuario=self.request.user)
            return Blog.objects.filter(autor=psicologo)
        except Psicologo.DoesNotExist:
            return Blog.objects.none()


@method_decorator(login_required, name='dispatch')
class BlogCreateView(CreateView):
    """Vista para crear un nuevo blog"""
    model = Blog
    form_class = BlogForm
    template_name = 'blog/psicologo/blog_form.html'
    success_url = reverse_lazy('psicologo_blog_list')
    
    def form_valid(self, form):
        try:
            psicologo = Psicologo.objects.get(usuario=self.request.user)
            form.instance.autor = psicologo
            messages.success(self.request, 'Blog creado correctamente.')
            return super().form_valid(form)
        except Psicologo.DoesNotExist:
            messages.error(self.request, 'No tienes permiso para crear blogs.')
            return redirect('home')


@method_decorator(login_required, name='dispatch')
class BlogUpdateView(UpdateView):
    """Vista para actualizar un blog existente"""
    model = Blog
    form_class = BlogForm
    template_name = 'blog/psicologo/blog_form.html'
    success_url = reverse_lazy('psicologo_blog_list')
    
    def get_queryset(self):
        # Verificar que el blog pertenezca al psicólogo actual
        try:
            psicologo = Psicologo.objects.get(usuario=self.request.user)
            return Blog.objects.filter(autor=psicologo)
        except Psicologo.DoesNotExist:
            return Blog.objects.none()
    
    def form_valid(self, form):
        messages.success(self.request, 'Blog actualizado correctamente.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class BlogDeleteView(DeleteView):
    """Vista para eliminar un blog"""
    model = Blog
    template_name = 'blog/psicologo/blog_confirm_delete.html'
    success_url = reverse_lazy('psicologo_blog_list')
    
    def get_queryset(self):
        # Verificar que el blog pertenezca al psicólogo actual
        try:
            psicologo = Psicologo.objects.get(usuario=self.request.user)
            return Blog.objects.filter(autor=psicologo)
        except Psicologo.DoesNotExist:
            return Blog.objects.none()
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Blog eliminado correctamente.')
        return super().delete(request, *args, **kwargs)


# Vistas públicas
class BlogListView(ListView):
    """Vista para mostrar el listado de blogs"""
    model = Blog
    template_name = 'blog_detail.html'  # Usamos blog_detail.html para el listado
    context_object_name = 'blogs'
    paginate_by = 6  # Muestra 6 blogs por página
    
    def get_queryset(self):
        # Filtrar por categoría si existe en la URL
        categoria = self.kwargs.get('categoria')
        if categoria:
            return Blog.objects.filter(publicado=True, categoria=categoria)
        return Blog.objects.filter(publicado=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener todas las categorías y contar blogs por categoría
        categorias = {}
        for codigo, nombre in Blog.CATEGORIAS:
            count = Blog.objects.filter(publicado=True, categoria=codigo).count()
            if count > 0:  # Solo mostrar categorías con al menos un blog
                categorias[codigo] = {
                    'nombre': nombre,
                    'count': count
                }
        context['categorias'] = categorias
        
        # Agregar categoría actual si existe
        categoria = self.kwargs.get('categoria')
        if categoria:
            categoria_dict = dict(Blog.CATEGORIAS)
            context['categoria_actual'] = categoria_dict.get(categoria, categoria)
        
        return context


class BlogDetailView(DetailView):
    """Vista para mostrar un blog específico"""
    model = Blog
    template_name = 'blog_single.html'  # Cambiamos el nombre para evitar confusión
    context_object_name = 'blog'
    
    def get_queryset(self):
        # Solo mostrar blogs publicados o si el autor es el usuario actual
        queryset = Blog.objects.filter(publicado=True)
        if self.request.user.is_authenticated:
            try:
                psicologo = Psicologo.objects.get(usuario=self.request.user)
                # Unir los blogs publicados con los del autor actual (aunque no estén publicados)
                autor_queryset = Blog.objects.filter(autor=psicologo, publicado=False)
                return queryset | autor_queryset
            except Psicologo.DoesNotExist:
                pass
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar blogs recientes para el sidebar
        context['blogs_recientes'] = Blog.objects.filter(publicado=True).exclude(id=self.object.id)[:5]
        
        blog = self.object
        contenido = blog.contenido
        
        # Dividir el contenido en segmentos usando marcadores
        split_cita = contenido.split('[CITA]', 1)
        if len(split_cita) == 2:
            before_quote, after_quote = split_cita
            split_imagen = after_quote.split('[IMAGEN]', 1)
            if len(split_imagen) == 2:
                between_quote_imagen, after_imagen = split_imagen
            else:
                between_quote_imagen = after_quote
                after_imagen = ''
        else:
            before_quote = contenido
            between_quote_imagen = ''
            after_imagen = ''
        
        context.update({
            'contenido_before_quote': before_quote,
            'contenido_between': between_quote_imagen,
            'contenido_after_imagen': after_imagen,
        })
        
        # Obtener todas las categorías y contar blogs por categoría (para el sidebar)
        categorias = {}
        for codigo, nombre in Blog.CATEGORIAS:
            count = Blog.objects.filter(publicado=True, categoria=codigo).count()
            if count > 0:  # Solo mostrar categorías con al menos un blog
                categorias[codigo] = {
                    'nombre': nombre,
                    'count': count
                }
        context['categorias'] = categorias
        
        context['related_posts'] = (
            Blog.objects
                .filter(publicado=True, categoria=blog.categoria)
                .exclude(id=blog.id)[:5]
        )
        
        return context


class BlogCategoryView(ListView):
    """Vista para mostrar blogs por categoría"""
    model = Blog
    template_name = 'blog/blog_list.html'
    context_object_name = 'blogs'
    
    def get_queryset(self):
        # Filtrar blogs por categoría
        categoria = self.kwargs.get('categoria')
        return Blog.objects.filter(publicado=True, categoria=categoria)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar conteo de blogs por categoría
        categorias = {}
        for codigo, nombre in Blog.CATEGORIAS:
            count = Blog.objects.filter(publicado=True, categoria=codigo).count()
            categorias[codigo] = {'nombre': nombre, 'count': count}
        context['categorias'] = categorias
        
        # Agregar nombre de la categoría actual
        categoria_actual = self.kwargs.get('categoria')
        for codigo, nombre in Blog.CATEGORIAS:
            if codigo == categoria_actual:
                context['categoria_actual'] = nombre
                break
        
        return context