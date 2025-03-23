# En registro.py
from .base_importaciones import (
    never_cache,
    render,
    redirect,
    messages,
    EstudianteForm
)

@never_cache
def registro_estudiante(request):
    if request.user.is_authenticated:
        messages.warning(request, "Ya tienes una sesión activa")
        return redirect('dashboard')
    step = 1

    if request.method == 'POST':
        estudiante_form = EstudianteForm(request.POST)
        
        # Si el usuario viene del botón "Siguiente Paso 2" o "Siguiente Paso 3"
        # (ver más abajo en el template los name="step" value="2" / "3")
        step = int(request.POST.get('step', 1))
        
        # Si el paso actual es 3 y se presionó "Crear cuenta", intentamos validar todo
        if step == 3:
            if estudiante_form.is_valid():
                estudiante_form.save()
                return redirect('dashboard')
            else:
                # Si hay errores en contraseña, forzamos a que se muestre step=3
                if estudiante_form.errors.get('password1') or estudiante_form.errors.get('password2'):
                    step = 3
                # Si hay errores en campos del Paso 2, volvemos al Paso 2
                elif any(field in estudiante_form.errors for field in [
                    'username','first_name','last_name','tipo_identificacion','identificacion'
                ]):
                    step = 2
                # Si hay errores en el email, volvemos al Paso 1
                elif estudiante_form.errors.get('email'):
                    step = 1
        else:
            # En pasos 1 o 2 podrías hacer validaciones parciales, 
            # o simplemente dejar que el usuario pase y al final se valide todo en step=3.
            # Si quieres validación parcial, puedes hacer algo como:
            
            if estudiante_form.is_valid():
                # Si no hay errores, avanzamos de paso
                step += 1
            else:
                # Dependiendo de qué campos fallan, retrocedes al paso que corresponda
                if any(field in estudiante_form.errors for field in ['email']):
                    step = 1
                elif any(field in estudiante_form.errors for field in [
                    'username','first_name','last_name','tipo_identificacion','identificacion'
                ]):
                    step = 2
                # Y si las contraseñas fallan (raro que pase en step 1/2, pero por si acaso)
                elif estudiante_form.errors.get('password1') or estudiante_form.errors.get('password2'):
                    step = 3

    else:
        # Si es GET, sólo inicializa el formulario
        estudiante_form = EstudianteForm()

    return render(request, 'registro_estudiante.html', {
        'estudiante_form': estudiante_form,
        'step': step
    }) 
 