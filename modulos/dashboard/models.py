from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone





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
        local_fecha_hora = timezone.localtime(self.fecha_hora)
        return (
            f"Cita #{self.id} - {self.estudiante.usuario.username} "  # Accedemos al username a través de la relación Estudiante → UsuarioPersonalizado
            f"con {self.psicologo.usuario.username} - {local_fecha_hora.strftime('%d/%m/%Y %H:%M')}"
            
        )
        

# models.py
class Review(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE)
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    puntuacion = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    
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


class Respuesta(models.Model):
    id_respuesta = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        UsuarioPersonalizado,
        on_delete=models.CASCADE,
        related_name='respuestas'
    )
    
    calificacion = models.DecimalField(
        max_digits=4,  
        decimal_places=2
    )
   
    nota = models.TextField(
        blank=True,
        null=True,
        help_text="Se asignará automáticamente en función de la calificación."
    )
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Respuesta de {self.usuario.username}  (Calificación: {self.calificacion})"

class Contacto(models.Model):
    # Opciones para el campo "deseo"
    TIPO_OPCIONES = (
        ('queja', 'Queja'),
        ('reclamo', 'Reclamo'),
        ('peticion', 'Petición'),
    )

    # Opciones para el campo "estado"
    ESTADO_OPCIONES = (
        ('pendiente', 'Pendiente'),
        ('resuelto', 'Resuelto'),
    )

    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    email = models.EmailField(verbose_name="Correo electrónico")
    deseo = models.CharField(
        max_length=10,
        choices=TIPO_OPCIONES,
        default='peticion',  # Valor por defecto
        verbose_name="Tipo de solicitud"
    )
    mensaje = models.TextField(verbose_name="Mensaje")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    estado = models.CharField(max_length=10, choices=ESTADO_OPCIONES, default='pendiente', verbose_name="Estado")

    def __str__(self):
        return f"{self.nombre} - {self.get_deseo_display()}"


class Notificacion(models.Model):
    TIPOS = (
        ('contacto', 'Nuevo mensaje de contacto'),
        ('cita', 'Nueva cita agendada'),
        ('sistema', 'Actualización del sistema'),
        ('recordatorio', 'Recordatorio de cita'),
    )

    usuario = models.ForeignKey(UsuarioPersonalizado, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    mensaje = models.CharField(max_length=255)
    enlace = models.URLField(blank=True, null=True)
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.mensaje[:50]}"

        


