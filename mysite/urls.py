"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from modulos.landing_page import views as landing_views
from modulos.dashboard import views as dashboard_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_views.index, name="index"),
    path('index/', landing_views.index, name="index"),  
    path('blog/', landing_views.blog, name="blog"),     
    path('preguntas/', landing_views.preguntas, name="preguntas"),
    path('validar_pregunta/', landing_views.validar_pregunta, name='validar_pregunta'),
    
    # Dashboard
    path('dashboard/', dashboard_views.dashboard, name="dashboard"),
    
    #usuarios
    path('usuarios/', dashboard_views.usuarios, name="usuarios"),
    path('crear_usuario/', dashboard_views.crear_usuario, name="crear_usuario"),
    path('editar_usuario/<int:usuario_id>/', dashboard_views.editar_usuario, name="editar_usuario"),
    path('eliminar_usuario/<int:usuario_id>/', dashboard_views.eliminar_usuario, name="eliminar_usuario"),
    path('perfil/', dashboard_views.perfil, name="perfil"),
    #auenticacion
    path('login/', dashboard_views.login_vista, name="login"),
    path('logout/', dashboard_views.logout_vista, name="logout"),

    #validaciones formulario de estudiante
	path('registro_estudiante/', dashboard_views.registro_estudiante, name="registro_estudiante"),
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
    path('procesar_contacto/', landing_views.procesar_contacto, name='procesar_contacto')

]

if settings.DEBUG:
    	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)