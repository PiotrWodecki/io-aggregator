from django.urls import reverse_lazy
from django.views import generic

from user import forms


class SignUpView(generic.CreateView):
    form_class = forms.UserRegisterForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
