# Generated by Django 2.0.4 on 2018-05-19 06:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='admin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='community',
            name='permitted_user',
            field=models.ManyToManyField(blank=True, related_name='permitted_user', to=settings.AUTH_USER_MODEL, verbose_name='許可されたユーザー'),
        ),
        migrations.AddField(
            model_name='community',
            name='stand_by_user',
            field=models.ManyToManyField(blank=True, related_name='stand_by_user', to=settings.AUTH_USER_MODEL, verbose_name='承認待ちのユーザー'),
        ),
        migrations.AddField(
            model_name='comment',
            name='admin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_admin_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_admin_article', to='core.Article'),
        ),
        migrations.AddField(
            model_name='article',
            name='admin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_admin_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='article',
            name='community',
            field=models.ForeignKey(default=int, on_delete=django.db.models.deletion.CASCADE, to='core.Community'),
        ),
        migrations.AddField(
            model_name='article',
            name='like_user',
            field=models.ManyToManyField(blank=True, related_name='article_like_user', to=settings.AUTH_USER_MODEL, verbose_name='いいねしたユーザー'),
        ),
    ]