from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .base_importaciones import (
    Blog, Psicologo, BlogForm
)

@method_decorator(login_required, name='dispatch')
class PsicologoBlogListView(ListView):
    """Vista para mostrar los blogs del psicólogo actual"""
    model = Blog
    template_name = 'blog/psicologo/blog_list.html'
    context_object_name = 'blogs'
    
    def get_queryset(self):
        # Filtrar blogs por el psicólogo actual
        try:
            psicologo = Psicologo.objects.get(usuario=self.request.user)
            return Blog.objects.filter(autor=psicologo)
        except Psicologo.DoesNotExist:
            return Blog.objects.none()


@method_decorator(login_required, name='dispatch')
class BlogCreateView(CreateView):
    """Vista para crear un nuevo blog"""
    model = Blog
    form_class = BlogForm
    template_name = 'blog/psicologo/blog_form.html'
    success_url = reverse_lazy('psicologo_blog_list')
    
    def form_valid(self, form):
        try:
            psicologo = Psicologo.objects.get(usuario=self.request.user)
            form.instance.autor = psicologo
            messages.success(self.request, 'Blog creado correctamente.')
            return super().form_valid(form)
        except Psicologo.DoesNotExist:
            messages.error(self.request, 'No tienes permiso para crear blogs.')
            return redirect('home')


@method_decorator(login_required, name='dispatch')
class BlogUpdateView(UpdateView):
    """Vista para actualizar un blog existente"""
    model = Blog
    form_class = BlogForm
    template_name = 'blog/psicologo/blog_form.html'
    success_url = reverse_lazy('psicologo_blog_list')
    
    def get_queryset(self):
        # Verificar que el blog pertenezca al psicólogo actual
        try:
            psicologo = Psicologo.objects.get(usuario=self.request.user)
            return Blog.objects.filter(autor=psicologo)
        except Psicologo.DoesNotExist:
            return Blog.objects.none()
    
    def form_valid(self, form):
        messages.success(self.request, 'Blog actualizado correctamente.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class BlogDeleteView(DeleteView):
    """Vista para eliminar un blog"""
    model = Blog
    template_name = 'blog/psicologo/blog_confirm_delete.html'
    success_url = reverse_lazy('psicologo_blog_list')
    
    def get_queryset(self):
        # Verificar que el blog pertenezca al psicólogo actual
        try:
            psicologo = Psicologo.objects.get(usuario=self.request.user)
            return Blog.objects.filter(autor=psicologo)
        except Psicologo.DoesNotExist:
            return Blog.objects.none()
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Blog eliminado correctamente.')
        return super().delete(request, *args, **kwargs)


# Vistas públicas
class BlogListView(ListView):
    """Vista para mostrar todos los blogs publicados"""
    model = Blog
    template_name = 'blog/blog_list.html'
    context_object_name = 'blogs'
    
    def get_queryset(self):
        # Solo mostrar blogs publicados
        return Blog.objects.filter(publicado=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar conteo de blogs por categoría
        categorias = {}
        for codigo, nombre in Blog.CATEGORIAS:
            count = Blog.objects.filter(publicado=True, categoria=codigo).count()
            categorias[codigo] = {'nombre': nombre, 'count': count}
        context['categorias'] = categorias
        return context


class BlogDetailView(DetailView):
    """Vista para mostrar un blog específico"""
    model = Blog
    template_name = 'blog/blog_detail.html'
    context_object_name = 'blog'
    
    def get_queryset(self):
        # Solo mostrar blogs publicados o si el autor es el usuario actual
        queryset = Blog.objects.filter(publicado=True)
        if self.request.user.is_authenticated:
            try:
                psicologo = Psicologo.objects.get(usuario=self.request.user)
                # Unir los blogs publicados con los del autor actual (aunque no estén publicados)
                autor_queryset = Blog.objects.filter(autor=psicologo, publicado=False)
                return queryset | autor_queryset
            except Psicologo.DoesNotExist:
                pass
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar blogs recientes para el sidebar
        context['blogs_recientes'] = Blog.objects.filter(publicado=True).exclude(id=self.object.id)[:5]
        return context


class BlogCategoryView(ListView):
    """Vista para mostrar blogs por categoría"""
    model = Blog
    template_name = 'blog/blog_list.html'
    context_object_name = 'blogs'
    
    def get_queryset(self):
        # Filtrar blogs por categoría
        categoria = self.kwargs.get('categoria')
        return Blog.objects.filter(publicado=True, categoria=categoria)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar conteo de blogs por categoría
        categorias = {}
        for codigo, nombre in Blog.CATEGORIAS:
            count = Blog.objects.filter(publicado=True, categoria=codigo).count()
            categorias[codigo] = {'nombre': nombre, 'count': count}
        context['categorias'] = categorias
        
        # Agregar nombre de la categoría actual
        categoria_actual = self.kwargs.get('categoria')
        for codigo, nombre in Blog.CATEGORIAS:
            if codigo == categoria_actual:
                context['categoria_actual'] = nombre
                break
        
        return context
