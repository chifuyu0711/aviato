from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from .forms import LoginForm, SignupForm, CommentForm
from .models import Post, Image, Category
from taggit.models import Tag
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, views
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin


class IndexView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog-posts.html'
    context_object_name = 'posts'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = Image.objects.all()
        context['tags'] = Tag.objects.all()
        context['categories'] = Category.objects.all()

        context['latest_posts'] = Post.objects.order_by('-date')[:3]


        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog-post-detail.html'
    context_object_name = 'post'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        context['categories'] = Category.objects.all()
        context['images'] = Image.objects.all()
        context['latest_posts'] = Post.objects.order_by('-date')[:3]
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = self.object
            comment.user = request.user
            comment.save()
            return redirect('post_detail', pk=self.object.pk)

        context['comment_form'] = comment_form
        return self.render_to_response(context)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TaggedPostListView(ListView):
    model = Post
    template_name = 'blog-full.html'
    context_object_name = 'posts'
    paginate_by = 3

    def get_queryset(self):
        tag_slug = self.kwargs.get('slug')
        return Post.objects.filter(tags__slug=tag_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        context['categories'] = Category.objects.all()
        return context


class CategoryPostListView(ListView):
    model = Post
    template_name = 'blog-full.html'
    context_object_name = 'posts'
    paginate_by = 3

    def get_queryset(self):
        category_slug = self.kwargs.get('slug')
        return Post.objects.filter(category__slug=category_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        context['categories'] = Category.objects.all()
        return context


class PasswordChangeView(views.PasswordChangeView):
    success_url = reverse_lazy("accounts:password_change_done")


class PasswordResetView(views.PasswordResetView):
    success_url = reverse_lazy("accounts:password_reset_done")


class PasswordResetConfirmView(views.PasswordResetConfirmView):
    success_url = reverse_lazy("accounts:password_reset_complete")


def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully!')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user_exists = User.objects.get(username=username)
            except User.DoesNotExist:
                user_exists = User.objects.filter(email=username).first()

            if user_exists:
                user = authenticate(request, username=user_exists.username, password=password)
                if user:
                    login(request, user)
                    return redirect('index')
                else:
                    messages.error(request, 'Неправильный пароль.')
            else:
                messages.error(request, 'Пользователь с таким именем или email не найден.')
        else:
            messages.error(request, 'Ошибка в заполнении формы.')

    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('login')
