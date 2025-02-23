from django import forms
from django.contrib.auth.forms import UserCreationForm
from modulos.dashboard.models import UsuarioPersonalizado, Horario, Psicologo, Preguntas, Estudiante, Cita
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import AuthenticationForm


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
        # ... widgets y demás código ...

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        # Si se está editando una instancia existente, formatear la fecha para el input datetime-local
        if self.instance and self.instance.pk and self.instance.fecha_hora:
<<<<<<< HEAD
            self.fields['fecha_hora'].initial = self.instance.fecha_hora.strftime('%Y-%m-%dT%H:%M')
=======
            self.fields['fecha_hora'].initial = self.instance.fecha_hora.strftime('%Y-%m-%dT%H:%M')


class EstudianteForm(UserCreationForm):
    class Meta:
        model = UsuarioPersonalizado
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'tipo_identificacion', 'identificacion'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'tipo_identificacion': forms.Select(attrs={'class': 'form-control'}),
            'identificacion': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'estudiante'  # Set rol to 'estudiante'
        if commit:
            user.save()
        return user
>>>>>>> d2d4302458e350eceb4484bc638c70d3f16e9517
