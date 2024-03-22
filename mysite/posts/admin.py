from django.contrib import admin, messages
from .models import Comment, Post, Category, TagPost, Metadata
from django.utils.safestring import mark_safe

# Фильтр по метаданным, если они есть
class MetadataFilter(admin.SimpleListFilter):
    title = "Наличие метаданных"
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('yes', 'есть метаданные'),
            ('no', 'нет метаданных'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(meta__isnull=False)
        elif self.value() == 'no':
            return queryset.filter(meta__isnull=True)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    fields = ['title', 'slug', 'content', 'photo', 'post_photo', 'cat', 'meta', 'tags'] # Поля для редактирования в порядке вывода
    # exclude = ['tags', 'is_published'] # Исключаемые поля, антоним fields
    readonly_fields = ['slug', 'post_photo']    # Только для чтения, нельзя редактировать
    # prepopulated_fields = {"slug": ("title", )} # Автозаполнение поля slug, нельзя сочетать вместе с readonly_fields
    # filter_horizontal = ['tags']  # Связанные таблицы
    filter_vertical = ['tags']  # Связанные таблицы
    list_display = ('title', 'post_photo', 'time_create', 'is_published', 'cat') # Отображаемые поля
    list_display_links = ('title', ) # Кликабельные поля
    ordering = ['-time_create', 'title'] # Сортировка
    list_editable = ('is_published', ) # Редактируемые поля
    list_per_page = 10  # Кол-во постов на странице, пагинация
    actions = ['set_published', 'set_draft'] # Действия над выбранными записями в админке
    search_fields = ['title__startswith', 'cat__name'] # Поиск по названию и рубрике
    list_filter = [MetadataFilter, 'cat__name', 'is_published']
    save_on_top = True
    
    # доп поле в дисплее админки
    @admin.display(description="Изображение", ordering='content')
    def post_photo(self, posts: Post):
        if posts.photo:
            return mark_safe(f"<img src='{posts.photo.url}' width=50>")
        return "Без фото"

    # действия над выбранными записями
    @admin.action(description="Опубликовать выбранные записи")
    def set_published(self, request, queryset):
        count = queryset.update(is_published=Post.Status.PUBLISHED)
        self.message_user(request, f"Изменено {count} записей.")

    @admin.action(description="Снять с публикации выбранные записи")
    def set_draft(self, request, queryset):
        count = queryset.update(is_published=Post.Status.DRAFT)
        self.message_user(request, f"{count} записей сняты с публикации!", messages.WARNING)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name')
    prepopulated_fields = {"slug": ("name", )}

@admin.register(Metadata)
class MetadataAdmin(admin.ModelAdmin):
    list_display = ('id', 'views', 'likes', 'shares')
    list_display_links = ('id', 'views', 'likes', 'shares')


@admin.register(TagPost)
class TagPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'slug')
    list_display_links = ('id', 'tag')
    prepopulated_fields = {"slug": ("tag", )}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['name', 'email', 'body']
    
    
# admin.site.register(Post)

