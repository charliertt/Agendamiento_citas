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

@never_cache
def logout_vista(request):
    logout(request)
    messages.info(request, "Sesión cerrada correctamente")
    return redirect('login')




