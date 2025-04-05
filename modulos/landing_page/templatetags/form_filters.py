from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='readonly_crispy_field')
def readonly_crispy_field(field):
    # Crea una copia del campo para no modificar el original
    field.field.widget.attrs.update({'readonly': 'readonly'})
    return field