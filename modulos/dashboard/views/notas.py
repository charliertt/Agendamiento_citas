from .base_importaciones import (Respuesta, 
                                 render)
from .autenticacion import psicologo_required
@psicologo_required
def notas(request):
    notas = Respuesta.objects.all().order_by('id_respuesta')
    return render(request, 'notas.html', {'notas': notas,
                                           'active_page': 'notas',})