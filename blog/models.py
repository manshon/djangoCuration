import os
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import models
from django.utils import timezone


# サイト詳細情報のテーマカラーの選択肢
SITE_COLORS = (
    ('primary', '青色'),
    ('secondary', '灰色'),
    ('success', '緑色'),
    ('info', '水色'),
    ('warning', '黄色'),
    ('danger', '赤'),
    ('dark', '黒'),
)

DEFAULT_HEADER_TEXT = "paleolithic !!"


class Category(models.Model):
    """category"""
    name = models.CharField(max_length=255)

    def __str__(self):
        """ str. """
        return self.name


class Tag(models.Model):
    """ tag """
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField('本文')
    category = models.ForeignKey(Category, verbose_name="カテゴリー", on_delete=models.PROTECT)
    tag = models.ManyToManyField(Tag, blank=True, verbose_name="タグ")
    thumbnail = models.ImageField('サムネイル', upload_to='post_thumbnail/%Y/%m/%d/', blank=True, null=True)
    is_public = models.BooleanField('公開可否', default=True)
    friend_posts = models.ManyToManyField('self', verbose_name="関連記事", blank=True)
    description = models.TextField('記事の説明', blank=True)
    files = GenericRelation('File')
    created_at = models.DateTimeField('作成日', default=timezone.now)

    def __str__(self):
        return self.title

    def get_description(self):
        if self.description:
            return self.description
        else:
            description = "カテゴリ：{0}, タグ：{1}"
            category = self.category
            tags = ' '.join(tag.name for tag in self.tag.all())
            description = description.format(category, tags)
            return description

    def get_text(self):
        if len(self.text) >= 100:
            return self.text[:100] + '...'
        else:
            return self.text

    def get_next(self):
        """次の記事を取得する(日付)
        パフォーマンス的に、無駄が多い処理ですが、APIとして一応残しておきます。
        """
        next_post = Post.objects.filter(is_public=True, created_at__gt=self.created_at).order_by('-created_at')
        if next_post:
            return next_post.last()
        return None

    def get_prev(self):
        """前の記事を取得する(日付)
        パフォーマンス的に、無駄が多い処理ですが、APIとして一応残しておきます。
        """
        prev_post = Post.objects.filter(is_public=True, created_at__lt=self.created_at).order_by('-created_at')
        if prev_post:
            return prev_post.first()
        return None


class ContactMail(models.Model):
    """ contact mail"""
    name = models.CharField('名前', max_length=30)
    email = models.EmailField('Email')
    text = models.TextField('内容')
    created_at = models.DateTimeField('作成日', auto_now_add=True)

    def get_text(self):
        if len(self.text) >= 30:
            return self.text + '...'
        else:
            return self.text


class Comment(models.Model):
    """ comment """
    name = models.CharField('名前', max_length=20, default='名無し')
    text = models.TextField('コメント')
    icon = models.ImageField('サムネイル', upload_to='comment_thumbnail/%Y/%m/%d/', blank=True, null=True)
    target = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='対象記事')
    files = GenericRelation('File')
    created_at = models.DateTimeField('作成日', auto_now_add=True)

    def __str__(self):
        return self.text[:10]

    def get_filename(self):
        """ファイル名を取得する"""
        return os.path.basename(self.file.url)


class ReComment(models.Model):
    """ reComment"""
    name = models.CharField('名前', max_length=20, default='名無し')
    text = models.TextField('返信')
    icon = models.ImageField('サムネイル', upload_to='recomment_thumbnail/%Y/%m/%d/', blank=True, null=True)
    target = models.ForeignKey(Comment, on_delete=models.CASCADE, verbose_name='対象コメント')
    files = GenericRelation('File')
    created_at = models.DateTimeField('作成日', auto_now_add=True)

    def __str__(self):
        return self.text[:10]

    def get_filename(self):
        """ get filename"""
        return os.path.basename(self.file.url)


class Link(models.Model):
    """link"""
    name = models.CharField('リンク', max_length=255)
    adrs = models.CharField('アドレス', max_length=255)

    def __str__(self):
        return self.name


class Analytics(models.Model):
    """アナリティクスの情報"""
    name = models.CharField('アナリティクス', max_length=255, blank=True)
    html = models.TextField('アナリティクスHTML', blank=True)

    def __str__(self):
        return self.name


class Ads(models.Model):
    """広告関連"""
    name = models.CharField('広告名', max_length=255, blank=True)
    html = models.TextField('広告HTML', blank=True)

    def __str__(self):
        return self.name


class SiteDetail(models.Model):
    """サイトの詳細情報"""
    site = models.OneToOneField(Site, verbose_name='Site', on_delete=models.PROTECT)
    title = models.CharField('タイトル', max_length=255, default='タイトル')
    heaer_text = models.TextField('ヘッダーテキスト', max_length=255, default=DEFAULT_HEADER_TEXT)
    description = models.TextField('サイト説明', max_length=255, default="説明")
    author = models.CharField('管理人', max_length=255, default='muscle')
    author_mail = models.EmailField('メールアドレス', default="muscle@gmail.com")
    color = models.CharField('サイトテーマ色', choices=SITE_COLORS, default='primary', max_length=30)

    def __str__(self):
        return self.author


class PopularPost(models.Model):
    """人気記事"""
    title = models.CharField('タイトル', max_length=255)
    url = models.CharField('URL', max_length=255)
    page_view = models.ImageField('ページビュー数')

    def __str__(self):
        return "{} {} {}".format(self.url, self.title, self.page_view)


class Image(models.Model):
    """image file related to post"""
    title = models.CharField('タイトル', max_length=255)
    post = models.ForeignKey(Post, on_delete=models.PROTECT, verbose_name='記事')
    src = models.ImageField('画像', upload_to='images/%Y/%m/%d/', help_text='送信後、一度保存してください')
    created_at = models.DateTimeField('作成日', auto_now=True)

    def __str__(self):
        return '間接リンク:[filter imgpk]{0}[end] 直接リンク:[filter img]{1}[end]'.format(self.pk, self.src.url)


class File(models.Model):
    """記事やコメントに紐づく添付ファイル"""
    title = models.CharField('タイトル', max_length=255, blank=True)
    src = models.FileField('添付ファイル', upload_to='files/%Y/%m/%d/')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField('作成日', default=timezone.now)

    def __str__(self):
        return 'モデル:{} pk:{} url:{}'.format(self.content_type, self.object_id, self.src.url)

    def get_filename(self):
        """ファイル名を取得する"""
        return os.path.basename(self.src.url)

