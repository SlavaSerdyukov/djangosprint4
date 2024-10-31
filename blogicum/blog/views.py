from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from blog.forms import CommentForm, PostForm, ProfileEditForm
from blog.models import Category, Comment, Post, User
from blog.service import get_paginator, get_posts


def index(request):
    """Главная страница."""
    post_list = get_posts(Post.objects, count_comments=True)
    page_obj = get_paginator(request, post_list)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    """Полное описание выбранной записи."""
    if request.user.is_authenticated:
        post = get_object_or_404(Post.objects, id=post_id)
    else:
        post = get_object_or_404(get_posts(Post.objects), id=post_id)
    if (
        request.user != post.author
        and (post.pub_date > timezone.now() or not post.is_published)
    ):
        raise Http404("Post not found")
    comments = post.comments.select_related('author')
    form = CommentForm()
    context = {'post': post, 'form': form, 'comments': comments}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Публикация категории."""
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True)
    post_list = get_posts(category.posts, count_comments=True)
    page_obj = get_paginator(request, post_list)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, 'blog/category.html', context)


@login_required
def create_post(request):
    """Создает новую запись."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', request.user.username)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


def profile(request, username):
    """Возвращает профиль пользователя."""
    user = get_object_or_404(User, username=username)
    posts_list = get_posts(user.posts, count_comments=True,
                           is_published_only=request.user != user)
    page_obj = get_paginator(request, posts_list)
    context = {'profile': user, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    """Редактирует профиль пользователя."""
    form = ProfileEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', request.user.username)
    context = {'form': form}
    return render(request, 'blog/user.html', context)


@login_required
def edit_post(request, post_id):
    """Редактирует запись блога."""
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_id):
    """Удаляет запись блога."""
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    if request.method == "POST":
        post.delete()
        return redirect('blog:profile', request.user.username)
    return render(request, 'blog/delete_confirmation.html', {'post': post})


@login_required
def add_comment(request, post_id):
    """Добавляет комментарий к записи."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирует комментарий."""
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {'form': form, 'comment': comment}
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаляет комментарий."""
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    if request.method == "POST":
        comment.delete()
        return redirect('blog:post_detail', post_id)
    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)
