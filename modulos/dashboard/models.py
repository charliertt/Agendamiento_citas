from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser

class UsuarioPersonalizado(AbstractUser):
    TIPOS_IDENTIFICACION = [
        ('cedula', 'Cédula'),
        ('tarjeta_identidad', 'Tarjeta de Identidad'),
    ]

    ROLES = [
        ('estudiante', 'Estudiante'),
        ('psicologo', 'Psicólogo'),
        ('administrativo', 'Administrativo'),
    ]

    rol = models.CharField(max_length=20, choices=ROLES, default='estudiante')
    tipo_identificacion = models.CharField(max_length=20, choices=TIPOS_IDENTIFICACION, blank=True, null=True)  # Nuevo campo
    identificacion = models.CharField(max_length=20, unique=True, blank=False, null=False) 
    eps = models.CharField(max_length=200, blank=True, null=True, default='ninguna')
    alergias = models.CharField(max_length=200, blank=True, null=True, default='ninguna')
    enfermedades = models.CharField(max_length=200, blank=True, null=True, default='ninguna')
  
    imagen = models.ImageField(upload_to='emedia/', blank=True, null=True)

    # Especifica un related_name único para los campos groups y user_permissions
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="usuario_personalizado_groups",  # Nombre único para el related_name
        related_query_name="usuario_personalizado",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="usuario_personalizado_user_permissions",  # Nombre único para el related_name
        related_query_name="usuario_personalizado",
    )

    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"


class Estudiante(models.Model):
    usuario = models.OneToOneField(UsuarioPersonalizado, on_delete=models.CASCADE, related_name='estudiante')
    
   


class Psicologo(models.Model):
    usuario = models.OneToOneField(UsuarioPersonalizado, on_delete=models.CASCADE, related_name='psicologo')
    especializacion = models.CharField(max_length=200, blank=True, null=True)
    horarios_disponibles = models.TextField(blank=True, null=True)


class Administrativo(models.Model):
    usuario = models.OneToOneField(UsuarioPersonalizado, on_delete=models.CASCADE, related_name='administrativo')
    # Campos específicos para administrativos (si los hay)
# Create your models here.

    
class Preguntas(models.Model):
    id_pregunta = models.AutoField(primary_key=True)
    categoria=models.CharField(max_length=200)
    pregunta = models.CharField(max_length=200)
    respuesta = models.BooleanField()

    def __str__(self):
        return f'{self.pregunta} - {"Verdadero" if self.respuesta else "Falso"}'
