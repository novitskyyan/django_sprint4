from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, UpdateView, \
    ListView, DeleteView

from .constants import COMMON_PAGINATION
from .forms import PostForm, UserForm, CommentForm
from .models import Post, Category, Comment


class ProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by = COMMON_PAGINATION
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs['username'])

    def posts_with_annotation(self, posts):
        return posts.annotate(comment_count=Count('comment'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.get_object()
        if self.request.user == author:
            posts = self.posts_with_annotation(
                Post.objects.filter(
                    author=author
                ).order_by(
                    '-pub_date'
                )
            )
        else:
            posts = self.posts_with_annotation(
                Post.published_objects.filter(
                    author=author
                ).order_by(
                    '-pub_date'
                )
            )
        paginator = Paginator(posts, COMMON_PAGINATION)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:edit_profile')

    def get_object(self, queryset=None):
        return self.request.user


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = COMMON_PAGINATION

    def get_queryset(self):
        return Post.published_objects.annotate(comment_count=Count('comment'))


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_queryset(self):
        query = Q(
            author_id=self.request.user.id
        ) | Q(
            category__is_published=True,
            is_published=True,
            pub_date__lte=timezone.now()
        )
        return Post.objects.filter(query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comment.select_related('author')
        )
        return context


class CategoryPostListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    pk_url_kwarg = 'category_slug'
    ordering = '-pub_date'
    paginate_by = COMMON_PAGINATION

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.category.posts.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(comment_count=Count('comment')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        new_form = form.save(commit=False)
        new_form.author = self.request.user
        return super().form_valid(new_form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'pk'

    def form_valid(self, form):
        new_comment = form.save(commit=False)
        new_comment.post = get_object_or_404(
            Post, pk=self.kwargs[self.pk_url_kwarg])
        new_comment.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['pk']})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return redirect('blog:post_detail', pk=post.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.get_object().pk}
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return redirect('blog:post_detail', pk=post.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:index')


class CommentUpdateDeleteMixin:
    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return redirect('blog:post_detail', pk=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'pk': self.kwargs['post_id']})


class CommentUpdateView(CommentUpdateDeleteMixin,
                        LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'


class CommentDeleteView(CommentUpdateDeleteMixin,
                        LoginRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'
