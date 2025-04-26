from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, FormView, CreateView, ListView
from itsdangerous import URLSafeSerializer, BadSignature


# Importaciones necesarias desde base_importaciones
from .base_importaciones import (
    settings,
    IntegrityError,
    Review,
    Cita,
    messages,
    timezone,
    ReviewForm,
    EmailMultiAlternatives,
    get_psicologo_context,
)


class CrearReviewView(FormView):
    template_name = 'formularios/review_form.html'
    form_class = ReviewForm  
    success_url = reverse_lazy('gracias_review')
    

    def get_cita(self):
        try:
            token = self.kwargs['token']
            print(f"\n--- DEBUG GET_CITA ---")
            print(f"Token recibido: {token}")
            
            serializer = URLSafeSerializer(settings.SECRET_KEY)
            cita_id = serializer.loads(token)
            print(f"ID deserializado: {cita_id} (tipo: {type(cita_id)})")
            
            cita = Cita.objects.get(id=cita_id)
            print(f"Cita encontrada: {cita}")
            return cita
            
        except BadSignature as e:
            print(f"Error BadSignature: {str(e)}")
            return None
        except Cita.DoesNotExist:
            print(f"Error: Cita no existe en DB")
            return None
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token'] = self.kwargs['token']
        cita = self.get_cita()
        
        if not cita:
            context['error'] = "Enlace inválido o expirado"
            return context
            
        if Review.objects.filter(cita=cita).exists():
            context['error'] = "Ya has calificado esta sesión."
        else:
            context['cita'] = cita
            
        return context
    def form_valid(self, form):
        print("\n--- DEBUG FORM_VALID ---")
        cita = self.get_cita()
        
        if not cita:
            print("Error: Cita no existe en form_valid")
            form.add_error(None, "Enlace inválido o expirado")
            return self.form_invalid(form)
            
        if Review.objects.filter(cita=cita).exists():
            print("Error: Reseña ya existe")
            form.add_error(None, "Ya has calificado esta sesión.")
            return self.form_invalid(form)
        
        try:
            print("Intentando crear reseña...")
            Review.objects.create(
                cita=cita,
                psicologo=cita.psicologo,
                estudiante=cita.estudiante,
                puntuacion=form.cleaned_data['puntuacion'],
                comentario=form.cleaned_data['comentario']
            )
            print("¡Reseña creada exitosamente!")
        except IntegrityError as e:
            print(f"Error IntegrityError: {str(e)}")
            form.add_error(None, "Error al crear la reseña")
            return self.form_invalid(form)
            
        return super().form_valid(form)


class ListaCitasReviewView(ListView):
    template_name = 'review.html'
    model = Review
    context_object_name = 'reviews'
    ordering = ['-fecha_creacion']  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'review'  # Añade la variable active_page
        return context

    # Opcional: Filtros adicionales
    def get_queryset(self):
        return Review.objects.all()
    
class GraciasReviewView(TemplateView):
    template_name = 'gracias_review.html'    
    
    
def generar_token(cita_id):
    serializer = URLSafeSerializer(settings.SECRET_KEY)
    return serializer.dumps(cita_id)