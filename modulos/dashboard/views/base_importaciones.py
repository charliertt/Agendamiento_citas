# Importaciones básicas de Django
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Q, Avg
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.urls import reverse  
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse, Http404

# Modelos
from modulos.dashboard.models import (
    UsuarioPersonalizado, Psicologo, Horario,
    Preguntas, Cita, Estudiante, Contacto,
    Review, Notificacion
)

# Formularios
from ..forms import (  
    UsuarioPersonalizadoEditForm,
    HorarioForm,
    PreguntasForm,
    CitaForm,
    EstudianteForm,
    ReviewForm,
    EmailAuthenticationForm,
    RespuestaForm
)

# Utilidades comunes
def get_psicologo_context(usuario):
    return {'psicologo': getattr(usuario, 'psicologo', None)}