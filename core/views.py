from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .models import Article, Community, Comment
from user_auth.models import User
from .forms import (
    ArticleCommentForm, ArticleCreateForm, ArticleEditForm, CommunityCreateForm, CommunityEditForm, ArticleSearchForm,
    search_articles
)

# Create your views here.


def home(request):
    community_id = request.GET.get('community_id', 1)
    if not community_id:
        community_id = 1
    # community = get_object_or_404(Community, id=community_id)
    # articles = community.articles.order_by('-updated_at')

    # return render(request, 'core/home.html',
    #               {'community': community,
    #                'articles': articles})
    return HttpResponseRedirect(reverse('core:real_home', args=(community_id,)))


@login_required
def real_home(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    permitted_communities = []
    admin_communities = []
    community_all = Community.objects.all()
    for com in community_all:
        if request.user in com.permitted_user.all():
            permitted_communities.append(com)
        if request.user.id == com.admin_id:
            admin_communities.append(com)

    articles = Article.objects.filter(community_id=community_id, is_public=True).order_by('-updated_at')
    # articles = community.articles.filter(is_public=True).order_by('-updated_at')

    article_search_form = ArticleSearchForm(request.GET)
    if article_search_form.is_valid():
        search_word = article_search_form.cleaned_data['search_word']
        articles = search_articles(search_word)

    params = request.GET.copy()
    if 'page' in params:
        page = params['page']
        del params['page']
    else:
        page = 1
    search_params = params.urlencode()

    paginator = Paginator(articles, 6)
    try:
        articles = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        articles = paginator.page(1)

    return render(request, 'core/home.html',
                  {'community': community,
                   'articles': articles,
                   'permitted_communities': permitted_communities,
                   'admin_communities': admin_communities,
                   'article_search_form': article_search_form,
                   'search_params': search_params})


@login_required
def article_detail(request,community_id, article_id):
    article = get_object_or_404(Article, id=article_id)
    comments = Comment.objects.filter(article_id=article.id)
    if request.method == 'POST':
        form = ArticleCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.admin_id = request.user.id
            comment.article_id = article.id
            comment.save()

        return HttpResponseRedirect(reverse('core:article_detail', args=(community_id, article_id,)))
    else:
        comment_paginator = Paginator(comments, 10)
        page = request.GET.get('page')
        try:
            comments = comment_paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            comments = comment_paginator.page(1)

        form = ArticleCommentForm()
        return render(request, 'core/article_detail.html',
                  {'article': article,
                   'form': form,
                   'comments': comments,
                   'community_id': community_id})


@login_required
def article_create(request, community_id):
    community = get_object_or_404(Community, id=community_id)

    if request.method == 'POST':
        form = ArticleCreateForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.community_id = community_id
            article.admin_id = request.user.id
            article.save()

        return HttpResponseRedirect(reverse('core:real_home', args=(community_id,)))
    else:
        form = ArticleCreateForm()
        return render(request, 'core/article_create.html',
                      {'form': form,
                       'community_id': community_id})


@login_required
def article_edit(request, community_id, article_id):
    article = get_object_or_404(Article, id=article_id)
    if article.admin_id != request.user.id:
        error = '権限がありません'
        return render(request, 'core/error.html',
                      {'error': error})

    if request.method == 'POST':
        form = ArticleEditForm(request.POST, instance=article)
        if form.is_valid():
            form.save()

        return HttpResponseRedirect(reverse('core:article_detail', args=(community_id, article_id)))
    else:
        form = ArticleEditForm(instance=article)
        return render(request, 'core/article_edit.html',
                      {'form': form,
                       'article': article})


@login_required
def my_article(request):
    try:
        articles = Article.objects.filter(admin_id=request.user.id).order_by('-updated_at')
    except Article.DoesNotExist:
        raise Http404
    is_exists = articles.exists()

    paginator = Paginator(articles, 14)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        articles = paginator.page(1)

    return render(request, 'core/my_article.html',
                  {'articles': articles,
                   'is_exists': is_exists})


@login_required
@require_POST
def article_delete(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    article.delete()
    return HttpResponseRedirect(reverse('core:real_home',args=(article.community_id,)))


@login_required
def article_search(request):
    pass


@login_required
@require_POST
def comment_delete(request, article_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    article = get_object_or_404(Article, id=article_id)
    comment.delete()
    return HttpResponseRedirect(reverse('core:article_detail', args=(article.community_id, article_id,)))


@login_required
def community_manage(request):
    communities = Community.objects.filter(admin_id=request.user.id).order_by('name')
    is_exists = communities.exists()
    paginator = Paginator(communities, 8)
    page = request.GET.get('page')
    try:
        communities = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        communities = paginator.page(1)

    return render(request, 'core/community_manage.html',
                  {'communities': communities,
                   'is_exists': is_exists})


@login_required
def community_create(request):
    if request.method == 'POST':
        form = CommunityCreateForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            community.admin_id = request.user.id
            community.save()

        return HttpResponseRedirect(reverse('core:community_manage'))
    else:
        form = CommunityCreateForm()
        return render(request, 'core/community_create.html',
                      {'form': form})


@login_required
def community_detail(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    user = request.user
    if user in community.permitted_user.all():
        follow_status = 1  # フォロー済み
    elif user in community.stand_by_user.all():
        follow_status = 2  # 承認待ち
    else:
        follow_status = 3  # 未フォロー

    return render(request, 'core/community_detail.html',
                  {'community': community,
                   'follow_status': follow_status})


@login_required
def community_edit(request, community_id):
    community = get_object_or_404(Community, id=community_id)

    if request.method == 'POST':
        form = CommunityEditForm(request.POST, instance=community)
        if form.is_valid():
            form.save()

        return HttpResponseRedirect(reverse('core:community_detail', args=(community_id,)))
    else:
        form = CommunityEditForm(instance=community)
        return render(request, 'core/community_edit.html',
                      {'form': form,
                       'community': community})


@login_required
@require_POST
def community_delete(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    community.delete()
    return HttpResponseRedirect(reverse('core:community_manage'))


@login_required
def community_search(request):
    communities = Community.objects.order_by('?')[:20]
    return render(request, 'core/community_search.html',
                  {'communities': communities})


@login_required
def community_follow(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    if request.user in community.stand_by_user.all() or request.user in community.permitted_user.all():
        community.stand_by_user.remove(request.user)
        community.save()
    else:
        community.stand_by_user.add(request.user)
        community.save()
    return HttpResponseRedirect(reverse('core:community_detail',args=(community_id,)))


@login_required
def community_user_manage(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    stand_by_users = community.stand_by_user.all()
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            user = get_object_or_404(User, id=user_id)
            community.permitted_user.add(user)
            community.stand_by_user.remove(user)
            community.save()
        return HttpResponseRedirect(reverse('core:community_user_manage',kwargs={'community_id': community_id}))
    else:
        return render(request, 'core/community_user_manage.html',
                  {'stand_by_users': stand_by_users,
                   'community': community})


@login_required
def community_permitted_user_manage(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    permitted_users = community.permitted_user.all()

    return render(request, 'core/community_permitted_user_manage.html',
                  {'permitted_users': permitted_users,
                   'community': community})