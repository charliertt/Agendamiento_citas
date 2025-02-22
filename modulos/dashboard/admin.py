from django.contrib import admin
from .models import UsuarioPersonalizado, Preguntas, Psicologo, Estudiante, Administrativo, Horario, Cita, Contacto
# Register your models here.
admin.site.register(Psicologo)
admin.site.register(Estudiante)
admin.site.register(Administrativo)
admin.site.register(UsuarioPersonalizado)
admin.site.register(Preguntas)
admin.site.register(Horario)
admin.site.register(Cita)
admin.site.register(Contacto)