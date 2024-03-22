from django.urls import path, re_path, register_converter
from . import views
from . import converters
from .feeds import LatestPostsFeed


register_converter(converters.FourDigitYearConverter, "year4")

urlpatterns = [
    path('', views.PostHome.as_view(), name='home'),  # http://127.0.0.1:8000
    path('about/', views.about, name='about'),
    path('addpage/', views.AddPage.as_view(), name='add_page'),
    path('post/<slug:post_slug>/', views.ShowPost.as_view(), name='post'),
    path('category/<slug:cat_slug>/', views.PostCategory.as_view(), name='category'),
    path('tag/<slug:tag_slug>/', views.TagPostList.as_view(), name='tag'),
    path('edit/<slug:slug>/', views.UpdatePage.as_view(), name='edit_page'),
    path('<int:post_id>/share/', views.PostShare.as_view(), name='post_share'),
    path('<int:post_id>/comments/', views.AddComment.as_view(), name='post_comments'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('search/', views.SearchResultsView.as_view(), name='post_search'),
    path('contact/', views.FeedBackView.as_view(), name='contact'),
    path('contact/success/', views.SuccessView.as_view(), name='success'),
]



# python3 manage.py runserver
# cd mysite

# python3 manage.py makemigrations
# python3 manage.py migrate
