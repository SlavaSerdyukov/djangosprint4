from blog.constants import POSTS_ON_PAGE
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone


def get_posts(
    post_objects, count_comments=False,
    is_published_only=True, allow_unpublished=False
):
    """Получает и возвращает посты из БД."""
    if is_published_only:
        post_objects = post_objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )

    elif allow_unpublished:
        post_objects = post_objects.filter(
            category__is_published=True
        )

    if count_comments:
        post_objects = post_objects.annotate(
            comment_count=Count('comments')
        )

    return (
        post_objects
        .select_related('category', 'author')
        .order_by('-pub_date')
    )


def get_paginator(request, items, num=POSTS_ON_PAGE):
    """Создает объект пагинации."""
    return Paginator(items, num).get_page(request.GET.get('page'))
