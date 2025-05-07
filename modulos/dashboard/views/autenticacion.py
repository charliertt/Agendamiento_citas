# autenticacion.py
from .base_importaciones import (
    never_cache,
    login_required,
    messages,
    redirect,
    render,
    login,
    logout,
    EmailAuthenticationForm
    
)
from django.contrib.auth.decorators import user_passes_test, login_required

@never_cache
def login_vista(request):
    # Capturamos el parámetro 'next' tanto en GET como en POST
    next_url = request.GET.get('next') or request.POST.get('next') or '/dashboard/'
    
    if request.method == "POST":
        form = EmailAuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"¡Bienvenido {user.first_name}!")
            return redirect(next_url)
        else:
            messages.error(request, "Credenciales inválidas. Intenta nuevamente")
    else: 
        form = EmailAuthenticationForm()

    return render(request, "login.html", {
        "form": form,
        "next": next_url
    })
    
def psicologo_required(view_func):
    """
    Decorador que permite el acceso sólo a usuarios autenticados
    cuyo campo `rol` sea 'psicologo'.
    """
    def check(user):
        return user.is_authenticated and user.rol == 'psicologo'
    return user_passes_test(
        check,
        login_url='/login',
        redirect_field_name=None
    )(view_func)

@never_cache
def logout_vista(request):
    
    logout(request)
    messages.info(request, "Sesión cerrada correctamente")
    return redirect('login')




