from django import template
from posts.models import Category, TagPost
from django.db.models import Count
from posts.utils import menu


register = template.Library()

@register.simple_tag
def get_menu():
    return menu


@register.inclusion_tag('posts/list_categories.html')
def show_categories(cat_selected=0):
    cats = Category.objects.annotate(total=Count("posts")).filter(total__gt=0)
    return {'cats': cats, 'cat_selected': cat_selected}


@register.inclusion_tag('posts/list_tags.html')
def show_all_tags():
    return {'tags': TagPost.objects.annotate(total=Count("tags")).filter(total__gt=0)}

