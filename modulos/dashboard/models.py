from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    email = models.EmailField(unique=True)  # Asegúrate de que el email sea único

    USERNAME_FIELD = 'email'      # Se usará el email para autenticarse
    REQUIRED_FIELDS = ['username']
    
  
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
    
    def __str__(self):
        return self.usuario.username
    
 

class Psicologo(models.Model):
    usuario = models.OneToOneField(UsuarioPersonalizado, on_delete=models.CASCADE, related_name='psicologo')
    especializacion = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
            # Retorna el nombre de usuario o cualquier otro dato descriptivo
        return f"{self.usuario.username} - {self.especializacion or 'Sin especialización'}"


class Administrativo(models.Model):
    usuario = models.OneToOneField(UsuarioPersonalizado, on_delete=models.CASCADE, related_name='administrativo')
    # Campos específicos para administrativos (si los hay)
# Create your models here.

class Horario(models.Model):
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.CharField(
        max_length=10,
        choices=[('Lunes', 'Lunes'),
                 ('Martes', 'Martes'),
                 ('Miércoles', 'Miércoles'),
                 ('Jueves', 'Jueves'),
                 ('Viernes', 'Viernes'),
                 ('Sábado', 'Sábado'),
                 ('Domingo', 'Domingo')],
    )
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    disponible = models.BooleanField(default=True)  # Opcional: Para marcar si el horario está disponible o no.

    def __str__(self):
        return f"{self.psicologo.usuario.username} - {self.dia_semana}: {self.hora_inicio} a {self.hora_fin}"
    



class Cita(models.Model):
    ESTADOS = [
        ('agendada', 'Agendada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]

    fecha_hora = models.DateTimeField(
        verbose_name="Fecha y Hora de la Cita",
        help_text="Indica la fecha y hora en la que se realizará la cita."
    )
    
    # Relación con el estudiante a través del modelo Estudiante
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='citas_estudiante',
        verbose_name="Estudiante"
    )
    
    # Relación con el psicólogo (se mantiene la relación con el modelo Psicologo)
    psicologo = models.ForeignKey(
        Psicologo,
        on_delete=models.CASCADE,
        related_name='citas',
        verbose_name="Psicólogo"
    )
    
    asunto = models.CharField(
        max_length=255,
        verbose_name="Asunto",
        help_text="Tema o motivo de la cita."
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='agendada',
        verbose_name="Estado"
    )
    
    notas = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notas",
        help_text="Comentarios adicionales (opcional)."
    )

    def __str__(self):
        return (
            f"Cita #{self.id} - {self.estudiante.usuario.username} "  # Accedemos al username a través de la relación Estudiante → UsuarioPersonalizado
            f"con {self.psicologo.usuario.username} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
        )

    

class Preguntas(models.Model):
    # Definición de las constantes para cada categoría
    ANSIEDAD   = 'ANS'
    ESTRES     = 'EST'
    DIALOGO    = 'DIA'
    AUTOESTIMA = 'AUT'
    RESILIENCIA= 'RES'
    EMPATIA    = 'EMP'
    
    # Tupla de opciones (código, etiqueta legible)
    CATEGORIA_CHOICES = [
        (ANSIEDAD,   'Ansiedad'),
        (ESTRES,     'Estrés'),
        (DIALOGO,    'Diálogo'),
        (AUTOESTIMA, 'Autoestima'),
        (RESILIENCIA,'Resiliencia'),
        (EMPATIA,    'Empatía'),
    ]
    
    id_pregunta = models.AutoField(primary_key=True)
    # Se establece el choices y se define un valor por defecto
    categoria = models.CharField(
        max_length=3, 
        choices=CATEGORIA_CHOICES, 
        default=ANSIEDAD
    )
    pregunta = models.CharField(max_length=200)
    respuesta = models.BooleanField()

    def __str__(self):
        return f'{self.pregunta} - {"Verdadero" if self.respuesta else "Falso"}'


    


