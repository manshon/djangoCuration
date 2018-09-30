from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sitemaps import ping_google
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from .forms import PostSearchForm, CommentCreateForm, ReCommentCreateForm, FileInlineFormSet, ContactMeCreateForm
from .models import Post, Comment, Tag, Category, ReComment, File, ContactMail


class BaseListView(generic.ListView):
    """記事の一覧表示の基底クラス"""
    paginate_by = 10

    def get_queryset(self):
        """公開フラグがTrue、作成日順の記事を返す"""
        # post.categoryや、post.tag.allをテンプレートで書く場合は
        # それぞれselect_relatedやprefetch_relatedで改善できる場合があります。
        query_set = Post.objects.filter(
            is_public=True
        ).order_by('-created_at').select_related('category').prefetch_related('tag')
        return query_set


class PostIndexView(BaseListView):
    """トップページ"""

    def get_queryset(self):
        """クイックサーチの絞り込み"""
        global_form = PostSearchForm(self.request.GET)
        global_form.is_valid()
        keyword = global_form.cleaned_data['keyword']
        queryset = super().get_queryset()

        if keyword:
            for word in keyword.split():
                queryset = queryset.filter(
                    Q(title__icontains=word) | Q(text__icontains=word)
                )
        return queryset


class PostPrivateIndexView(LoginRequiredMixin, BaseListView):
    """非公開の記事一覧"""

    def get_queryset(self):
        """公開フラグがFalse、作成日順"""
        queryset = Post.objects.filter(
            is_public=False
        ).order_by('-created_at').select_related('category').prefetch_related('tag')
        return queryset


class CategoryView(BaseListView):
    """click link of categories"""

    def get_queryset(self):
        """カテゴリの絞り込み"""
        category_name = self.kwargs['category']
        self.category = Category.objects.get(name=category_name)
        query_set = super().get_queryset().filter(category=self.category)
        return query_set

    def get_context_data(self, *args, **kwargs):
        """クリックされたカテゴリを保持"""
        context = super().get_context_data(*args, **kwargs)
        context['category'] = self.category
        return context


class TagView(BaseListView):
    """タグのリンククリック"""

    def get_queryset(self):
        tag_name = self.kwargs['tag']
        self.tag = Tag.objects.get(name=tag_name)
        query_set = super().get_queryset().filter(tag=self.tag)
        return query_set

    def get_context_data(self, *args, **kwargs):
        """クリックされたタグを保持"""
        context = super().get_context_data(*args, **kwargs)
        context['tag'] = self.tag
        return context


class PostDetailView(generic.DetailView):
    """記事詳細ページ"""
    model = Post

    def get_object(self, query_set=None):
        """その記事が公開か、ユーザがログインしていればよし"""
        post = super().get_object()
        if post.is_public or self.request.user.is_authenticated:
            return post
        else:
            return Http404


class ContactMeCreateView(generic.CreateView):
    """ダイレクトメールを送る画面"""
    form_class = ContactMeCreateForm
    template_name = 'blog/contact_me_form.html'
    success_url = reverse_lazy('blog:thanks')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ThanksView(generic.TemplateView):
    template_name = 'blog/thank.html'


class ContactMailListView(generic.ListView):
    paginate_by = 20
    template_name = 'blog/contact_mail.html'
    context_object_name = 'mail_list'

    def get_queryset(self):
        mail = ContactMail.objects.all().order_by('-created_at')
        return mail


class ContactMailDetailView(generic.DetailView):
    model = ContactMail
    template_name = 'blog/contact_mail_detail.html'
    context_object_name = 'mail'

    def get_object(self, query_set=None):
        mail = super().get_object()
        if self.request.user.is_authenticated:
            return mail
        else:
            return Http404


class CommentCreateView(generic.CreateView):
    """コメント投稿画面
    '^comment/(?P<pk>[0-9]+)/$'のようにして、記事のpkも受け取っている
    このpkをcontextへ渡し前へ戻るリンクに利用したり、targetに指定する記事を取得するのに使う
    """
    model = Comment
    form_class = CommentCreateForm

    def form_valid(self, form):
        """記事をコメントのターゲットに指定"""
        comment = form.save(commit=False)
        post_pk = self.kwargs['pk']
        comment.target = Post.objects.get(id=post_pk)
        comment.save()
        formset = FileInlineFormSet(self.request.POST, instance=comment, files=self.request.FILES)
        if formset.is_valid():
            formset.save()
        return redirect('blog:detail', pk=post_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['pk'])
        if 'formset' not in context:
            context['formset'] = FileInlineFormSet(self.request.POST or None)
        return context


class ReCommentCreateView(generic.CreateView):
    """返信コメント投稿"""

    model = ReComment
    form_class = ReCommentCreateForm
    template_name = 'blog/comment_form.html'

    def form_valid(self, form):
        comment_pk = self.kwargs['pk']
        comment = Comment.objects.get(pk=comment_pk)
        recomment = form.save(commit=False)
        recomment.target = comment
        recomment.save()

        formset = FileInlineFormSet(self.request.POST, instance=recomment, files=self.request.FILES)
        if formset.is_valid():
            formset.save()
        return redirect('blog:detail', pk=comment.target.pk)

    def get_context_data(self, **kwargs):
        comment_pk = self.kwargs['pk']
        comment = Comment.objects.get(pk=comment_pk)
        context = super().get_context_data(**kwargs)
        context['post'] = comment.target
        if 'formset' not in context:
            context['formset'] = FileInlineFormSet(self.request.POST or None)
        return context


class TagListView(generic.ListView):
    """タグの一覧ビュー"""

    model = Tag
    queryset = Tag.objects.annotate(
        num_posts=Count('post')).order_by('-num_posts')


@login_required
def ping(request):
    """Googleにpingを送信する"""
    try:
        url = reverse_lazy('blog:sitemap')
        ping_google(sitemap_url=url)
    except Exception:
        raise
    else:
        return redirect('blog:index', permanent=True)


def file_download(request, pk):
    """コメントに添付されたファイルのダウンロード
    ユーザーがアップロードできるファイルなので、セキュリティ対策のため
    必ずブラウザ上で開かせず、ダウンロードさせるようにする
    """
    file = get_object_or_404(File, pk=pk)
    response = HttpResponse(file.src, content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(file.get_filename())
    return response
