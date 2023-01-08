from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView
from django_email_verification import send_email, verify_view, verify_token

from user import forms


class SignUpView(FormView):
    form_class = forms.UserRegisterForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

    def form_valid(self, form):
        response = super(SignUpView, self).form_valid(form)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_email(user)
        return response


@verify_view
def confirm_email(request, token):
    success, user = verify_token(token)
    if success:
        user.is_active = True
        user.save()

    return render(
        request,
        "registration/confirm_email.html",
        {"success": success, "username": user.username},
    )
