from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Blog
from django.contrib.auth.decorators import login_required
from .forms import BlogForm, CommentForm
from django.core.paginator import Paginator

def blog_list(request):
    blogs = Blog.objects.all().order_by('-created_at')
    paginator = Paginator(blogs, 5)  # 5 blogs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blogs/blog_list.html', {'page_obj': page_obj})

def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    comments = blog.comments.all()
    user = request.user

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = blog
            comment.author = request.user
            comment.save()
            return redirect('blog_detail', pk=pk)
    else:
        form = CommentForm()

    return render(request, 'blogs/blog_detail.html', {
        'blog': blog,
        'comments': comments,
        'form': form,
        'user': user,
    })


@login_required
def blog_create(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            return redirect('blog_list')
    else:
        form = BlogForm()
    return render(request, 'blogs/blog_form.html', {'form': form})


@login_required
def blog_update(request, pk):
    blog = get_object_or_404(Blog, pk=pk, author=request.user)

    # Check if the current user is the author
    if blog.author != request.user:
        messages.error(request, "You are not authorized to edit this blog.")
        return redirect('blog_detail', pk=pk)
    
    if request.method == 'POST':
        form = BlogForm(request.POST, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('blog_detail', pk=pk)
    else:
        form = BlogForm(instance=blog)
    return render(request, 'blogs/blog_form.html', {'form': form})


@login_required
def blog_delete(request, pk):
    blog = get_object_or_404(Blog, pk=pk, author=request.user)

    # Check if the current user is the author
    if blog.author != request.user:
        messages.error(request, "You are not authorized to edit this blog.")
        return redirect('blog_detail', pk=pk)
    
    if request.method == 'POST':
        blog.delete()
        return redirect('blog_list')
    return render(request, 'blogs/blog_confirm_delete.html', {'blog': blog})

