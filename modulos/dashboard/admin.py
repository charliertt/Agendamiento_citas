from django.contrib import admin
from .models import UsuarioPersonalizado,Blog,Preguntas, Psicologo, Estudiante, Horario, Cita, Contacto, Respuesta, Review, Cita, Notificacion



# Register your models here.
admin.site.register(Psicologo)
admin.site.register(Estudiante)

admin.site.register(UsuarioPersonalizado)
admin.site.register(Preguntas)
admin.site.register(Horario)
admin.site.register(Cita)
admin.site.register(Contacto)
admin.site.register(Respuesta)
admin.site.register(Review)
admin.site.register(Notificacion)


class BlogAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'fecha_creacion', 'publicado')
    list_filter = ('categoria', 'publicado', 'autor')
    search_fields = ('titulo', 'contenido')
    prepopulated_fields = {'slug': ('titulo',)}
    date_hierarchy = 'fecha_creacion'
    ordering = ('-fecha_creacion',)
    
    # Este método limita los blogs mostrados a solo aquellos del psicólogo conectado
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Si no es superusuario y es psicólogo, mostrar solo sus blogs
        if not request.user.is_superuser and hasattr(request.user, 'psicologo'):
            return qs.filter(autor=request.user.psicologo)
        return qs
    
    # Establece automáticamente el autor como el psicólogo actual
    def save_model(self, request, obj, form, change):
        if not obj.autor_id and hasattr(request.user, 'psicologo'):
            obj.autor = request.user.psicologo
        super().save_model(request, obj, form, change)

# Registrar el modelo en el admin
admin.site.register(Blog, BlogAdmin)
