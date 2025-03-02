from django import forms
from modulos.dashboard.models import UsuarioPersonalizado, Contacto
from django.contrib.auth.forms import UserCreationForm

class EstudianteForm(UserCreationForm):
    comentarios = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Comentarios adicionales (opcional)'}),
        label='Comentarios adicionales (opcional)'
    )

    class Meta:
        model = UsuarioPersonalizado
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'tipo_identificacion', 'identificacion', 'eps',
            'alergias', 'enfermedades'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'tipo_identificacion': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'identificacion': forms.TextInput(attrs={'class': 'form-control'}),
            'eps': forms.TextInput(attrs={'class': 'form-control'}),
            'alergias': forms.TextInput(attrs={'class': 'form-control'}),
            'enfermedades': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Si se pasa 'usuario_existente' como True, se omiten los campos de contraseña.
        usuario_existente = kwargs.pop('usuario_existente', False)
        super().__init__(*args, **kwargs)
        
        # Establecer valor por defecto para el select 'tipo_identificacion'
        # Asumimos que 'cedula' es el valor deseado por defecto
        self.fields['tipo_identificacion'].initial = 'cedula'
        
        if usuario_existente:
            self.fields.pop('password1', None)
            self.fields.pop('password2', None)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'estudiante'
        if commit:
            user.save()
        return user


class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = ['nombre', 'email', 'deseo', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu nombre'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu correo'}),
            'deseo': forms.Select(choices=Contacto.TIPO_OPCIONES, attrs={'class': 'form-control'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe tu mensaje aquí', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['deseo'].required = True
        # Establecer el valor por defecto para 'deseo' (ej.: 'peticion')
        self.fields['deseo'].initial = 'peticion'
