from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from modulos.dashboard.models import UsuarioPersonalizado, Horario, Psicologo, Preguntas, Estudiante, Cita
from django.core.exceptions import ObjectDoesNotExist


class UsuarioPersonalizadoCreationForm(UserCreationForm):
    # Campo extra para psicólogos (puedes mantener o adaptar según tus necesidades)
    especializacion = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control campo-psicologo hidden'})
    )

    class Meta:
        model = UsuarioPersonalizado
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'tipo_identificacion', 'identificacion', 'rol',
            'imagen', 'especializacion', 'eps', 'alergias',
            'enfermedades'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'tipo_identificacion': forms.Select(attrs={'class': 'form-control'}),
            'identificacion': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control', 'id': 'id_rol'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
            'eps': forms.TextInput(attrs={'class': 'form-control'}),
            'alergias': forms.TextInput(attrs={'class': 'form-control'}),
            'enfermedades': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer valores por defecto para los selects
        self.fields['tipo_identificacion'].initial = 'cedula'
        self.fields['rol'].initial = 'estudiante'

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()  # Primero se guarda el usuario
            # Crear objeto en el modelo correspondiente según el rol
            if user.rol == 'psicologo':
                Psicologo.objects.create(
                    usuario=user,
                    especializacion=self.cleaned_data['especializacion']
                )
            elif user.rol == 'estudiante':
                Estudiante.objects.create(
                    usuario=user
                )
        return user

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        especializacion = cleaned_data.get('especializacion')

        if rol == 'psicologo' and not especializacion:
            self.add_error('especializacion', 'Este campo es requerido para psicólogos')
        elif rol != 'psicologo':
            cleaned_data['especializacion'] = None  # Limpiar campo si no aplica

        return cleaned_data


class UsuarioPersonalizadoEditForm(forms.ModelForm):
    especializacion = forms.CharField(required=False)

    class Meta:
        model = UsuarioPersonalizado
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'tipo_identificacion', 'identificacion',
            'eps', 'alergias', 'enfermedades',
            'imagen', 'rol', 'especializacion',
        ]
        # Puedes agregar aquí los widgets y demás configuraciones

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asignar valores por defecto en caso de que la instancia no tenga asignado el campo
        if not self.instance.tipo_identificacion:
            self.fields['tipo_identificacion'].initial = 'cedula'
        if not self.instance.rol:
            self.fields['rol'].initial = 'estudiante'
        # Verificar si existe psicólogo sin usar la relación inversa
        if self.instance.pk:
            psicologo = Psicologo.objects.filter(usuario=self.instance).first()
            self.fields['especializacion'].initial = psicologo.especializacion if psicologo else ''

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        especializacion = cleaned_data.get('especializacion')
        
        if rol == 'psicologo' and not especializacion:
            self.add_error('especializacion', 'Requerido para psicólogos')
        
        return cleaned_data


class EmailAuthenticationForm(AuthenticationForm):
    # Sobreescribimos el campo username para que sea de tipo EmailField y se muestre como "Correo Electrónico"
    username = forms.EmailField(label="Correo Electrónico", max_length=254)


class HorarioForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)
        # Establecer 'Lunes' como valor por defecto para el select de día de la semana
        self.fields['dia_semana'].initial = 'Lunes'
    
    class Meta:
        model = Horario
        fields = ['psicologo', 'dia_semana', 'hora_inicio', 'hora_fin', 'disponible']
        widgets = {
            'psicologo': forms.Select(attrs={'class': 'form-control'}),
            'dia_semana': forms.Select(attrs={'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class PreguntasForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer 'ANS' (Ansiedad) como valor por defecto
        self.fields['categoria'].initial = 'ANS'
    
    class Meta:
        model = Preguntas
        fields = ['categoria', 'pregunta', 'respuesta']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'pregunta': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Pregunta'}),
            'respuesta': forms.NullBooleanSelect(attrs={'class': 'form-control'})
        }


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['fecha_hora', 'estudiante', 'psicologo', 'asunto', 'estado', 'notas']
        widgets = {
            'fecha_hora': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                },
                format='%Y-%m-%dT%H:%M'  # Formato que espera el input datetime-local
            ),
            'estudiante': forms.Select(attrs={'class': 'form-control'}),
            'psicologo': forms.Select(attrs={'class': 'form-control'}),
            'asunto': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Comentarios adicionales (opcional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Para una instancia nueva, asignar el estado por defecto 'agendada'
        if not self.instance.pk:
            self.fields['estado'].initial = 'agendada'
        # Si se está editando una instancia existente, formatear la fecha para el input datetime-local
        if self.instance and self.instance.pk and self.instance.fecha_hora:
            self.fields['fecha_hora'].initial = self.instance.fecha_hora.strftime('%Y-%m-%dT%H:%M')


class EstudianteForm(UserCreationForm):
    last_name = forms.CharField(
        validators=[RegexValidator(
            regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$',
            message='El apellido solo debe contener letras.'
        )],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = UsuarioPersonalizado
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'tipo_identificacion', 'identificacion', 'password1', 'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'tipo_identificacion': forms.Select(attrs={'class': 'form-control'}),
            'identificacion': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Forzar que los campos de contraseña tengan la clase 'form-control'
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        # Establecer 'cedula' como valor por defecto para tipo_identificacion
        self.fields['tipo_identificacion'].initial = 'cedula'

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'estudiante'
        if commit:
            user.save()
            from modulos.dashboard.models import Estudiante  
            Estudiante.objects.create(usuario=user)
        return user


class RespuestaForm(forms.Form):
    respuesta = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}),
        label="Respuesta"
    )
