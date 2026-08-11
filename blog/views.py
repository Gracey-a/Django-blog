from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone

from .models import Post, Comment, Category, Profile
from .forms import PostForm, CommentForm, ProfileForm

# ---------- Home page ----------
class HomeView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        queryset = Post.objects.filter(
            status=Post.PUBLISHED,
            deleted=False
        ).filter(
            Q(publish_date__isnull=True) | Q(publish_date__lte=timezone.now())
        ).order_by('-created_at')
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(content__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

# ---------- Post detail (function-based) ----------
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, status=Post.PUBLISHED, publish_date__lte=timezone.now(), deleted=False)
    comments = post.comments.all().order_by('-created_at')
    comment_form = CommentForm()
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'now': timezone.now(),
    })

# ---------- Create post ----------
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_editor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        category_id = self.request.POST.get('category')
        if category_id:
            form.instance.category = get_object_or_404(Category, id=category_id)
        else:
            form.instance.category = None
        action = self.request.POST.get('action')
        if action == 'publish':
            form.instance.status = Post.PUBLISHED
            if not form.instance.publish_date:
                form.instance.publish_date = timezone.now()
        else:
            form.instance.status = Post.DRAFT
            form.instance.publish_date = None
        messages.success(self.request, 'Your post was created successfully! 🎉')
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.status == Post.PUBLISHED:
            return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('dashboard')

# ---------- Update post ----------
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_editor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def form_valid(self, form):
        category_id = self.request.POST.get('category')
        if category_id:
            form.instance.category = get_object_or_404(Category, id=category_id)
        else:
            form.instance.category = None
        action = self.request.POST.get('action')
        if action == 'publish':
            form.instance.status = Post.PUBLISHED
            if not form.instance.publish_date or form.instance.publish_date > timezone.now():
                form.instance.publish_date = timezone.now()
        else:
            form.instance.status = Post.DRAFT
            form.instance.publish_date = None
        messages.success(self.request, 'Post updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.status == Post.PUBLISHED:
            return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('dashboard')

# ---------- Delete post (hard delete via class) ----------
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Post deleted successfully.')
        return super().delete(request, *args, **kwargs)

# ---------- Dashboard ----------
class DashboardView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/dashboard.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).order_by('-created_at')

# ---------- Profile ----------
class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_posts'] = Post.objects.filter(author=self.request.user).order_by('-created_at')[:5]
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'blog/profile_edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user.profile

# ---------- Author posts ----------
class AuthorPostsView(ListView):
    model = Post
    template_name = 'blog/author_posts.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(
            author=self.author,
            status=Post.PUBLISHED,
            publish_date__lte=timezone.now(),
            deleted=False
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        return context

# ---------- Category posts ----------
class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category_posts.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(
            category=self.category,
            status=Post.PUBLISHED,
            publish_date__lte=timezone.now(),
            deleted=False
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

# ---------- Trash ----------
class TrashView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/trash.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user, deleted=True).order_by('-deleted_at')

# ---------- Duplicate, soft delete, restore, permanent delete ----------
@login_required
def duplicate_post(request, pk):
    original = get_object_or_404(Post, pk=pk)
    if request.user != original.author and not request.user.is_staff:
        messages.error(request, "You cannot duplicate this post.")
        return redirect('post_detail', pk=pk)
    new_post = Post.objects.create(
        title=f"{original.title} (Copy)",
        content=original.content,
        image=original.image,
        author=request.user,
        category=original.category,
        status='D',
        publish_date=None,
    )
    new_post.tags.set(original.tags.all())
    messages.success(request, f"Post '{new_post.title}' duplicated as draft.")
    return redirect('post_update', pk=new_post.pk)

@login_required
def delete_post_permanent(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author and not request.user.is_staff:
        messages.error(request, "You cannot delete this post.")
        return redirect('post_detail', pk=pk)
    post.delete()
    messages.success(request, f"Post '{post.title}' permanently deleted.")
    return redirect('dashboard')

@login_required
def soft_delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author and not request.user.is_staff:
        messages.error(request, "You cannot delete this post.")
        return redirect('post_detail', pk=pk)
    post.deleted = True
    post.deleted_at = timezone.now()
    post.save()
    messages.success(request, f"Post '{post.title}' moved to trash.")
    return redirect('dashboard')

@login_required
def restore_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author and not request.user.is_staff:
        messages.error(request, "You cannot restore this post.")
        return redirect('post_detail', pk=pk)
    post.deleted = False
    post.deleted_at = None
    post.save()
    messages.success(request, f"Post '{post.title}' restored.")
    return redirect('dashboard')

# ---------- Like ----------
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user.is_authenticated:
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return redirect('post_detail', pk=pk)
    return redirect('login')

# ---------- Comments ----------
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    return redirect('post_detail', pk=post_id)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author == request.user or request.user.is_staff:
        post_pk = comment.post.pk
        comment.delete()
        return redirect('post_detail', pk=post_pk)
    else:
        return redirect('post_detail', pk=comment.post.pk)

# ---------- Custom logout ----------
def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

# ---------- Custom login ----------
class CustomLoginView(LoginView):
    template_name = 'blog/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Welcome back, {form.get_user().username}! 👋')
        return redirect(response.url + '?welcome=true')

# ---------- Signup ----------
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView

class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'blog/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Account created! Please log in.')
        return super().form_valid(form)


from django.http import HttpResponse
from django.conf import settings

def test_storage(request):
    return HttpResponse(f"DEFAULT_FILE_STORAGE = {settings.DEFAULT_FILE_STORAGE}")
