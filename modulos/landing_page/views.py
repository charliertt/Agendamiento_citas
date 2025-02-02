from django.shortcuts import render, redirect
from modulos.dashboard.models import Preguntas

# Create your views here.
def index(request):
    
    return render(request, 'index.html')
def blog(request):
    
    return render(request, 'blog.html')

def preguntas(request):
    
    preguntas = Preguntas.objects.all()
    return render(request, 'preguntas.html', {'preguntas': preguntas})



def validar_pregunta(request):
    if request.method == 'POST':
        preguntas = Preguntas.objects.all()
        respuestas_correctas = 0
        total_preguntas = preguntas.count()

        for pregunta in preguntas:
            respuesta_usuario = request.POST.get(f"respuesta_{pregunta.id_pregunta}")

            if respuesta_usuario:
                if respuesta_usuario == 'True' and pregunta.respuesta:
                    respuestas_correctas += 1
                elif respuesta_usuario == 'False' and not pregunta.respuesta:
                    respuestas_correctas += 1

        # Calculamos el porcentaje de respuestas correctas
        porcentaje = (respuestas_correctas / total_preguntas) * 100

        # Mostrar los resultados en la consola (para depuración)
        print(f"respuestas correctas: {respuestas_correctas}")
        print(f"total preguntas: {total_preguntas}")
        print(f"porcentaje: {porcentaje}")

        return render(request, 'preguntas.html', {'preguntas': preguntas, 
                                                  'respuestas_correctas': respuestas_correctas, 
                                                  'total_preguntas': total_preguntas, 
                                                  'porcentaje': porcentaje})  
    else:
        return redirect('preguntas')  
