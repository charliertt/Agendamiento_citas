# Bibliotecas estándar
import pytz
from sqlite3 import IntegrityError
from itsdangerous import URLSafeSerializer, BadSignature
# Importaciones de Django
from django.conf import settings
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.serializers import serialize
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.template.loader import get_template, render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy, reverse
from django.db.models import Avg  
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
# Importaciones de la aplicación
from modulos.dashboard.models import UsuarioPersonalizado, Horario, Psicologo, Preguntas, Cita, Estudiante, Contacto, Review,Contacto, Cita, Notificacion
from .forms import UsuarioPersonalizadoCreationForm, UsuarioPersonalizadoEditForm, HorarioForm, PreguntasForm, EmailAuthenticationForm, CitaForm, EstudianteForm, RespuestaForm, ReviewForm

# Create your views here.

    






    



#preguntas


#buzon:

#citas:


    
