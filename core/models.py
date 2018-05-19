from django.db import models

# Create your models here.
from django.db import models
from user_auth.models import User
# Create your models here.


class Community(models.Model):
    name = models.CharField('コミュニティ名', max_length=30)
    description = models.TextField('コミュニティの説明')
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    is_public = models.BooleanField('公開非公開設定', default=True)
    stand_by_user = models.ManyToManyField(User, verbose_name='承認待ちのユーザー', related_name='stand_by_user', blank=True)
    permitted_user = models.ManyToManyField(User, verbose_name='許可されたユーザー', related_name='permitted_user', blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField('記事名', max_length=30)
    body = models.TextField('内容')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_admin_user')
    thumbnail = models.ImageField('サムネイル', upload_to='media/', blank=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, default=int)
    is_public = models.BooleanField('公開非公開設定', default=True)
    like_user = models.ManyToManyField(User, verbose_name='いいねしたユーザー', related_name='article_like_user',blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    def __str__(self):
        return self.title

    def summary(self):
        if len(self.body) < 150:
            return self.body
        else:
            return self.body[:150] + '...'


class Comment(models.Model):
    body = models.TextField('内容')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_admin_user')
    created_at = models.DateTimeField('投稿日時', auto_now_add=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comment_admin_article')
