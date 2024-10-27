from blog.constants import POSTS_ON_PAGE
from blog.forms import CommentForm, PostForm, ProfileEditForm
from blog.models import Category, Comment, Post, User
from blog.service import get_paginator, get_posts
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone


def index(request):
    """Главная страница."""
    post_list = get_posts(Post.objects).order_by('-pub_date')
    page_obj = get_paginator(request, post_list)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    """Полное описание выбранной записи."""
    posts = get_object_or_404(Post, id=post_id)
    if request.user != posts.author:
        posts = get_object_or_404(get_posts(Post.objects), id=post_id)
    comments = posts.comments.select_related('author')
    form = CommentForm()
    context = {'post': posts, 'form': form, 'comments': comments}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Публикация категории."""
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True)
    post_list = get_posts(category.posts).order_by(
        '-pub_date').select_related('author', 'location')
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

    posts_list = user.posts.all().select_related(
        "location", "category").prefetch_related("comments")

    # Считаем количество комментариев для каждого поста
    for post in posts_list:
        post.comment_count = post.comments.count()

    page_obj = get_paginator(request, posts_list)

    context = {
        'profile': user,
        'page_obj': page_obj,
        'comment_count': sum(post.comment_count for post in posts_list)  # Общее количество комментариев
    }
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
