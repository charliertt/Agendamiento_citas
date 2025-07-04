# Generated by Django 5.1.6 on 2025-05-06 02:53

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0016_blog'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='cita_destacada',
            field=models.TextField(blank=True, help_text='Una cita o frase destacada que aparecerá en blockquote', null=True, verbose_name='Cita destacada'),
        ),
        migrations.AlterField(
            model_name='blog',
            name='categoria',
            field=models.CharField(choices=[('ansiedad', 'Ansiedad'), ('depresion', 'Depresión'), ('terapia', 'Terapia'), ('neurociencia', 'Neurociencia'), ('psicologia_positiva', 'Psicología Positiva'), ('desarrollo_personal', 'Desarrollo Personal'), ('otros', 'Otros')], default='otros', max_length=50, verbose_name='Categoría'),
        ),
        migrations.AlterField(
            model_name='blog',
            name='contenido',
            field=ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Contenido del Blog'),
        ),
        migrations.AlterField(
            model_name='blog',
            name='fecha_actualizacion',
            field=models.DateTimeField(auto_now=True, verbose_name='Última Actualización'),
        ),
        migrations.AlterField(
            model_name='blog',
            name='fecha_creacion',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación'),
        ),
        migrations.AlterField(
            model_name='blog',
            name='imagen_principal',
            field=models.ImageField(blank=True, null=True, upload_to='blog_images/', verbose_name='Imagen Principal'),
        ),
        migrations.AlterField(
            model_name='blog',
            name='publicado',
            field=models.BooleanField(default=False, help_text='Marcar para publicar el blog', verbose_name='Publicado'),
        ),
    ]
