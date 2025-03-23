from .usuarios import (
    usuarios,
    crear_usuario,
    editar_usuario,
    eliminar_usuario
)


from .core import (
    dashboard
   
)

from .perfil import (
    perfil,       
    editar_perfil
)

from .autenticacion import (
    login_vista,
    logout_vista,)

from .registro import (
    registro_estudiante
)

from .verificar import (
    verificar_email,
    verificar_username,
    verificar_identificacion
)

from .contacto import (
    lista_contactos,
    responder_contacto
)

from .horarios import (
    horarios,
    crear_editar_horario,
    eliminar_horario
)

from .preguntas import (
    preguntas_tabla,
    crear_editar_pregunta,
    eliminar_pregunta
)

from .citas import (
    CitaCreateView,
    CitaListView,
    CitaUpdateView,
    CitaDeleteView
)