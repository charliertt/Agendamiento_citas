from .base_importaciones import (Respuesta, 
                                 render)


def notas(request):
    notas = Respuesta.objects.all().order_by('id_respuesta')
    return render(request, 'notas.html', {'notas': notas})