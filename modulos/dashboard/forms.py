from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UsuarioPersonalizado

class UsuarioPersonalizadoCreationForm(UserCreationForm):
    especializacion = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control campo-psicologo hidden'})
    )
    horarios_disponibles = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control campo-psicologo hidden'})
    )
    
    class Meta:
        model = UsuarioPersonalizado
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'tipo_identificacion', 'identificacion', 'rol',
            'imagen', 'especializacion', 'horarios_disponibles'
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
        }

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        
        if rol == 'psicologo':
            especializacion = cleaned_data.get('especializacion')
            horarios_disponibles = cleaned_data.get('horarios_disponibles')
            
            if not especializacion:
                self.add_error('especializacion', 'Este campo es requerido para psicólogos')
            if not horarios_disponibles:
                self.add_error('horarios_disponibles', 'Este campo es requerido para psicólogos')
                
        return cleaned_data
