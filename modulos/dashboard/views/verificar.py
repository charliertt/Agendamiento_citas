from .base_importaciones import (
    JsonResponse)

def verificar_email(request):
    email = request.GET.get('email', '')
    User = get_user_model()
    existe = User.objects.filter(email=email).exists()
    return JsonResponse({'existe': existe})


def verificar_username(request):
    username = request.GET.get('username', '')
    User = get_user_model()
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

def verificar_identificacion(request):
    identificacion = request.GET.get('identificacion', '')
    exists = UsuarioPersonalizado.objects.filter(identificacion=identificacion).exists()
    return JsonResponse({'exists': exists})


    return render(request, 'usuarios.html', {'form': form, 'usuario': usuario})  