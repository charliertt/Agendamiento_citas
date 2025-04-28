import pytz
from itsdangerous import URLSafeSerializer, BadSignature
from django.template.loader import get_template, render_to_string
from django.db import IntegrityError

# Importaciones comunes desde base_imports
from .base_importaciones import (
    messages, redirect, render, get_object_or_404,
    UsuarioPersonalizado, Psicologo, get_psicologo_context,
      never_cache,
    login_required, Review, Contacto
)




def perfil(request):
    context = {'usuario': request.user,
                'seccion_activa': 'perfil'}

    print( "hola", get_template('registration/password_change.html').origin)
    

    return render(request, 'perfil.html', context)

def reviews_perfil(request):
    # Comprueba si el usuario tiene la relación con Psicologo
    if hasattr(request.user, 'psicologo'):
        reviews = Review.objects.filter(psicologo=request.user.psicologo)
    # Comprueba si el usuario tiene la relación con Estudiante
    elif hasattr(request.user, 'estudiante'):
        reviews = Review.objects.filter(estudiante=request.user.estudiante)

    else:
        reviews = Review.objects.none()

    context = {
        'usuario': request.user,
        'seccion_activa': 'reviews',  
        'reviews': reviews,
    }
    return render(request, 'reviews_profile.html', context)

def buzon_profile(request):
    # Filtrar los contactos asociados al usuario logueado
    contactos = Contacto.objects.filter(email=request.user.email)

    context = {
        'usuario': request.user,
        'contactos': contactos,
    }
    return render(request, 'buzon_profile.html', context)

@never_cache
@login_required
def editar_perfil(request):
    usuario = request.user
    print(f"\n--- INICIO DE PETICIÓN [{request.method}] ---") 
    
    if request.method == 'POST':
        try:
            # Obtener nuevos valores del formulario
            nueva_identificacion = request.POST.get('identificacion')
            nuevo_email = request.POST.get('email', usuario.email)

            # Validar identificación única (excluyendo al usuario actual)
            if nueva_identificacion != usuario.identificacion:
                if UsuarioPersonalizado.objects.exclude(id=usuario.id).filter(identificacion=nueva_identificacion).exists():
                    messages.error(request, 'Esta identificación ya está registrada por otro usuario')
                    return redirect('editar_perfil')

            # Validar email único (excluyendo al usuario actual)
            if nuevo_email != usuario.email:
                if UsuarioPersonalizado.objects.exclude(id=usuario.id).filter(email=nuevo_email).exists():
                    messages.error(request, 'Este correo electrónico ya está registrado')
                    return redirect('editar_perfil')

            # Actualizar campos del usuario
            usuario.first_name = request.POST.get('first_name', usuario.first_name)
            usuario.last_name = request.POST.get('last_name', usuario.last_name)
            usuario.tipo_identificacion = request.POST.get('tipo_identificacion')
            usuario.identificacion = nueva_identificacion  
            usuario.eps = request.POST.get('eps', usuario.eps)
            usuario.alergias = request.POST.get('alergias', usuario.alergias)
            usuario.enfermedades = request.POST.get('enfermedades', usuario.enfermedades)
            usuario.email = nuevo_email  
            
            print("\nArchivos recibidos:", request.FILES)
            print("Datos POST:", request.POST)

           
            if 'imagen-clear' in request.POST:
                usuario.imagen.delete(save=True) 
                
                print("\n>>> Borrando imagen existente")
                usuario.imagen.delete(save=True)
                
                print("\nEstado ANTES de imagen:", usuario.imagen)
                
           
            if 'imagen' in request.FILES:
             
                usuario.imagen = request.FILES['imagen']
            
          
            print("Estado DESPUÉS de imagen:", usuario.imagen)
            
            usuario.save()
            print("\nUsuario guardado. Imagen final:", usuario.imagen.url if usuario.imagen else "Sin imagen")
            
        

            # Actualizar especialización para psicólogos
            if usuario.rol == 'psicologo':
                psicologo, created = Psicologo.objects.get_or_create(usuario=usuario)
                psicologo.especializacion = request.POST.get('especializacion')
                psicologo.save()
            
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('perfil')
        
        except IntegrityError as e:
            messages.error(request, 'Error al guardar los cambios')
            return redirect('editar_perfil')
    
    context = {
        'usuario': usuario,
        'psicologo': getattr(usuario, 'psicologo', None)
    }
    
    return render(request, 'perfil.html', context)