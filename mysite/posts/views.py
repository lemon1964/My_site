from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView
from .utils import DataMixin
from .forms import AddPostForm, CommentForm, EmailPostForm, FeedBackForm, UploadFileForm, SearchForm
from .models import Category, Post, TagPost, UploadFiles, Comment
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail, BadHeaderError
from django.views.decorators.http import require_POST
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q


class PostHome(DataMixin, ListView):
    template_name = 'posts/index.html'
    context_object_name = 'posts'
    title_page = 'Главная страница'
    cat_selected = 0

    def get_queryset(self):
        return Post.published.all().select_related('cat')
 

@login_required
def about(request):
    contact_list = Post.published.all()
    paginator = Paginator(contact_list, 3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'posts/about.html',
                  {'title': 'О сайте', 'page_obj': page_obj})


class ShowPost(DataMixin, DetailView):
    template_name = 'posts/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=context['post'].title)

    def get_object(self, queryset=None):
        return get_object_or_404(Post.published, slug=self.kwargs[self.slug_url_kwarg])


class AddPage(PermissionRequiredMixin, LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'posts/addpage.html'
    title_page = 'Добавление статьи'
    permission_required = 'posts.add_post' # <приложение>.<действие>_<таблица>

    def form_valid(self, form):
        w = form.save(commit=False)
        w.author = self.request.user
        return super().form_valid(form)


class UpdatePage(PermissionRequiredMixin, DataMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'photo', 'is_published', 'cat']
    template_name = 'posts/addpage.html'
    success_url = reverse_lazy('home')
    title_page = 'Редактирование статьи'
    permission_required = 'posts.change_post'


class PostCategory(DataMixin, ListView):
    template_name = 'posts/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        return Post.published.filter(cat__slug=self.kwargs['cat_slug']).select_related("cat")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cat = context['posts'][0].cat
        return self.get_mixin_context(context,
                                      title='Категория - ' + cat.name,
                                      cat_selected=cat.pk,
                                      )


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


class TagPostList(DataMixin, ListView):
    template_name = 'posts/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = TagPost.objects.get(slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context, title='Тег: ' + tag.tag)

    def get_queryset(self):
        return Post.published.filter(tags__slug=self.kwargs['tag_slug']).select_related('cat')


class PostShare(FormView):
    template_name = 'posts/share.html'
    form_class = EmailPostForm
    
    def __init__(self, *args, **kwargs):
        self.sent = False
    
    def get_success_url(self):
        # Добавляем sent и email адрес в параметры запроса при редиректе
        email = self.request.POST.get('to')  # Получаем email адрес из POST запроса
        return reverse_lazy('post_share', kwargs={'post_id': self.kwargs['post_id']}) + f"?sent={self.sent}&to={email}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        context['post'] = post
        context['sent'] = self.sent 
        return context

    def form_valid(self, form):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        cd = form.cleaned_data
        
        if self.request.user.is_authenticated:
            cd['name'] = self.request.user.username
        
        post_url = self.request.build_absolute_uri(post.get_absolute_url())
        subject = f"{cd['name']} рекомендует ознакомиться со статьей {post.title}"
        message = f"Прочитайте {post.title} по ссылке {post_url}\n\n{cd['name']}, комментарий: {cd['comments']}"
        send_mail(subject, message, '', [cd['to']])
        
        # Устанавливаем флаг sent в True после успешной отправки
        self.sent = True
        return super().form_valid(form)


class AddComment(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'posts/comment_post.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        comments = post.comments.filter(active=True)  # Получаем список активных комментариев к этой статье
        context['post'] = post
        context['comments'] = comments  # Добавляем список комментариев в контекст
        return context

    def form_valid(self, form):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        comment = form.save(commit=False)
        comment.post = post
        comment.name = self.request.user.username  # Присваиваем имя пользователя комментарию
        comment.email = self.request.user.email  # Присваиваем почту пользователя комментарию
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        # Получаем идентификатор поста из параметров запроса
        post_id = self.kwargs.get('post_id')
        # Формируем URL для перенаправления к комментариям поста
        return reverse_lazy('post_comments', kwargs={'post_id': post_id})


class SearchResultsView(DataMixin, ListView):
    template_name = 'posts/search.html'
    context_object_name = 'results'
    cat_selected = 0

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Post.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).select_related('cat')
        else:
            return Post.published.all().select_related('cat')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        context['query'] = query
        context['total_results'] = self.get_queryset().count()
        return context
    # На главную при пустом запросе
    def dispatch(self, request, *args, **kwargs):
        if not self.request.GET.get('q'):
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    

# @permission_required(perm='posts.add_post', raise_exception=True)
# def contact(request):
#     return HttpResponse("Обратная связь")

class FeedBackView(View):
    def get(self, request, *args, **kwargs):
        form = FeedBackForm()
        return render(request, 'posts/contact.html', context={
            'form': form,
            'title': 'Написать мне'
        })

    def post(self, request, *args, **kwargs):
        form = FeedBackForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            try:
                send_mail(f'От {name} | Почта {from_email} | {subject}', message, '', ['lemon.design@mail.ru'])
            except BadHeaderError:
                return HttpResponse('Невалидный заголовок')
            return HttpResponseRedirect('success')
        return render(request, 'posts/contact.html', context={
            'form': form,
        })


class SuccessView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'posts/contact_success.html', context={
            'title': 'Спасибо'
        })

