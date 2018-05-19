from django import forms

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