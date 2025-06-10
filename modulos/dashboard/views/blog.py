from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .base_importaciones import (
     Blog, BlogForm
)
from .autenticacion import psicologo_required



@psicologo_required
def blog_listado(request):
    blogs = Blog.objects.all()
    return render(request, 'blog_listado.html', {'blogs': blogs, 'active_page': 'blog'})

@psicologo_required
def blog_create(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.autor = request.user.psicologo  
            blog.save()
            messages.success(request, 'Blog creado exitosamente.')
            return redirect('blog_listado')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = BlogForm()
    
    return render(request, 'blog_form.html', {'form': form})

@psicologo_required
def blog_edit(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog actualizado exitosamente.')
            return redirect('blog_listado')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = BlogForm(instance=blog)
    
    return render(request, 'blog_form.html', {'form': form, 'blog': blog})