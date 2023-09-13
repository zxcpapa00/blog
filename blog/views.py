from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from taggit.models import Tag
from django.db.models import Count

from .models import Post
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.contrib.postgres.search import TrigramSimilarity


class PostListView(ListView):
    model = Post
    queryset = Post.published.all()
    template_name = 'blog/post_list.html'
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset()
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            tag = Tag.objects.get(slug=tag_slug)
            queryset = Post.published.filter(tags__in=[tag, ])
        return queryset


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, status=Post.PUBLISHED, id=self.object.id)
        context['form'] = CommentForm()
        context['comments'] = post.comments.filter(active=True)
        tags_ids = post.tags.all().values_list('id', flat=True)
        similar_posts = Post.published.filter(tags__in=tags_ids).exclude(id=post.id)
        context['similar_posts'] = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags')[:4]
        return context


@require_POST
def create_comment(request, post_slug):
    post = Post.published.get(slug=post_slug)
    form = CommentForm(request.POST)
    comment = None
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        messages.success(request, message='Комментарий успешно создан')
        return HttpResponseRedirect(post.get_absolute_url())

    return render(request, 'blog/form_comment.html', {'form': form,
                                                      'post': post,
                                                      'comment': comment})


def post_share(request, post_slug):
    # Извлечь пост по идентификатору id
    post = get_object_or_404(Post,
                             slug=post_slug,
                             status=Post.PUBLISHED)
    sent = False
    if request.method == 'POST':
        # Форма была передана на обработку
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Поля формы успешно прошли валидацию
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommend you {post.title}"
            message = f"Read {post.title} at {post_url}\n\n {cd['name']}'s {cd['email']} comments:{cd['comments']}"
            send_mail(subject, message, 'zxcpapa00@gmail.com', (cd['to'],))
            sent = True

    else:
        form = EmailPostForm()
    return render(request, 'blog/share.html', {'post': post, 'form': form, 'sent': sent})


def search_view(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            results = (Post.published.annotate(similarity=TrigramSimilarity('title', query),)
                       .filter(similarity__gt=0.1)).order_by('-similarity')

    context = {
        'form': form,
        'query': query,
        'results': results
    }

    return render(request, 'blog/search.html', context)
