from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import CreationForm


class LoggedOut(TemplateView):
    template_name = 'registration/logged_out.html'


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('signup')
    template_name = 'signup.html'
