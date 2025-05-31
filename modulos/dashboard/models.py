from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField





class UsuarioPersonalizado(AbstractUser):
    TIPOS_IDENTIFICACION = [
        ('cedula', 'Cédula'),
        ('tarjeta_identidad', 'Tarjeta de Identidad'),
    ]

    ROLES = [
        ('estudiante', 'Estudiante'),
        ('psicologo', 'Psicólogo'),
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
    disponible = models.BooleanField(default=True) 
    
  

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
    usuario = models.ForeignKey(
        UsuarioPersonalizado, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        verbose_name="Usuario relacionado"
    )
    
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
        ('contacto', 'Nuevo mensaje'),
        ('cita', 'Actualización cita'),
        ('sistema', 'Actualización sistema'),
        ('cuestionario', 'Cuestionario completado'),
    )

    DESTINATARIOS = (
        ('estudiante', 'Estudiante'),
        ('psicologo', 'Psicólogo'),
        ('todos', 'Todos los usuarios'),
    )

    usuario = models.ForeignKey(
        UsuarioPersonalizado, 
        on_delete=models.CASCADE, 
        related_name='notificaciones',
        null=True,  # Permitir notificaciones globales
        blank=True
    )
    destinatario_tipo = models.CharField(
        max_length=20, 
        choices=DESTINATARIOS,
        default='todos'
    )
    tipo = models.CharField(max_length=20, choices=TIPOS)
    mensaje = models.CharField(max_length=255)
    relacionado_con = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Relacionado con"
    )
    enlace = models.URLField(blank=True, null=True)
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.mensaje[:50]}"



# models.py (añadir al archivo existente)
class Blog(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(unique=True, help_text="URL amigable generada automáticamente desde el título")
    autor = models.ForeignKey('Psicologo', on_delete=models.CASCADE, related_name='blogs')
    
    
    contenido = RichTextUploadingField(verbose_name="Contenido del Blog")
    
    imagen_principal = models.ImageField(upload_to='blog_images/', blank=True, null=True, verbose_name="Imagen Principal")
    imagen_secundaria = models.ImageField(upload_to='blog_images/',blank=True, null=True, verbose_name="Imagen Secundaria")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    CATEGORIAS = [
        ('ansiedad', 'Ansiedad'),
        ('depresion', 'Depresión'),
        ('terapia', 'Terapia'),
        ('neurociencia', 'Neurociencia'),
        ('psicologia_positiva', 'Psicología Positiva'),
        ('desarrollo_personal', 'Desarrollo Personal'),
        ('otros', 'Otros'),
    ]
    
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='otros', verbose_name="Categoría")
    publicado = models.BooleanField(default=False, help_text="Marcar para publicar el blog", verbose_name="Publicado")
    
    # Nuevo campo para cita destacada
    cita_destacada = models.TextField(
        verbose_name="Cita destacada", 
        blank=True, 
        null=True,
        help_text="Una cita o frase destacada que aparecerá en blockquote"
    )
    
    class Meta:
        verbose_name = "Blog"
        verbose_name_plural = "Blogs"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs):
        # Genera el slug automáticamente desde el título si no existe
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)



class HistorialClinico(models.Model):
    cita = models.OneToOneField(
        Cita,
        on_delete=models.CASCADE,
        related_name='historial_clinico',
        limit_choices_to={'estado': 'completada'}, # Asegura que el historial solo sea para citas completadas
        verbose_name="Cita Asociada"
    )
    # Campos redundantes, se pueden acceder mediante self.cita.psicologo y self.cita.estudiante
    # psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE, related_name='historiales_creados')
    # estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='historiales_clinicos')
    
    # Campos a ser llenados por el psicólogo para el reporte
    motivo_consulta_reporte = models.TextField(
        verbose_name="Motivo de Consulta (para el reporte)", 
        help_text="Detalle del motivo de la consulta tal como se registrará en el historial."
    )
    antecedentes_relevantes = RichTextUploadingField( #
        verbose_name="Antecedentes Relevantes", 
        blank=True, null=True,
        help_text="Información previa del estudiante que sea pertinente para el caso."
    )
    evaluacion_sesion = RichTextUploadingField( #
        verbose_name="Evaluación y Desarrollo de la Sesión",
        help_text="Descripción de lo ocurrido y evaluado durante la sesión."
    )
    diagnostico_impresion = RichTextUploadingField( # Cambiado de TextField a RichText por consistencia #
        verbose_name="Impresión Diagnóstica / Conceptualización del Caso", 
        blank=True, null=True,
        help_text="Análisis y conclusiones del psicólogo sobre el caso."
    )
    plan_intervencion_sugerencias = RichTextUploadingField( #
        verbose_name="Plan de Intervención y Sugerencias", 
        blank=True, null=True,
        help_text="Acciones a seguir, recomendaciones para el estudiante o terceros."
    )
    evolucion_observaciones_adicionales = RichTextUploadingField( #
        verbose_name="Evolución y Observaciones Adicionales", 
        blank=True, null=True,
        help_text="Progreso del estudiante y cualquier otra observación relevante."
    )
    
    # Metadatos del reporte
    fecha_creacion_reporte = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación del Reporte")
    ultima_actualizacion_reporte = models.DateTimeField(auto_now=True, verbose_name="Última Actualización del Reporte")
    reporte_finalizado = models.BooleanField(
        default=False, 
        verbose_name="Reporte Finalizado", 
        help_text="Marcar si el psicólogo ha completado y revisado el reporte. Esto podría habilitar su descarga por el estudiante en el futuro."
    )
    # archivo_pdf_adjunto = models.FileField(upload_to='reportes_clinicos/', blank=True, null=True, verbose_name="Archivo PDF Adjunto") # Considerar generar sobre la marcha

    class Meta:
        verbose_name = "Historial Clínico"
        verbose_name_plural = "Historiales Clínicos"
        ordering = ['-cita__fecha_hora'] # Ordenar por la fecha de la cita

    def __str__(self):
        return f"Historial Clínico para Cita #{self.cita.id} ({self.cita.estudiante.usuario.username})"

    def save(self, *args, **kwargs):
        # Pre-llenar motivo_consulta_reporte desde cita.asunto si está vacío en la creación
        if not self.pk and self.cita and self.cita.asunto and not self.motivo_consulta_reporte:
            self.motivo_consulta_reporte = self.cita.asunto
        super().save(*args, **kwargs)
        
# admin.py (crear o modificar este archivo)
