from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from .forms import SignUpForm, LoginForm, UpdateUserForm, UpdateProfileForm
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
    initial = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('blog:index'))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Accounts created for {username}')

            return HttpResponseRedirect(reverse_lazy('accounts:login'))

        return render(request, self.template_name, {'form': form})


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True

        return super().form_valid(form)


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, files=request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, message='Your profile is update')
            return HttpResponseRedirect(reverse_lazy('accounts:user-profile'))
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }

    return render(request, 'registration/profile.html', context)


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'registration/change_password.html'
    success_url = reverse_lazy('accounts:user-profile')
    success_message = 'Successfully Changed Your Password'




