from django import forms
from modulos.dashboard.models import UsuarioPersonalizado
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
            'tipo_identificacion': forms.Select(attrs={'class': 'form-control'}),
            'identificacion': forms.TextInput(attrs={'class': 'form-control'}),
            'eps': forms.TextInput(attrs={'class': 'form-control'}),
            'alergias': forms.TextInput(attrs={'class': 'form-control'}),
            'enfermedades': forms.TextInput(attrs={'class': 'form-control'}), 
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'estudiante'  # Set rol to 'estudiante'
        if commit:
            user.save()
        return user

