from django import forms
from .models import Category, Comment, Metadata, Post, TagPost
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils.deconstruct import deconstructible
from captcha.fields import CaptchaField



@deconstructible
class RussianValidator:
    ALLOWED_CHARS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯабвгдеёжзийклмнопрстуфхцчшщбыъэюя0123456789- "
    code = 'russian'

    def __init__(self, message=None):
        self.message = message if message else "Должны присутствовать только русские символы, дефис и пробел."

    def __call__(self, value, *args, **kwargs):
        if not (set(value) <= set(self.ALLOWED_CHARS)):
            raise ValidationError(self.message, code=self.code)


class AddPostForm(forms.ModelForm):
    cat = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Категория не выбрана", label="Категории")
    meta = forms.ModelChoiceField(queryset=Metadata.objects.all(), empty_label="Не замужем", required=False, label="Муж")

    class Meta:
        model = Post
        fields = ['title', 'slug', 'content', 'photo', 'is_published', 'cat', 'meta', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'cols': 50, 'rows': 5}),
        }
        labels = {'slug': 'URL'}

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 100:
            raise ValidationError("Длина превышает 100 символов")

        return title


class UploadFileForm(forms.Form):
    file = forms.ImageField(label="Файл")
    
    
class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25, label="Ваше имя", required=False)
    to = forms.EmailField(label="E-mail получателя")
    comments = forms.CharField(required=False, widget=forms.Textarea, label="Комментарий")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EmailPostForm, self).__init__(*args, **kwargs)
        if self.user and self.user.is_authenticated:
            self.fields['name'].required = False


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 10}),
        }


class SearchForm(forms.Form):
    query = forms.CharField()
    
    

class FeedBackForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            # 'class': 'form-control',
            'id': 'name',
            'size': '30',
            # 'placeholder': "Ваше имя"
        })
    )
    email = forms.CharField(
        max_length=100,
        widget=forms.EmailInput(attrs={
            # 'class': 'form-control',
            'id': 'email',
            'size': '40',
            # 'placeholder': "Ваша почта"
        })
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            # 'class': 'form-control',
            'id': 'subject',
            'size': '60',
            # 'placeholder': "Тема"
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            # 'class': 'form-control md-textarea',
            'id': 'message',
            'rows': 10,
            'cols': 50,
            # 'placeholder': "Ваше сообщение"
        })
    )
    capatcha = CaptchaField()
