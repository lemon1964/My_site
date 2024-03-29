# Generated by Django 5.0.1 on 2024-01-28 11:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("posts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="author",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="posts",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="cat",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="posts",
                to="posts.category",
                verbose_name="Рубрика",
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="meta",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="metadata",
                to="posts.metadata",
                verbose_name="Метаданные",
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="tags",
            field=models.ManyToManyField(
                blank=True, related_name="tags", to="posts.tagpost", verbose_name="Теги"
            ),
        ),
        migrations.AddIndex(
            model_name="post",
            index=models.Index(
                fields=["-time_create"], name="posts_post_time_cr_e5aa17_idx"
            ),
        ),
    ]
