from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, FormView
from itsdangerous import URLSafeSerializer, BadSignature
from django.conf import settings
from django.template.loader import get_template, render_to_string

from .base_importaciones import (
    messages,  timezone, CitaForm, Cita,  EmailMultiAlternatives
)


class CitaCreateView(CreateView):
    model = Cita
    form_class = CitaForm
    template_name = "citas.html"
    success_url = reverse_lazy("citas")

    def form_valid(self, form):
        # Obtén el valor de la fecha/hora ingresado en el formulario
        fecha_hora = form.instance.fecha_hora
        # Si la fecha/hora es naive (sin información de zona horaria), la hacemos "aware"
        if fecha_hora and timezone.is_naive(fecha_hora):
            # Esto utiliza la zona horaria configurada en settings (America/Bogota)
            form.instance.fecha_hora = timezone.make_aware(fecha_hora, timezone.get_current_timezone())
        
        messages.success(self.request, "¡Cita creada correctamente!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Hubo un error al crear la cita. Verifica los datos ingresados.")
        return super().form_invalid(form)
    
class CitaListView(ListView):
    model = Cita
    template_name = "citas.html"  # Plantilla para listar las citas
    context_object_name = "citas"
    ordering = ['-fecha_hora']  
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'review'  # Añade la variable active_page
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.rol == 'estudiante':
            # Filtrar las citas para que solo muestre las del estudiante logueado
            qs = qs.filter(estudiante__usuario=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Formulario para la creación de una nueva cita
        context['form'] = CitaForm()
        # Para cada cita en la lista, asignamos un formulario de edición
        for cita in context['citas']:
            cita.form_editar = CitaForm(instance=cita)
        # Agregar la URL para crear cita
        context['crear_cita_url'] = reverse('crear_cita')
        return context

class CitaUpdateView(UpdateView):
    model = Cita
    form_class = CitaForm
    template_name = "citas.html"  
    success_url = reverse_lazy("citas")

    def form_valid(self, form):
        # Obtener instancia antes de guardar cambios
        old_estado = self.get_object().estado
        new_estado = form.cleaned_data.get('estado')

        response = super().form_valid(form)
        
        # Solo si cambió el estado
        if old_estado != new_estado:
            cita = self.object
            
            # Enviar correo de cancelación
            if new_estado == 'cancelada':
                self.enviar_correo_cancelacion(cita)
                
            # Enviar correo de completado con enlace
            elif new_estado == 'completada':
                self.enviar_correo_completada(cita)

        messages.success(self.request, "¡Cita editada correctamente!")
        return response

    def enviar_correo_cancelacion(self, cita):
        context = {
            'nombre_paciente': cita.estudiante.usuario.first_name,
            'nombre_psicologo': cita.psicologo.usuario.get_full_name(),
            'fecha_cita': cita.fecha_hora.strftime('%d/%m/%Y'),
            'hora_cita': cita.fecha_hora.strftime('%H:%M'),
            'citas_url': self.request.build_absolute_uri(reverse('citas'))
        }
        
        html_content = render_to_string('cita_cancelada.html', context)
        
        msg = EmailMultiAlternatives(
            subject="Tu cita ha sido cancelada ❌",
            body=html_content,  # Versión texto plano opcional
            from_email='puntomentalcosfacali@gmail.com',
            to=[cita.estudiante.usuario.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def enviar_correo_completada(self, cita):
        serializer = URLSafeSerializer(settings.SECRET_KEY)
        token = serializer.dumps(cita.id)

        print(f"\n--- DEBUG GENERACIÓN TOKEN ---")
        print(f"Cita ID: {cita.id} (tipo: {type(cita.id)})")
        print(f"Token generado: {token}")

        
        context = {
            'nombre_paciente': cita.estudiante.usuario.first_name,
            'nombre_psicologo': cita.psicologo.usuario.get_full_name(),
            'fecha_cita': cita.fecha_hora.strftime('%d/%m/%Y'),
            'enlace_review': self.request.build_absolute_uri(
                reverse('crear_review', kwargs={'token': token})
            )
            }
        
        html_content = render_to_string('cita_completada.html', context)
        
        msg = EmailMultiAlternatives(
            subject="¡Califica tu sesión ⭐",
            body=html_content,
            from_email='puntomentalcosfacali@gmail.com',
            to=[cita.estudiante.usuario.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        


class CitaDeleteView(DeleteView):
    model = Cita
    # Esta plantilla se usa para confirmar la eliminación; también podrías hacer la confirmación mediante un modal.
    template_name = "citas.html"
    success_url = reverse_lazy("citas")

    def post(self, request, *args, **kwargs):
        messages.success(request, "¡Cita eliminada correctamente!")
        print("Mensaje de eliminación añadido")  # Verifica esto en la consola
        return self.delete(request, *args, **kwargs)