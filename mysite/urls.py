from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include
from modulos.landing_page import views as landing_views

from modulos.dashboard import views as dashboard_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import reverse_lazy
from django.views.generic import TemplateView 
from modulos.dashboard.forms import CustomPasswordResetForm, CustomSetPasswordForm



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_views.index, name="index"),
    path('index/', landing_views.index, name="index"),  
     path('blog/', landing_views.BlogListView.as_view(), name='blog'),
    
    # Vista filtrada por categoría
    path('blog/categoria/<str:categoria>/', landing_views.BlogListView.as_view(), name='blog_category'),
    
    # Vista de detalle de un blog específico
    path('blog/<slug:slug>/', landing_views.BlogDetailView.as_view(), name='blog_detail'),


    
    path('validar_pregunta/', landing_views.validar_pregunta, name='validar_pregunta'),
    
    # Dashboard
    path('dashboard/', dashboard_views.dashboard, name="dashboard"),
    
    #usuarios
    path('usuarios/', dashboard_views.usuarios, name="usuarios"),
    path('crear_usuario/', dashboard_views.crear_usuario, name="crear_usuario"),
    path('editar_usuario/<int:usuario_id>/', dashboard_views.editar_usuario, name="editar_usuario"),
    path('eliminar_usuario/<int:usuario_id>/', dashboard_views.eliminar_usuario, name="eliminar_usuario"),

    #perfil
    path('perfil/', dashboard_views.perfil, name="perfil"),
	path('editar_perfil/', dashboard_views.editar_perfil, name="editar_perfil"),
    #auenticacion
    path('login/', dashboard_views.login_vista, name="login"),
    path('logout/', dashboard_views.logout_vista, name="logout"),

    #validaciones formulario de estudiante
	path('registro_estudiante/', dashboard_views.registro_estudiante, name="registro_estudiante"),
 
    
    path('review/', dashboard_views.ListaCitasReviewView.as_view(), name='review'),
    path('reviews_profile/', dashboard_views.reviews_perfil, name='reviews_perfil'),
    
    path('buzon_profile/', dashboard_views.buzon_profile, name='buzon_profile'),
 
    
	path('verificar_email/', dashboard_views.verificar_email, name='verificar_email'),
	
    path('verificar_username/', dashboard_views.verificar_username, name='verificar_username'),
    path('verificar_identificacion/', dashboard_views.verificar_identificacion, name='verificar_identificacion'),

    #peticiones, quejas y sugerencias:
    path('lista_contactos/', dashboard_views.lista_contactos, name='lista_contactos'),
    path('responder_contacto/<int:contacto_id>/', dashboard_views.responder_contacto, name="responder_contacto"),
    

    #horarios
    path('horarios/',  dashboard_views.horarios, name='horarios'),  
    path('horario/<int:horario_id>/',  dashboard_views.crear_editar_horario, name='crear_editar_horario'),
    path('eliminar_horario/<int:horario_id>/', dashboard_views.eliminar_horario, name="eliminar_horario"),
    
    #preguntas
    path('preguntas_tabla/', dashboard_views.preguntas_tabla, name="preguntas_tabla"),
    path('pregunta/<int:pregunta_id>/', dashboard_views.crear_editar_pregunta, name='crear_editar_pregunta'),
    path('eliminar_pregunta/<int:pregunta_id>/', dashboard_views.eliminar_pregunta, name="eliminar_pregunta"),

    #citas:
    path('crear_cita/', dashboard_views.CitaCreateView.as_view(), name='crear_cita'),    
    path('citas/', dashboard_views.CitaListView.as_view(), name='citas'),
    path('citas/editar/<int:pk>/', dashboard_views.CitaUpdateView.as_view(), name='cita_update'),
    path('cita/eliminar/<int:pk>/', dashboard_views.CitaDeleteView.as_view(), name='eliminar_cita'),
    path('verificar_usuario/', landing_views.verificar_usuario, name='verificar_usuario'),
    
    
    #__________________________________citas_fronted______________________________________________
    

    # Ruta para obtener horarios en la API
   
    path('agendar-cita/', landing_views.agendar_cita, name='agendar_cita'),
    path('horarios-disponibles/', landing_views.obtener_horarios_disponibles, name='horarios_disponibles'),

    #procesar_contacto
    path('procesar_contacto/', landing_views.procesar_contacto, name='procesar_contacto'),
	
    #__________________________________preguntas______________________________________________
    path('preguntas/', landing_views.preguntas, name="preguntas"),
    path('resultados/', landing_views.resultados, name="resultados"),
	
     # Cambio de contraseña (USUARIOS LOGUEADOS)
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change.html',
        success_url=reverse_lazy('password_change_done')
    ), name='password_change'),
    
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'  # Tu template con el check
    ), name='password_change_done'),

    # Restablecimiento de contraseña (USUARIOS NO LOGUEADOS)
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html',
        form_class=CustomPasswordResetForm,
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),
    
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'  # Solo dice "email enviado"
    ), name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        form_class=CustomSetPasswordForm,
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),
    
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'  
    ), name='password_reset_complete'),
    

    #__________________________________reviews______________________________________________
    

     path(
        'review/gracias/', 
        TemplateView.as_view(template_name='gracias_review.html'),
        name='gracias_review'  # Asegúrate de agregar el nombre
    ),
     
     
     
    
    # URL para crear reseña (con token)
    path('review/<str:token>/', dashboard_views.CrearReviewView.as_view(), name='crear_review'),
    path('marcar-notificacion-leida/<int:notificacion_id>/',  dashboard_views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    
    #notas
    path('notas/', dashboard_views.notas, name='notas'),


     path('ckeditor/', include('ckeditor_uploader.urls')),
  
   

    
]




if settings.DEBUG:
    	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


    