from django import forms
from django.db.models import Q

from .models import Comment, Community, Article


class ArticleCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = (
            'body',
        )


class ArticleCreateForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = (
            'title',
            'body',
            'thumbnail',
            'is_public',
        )


class ArticleEditForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = (
            'title',
            'body',
            'thumbnail',
            'is_public',
        )


# 記事のタイトルか中身にキーワードを含むものを返す
def search_articles(keyword):
    return Article.objects.filter(Q(title__contains=keyword) | Q(body__contains=keyword))


class ArticleSearchForm(forms.ModelForm):
    search_word = forms.CharField(label='検索ワード')

    class Meta:
        model = Article
        fields = ()


class CommunityCreateForm(forms.ModelForm):

    class Meta:
        model = Community
        fields = (
            'name',
            'description',
        )


class CommunityEditForm(forms.ModelForm):

    class Meta:
        model = Community
        fields = (
            'name',
            'description',
        )