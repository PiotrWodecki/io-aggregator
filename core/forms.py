from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, HTML
from django.urls import reverse

from core.validators import validate_file_extension


class SearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse("select_product")
        self.helper.form_method = "GET"
        self.helper.layout = Div(
            Field("q", placeholder="Wpisz nazwę produktu"),
            Field("shop"),
            Field("category"),
            # using Submit tag causes its value be sent as a URL query string,
            # this hack solves this problem
            HTML("<button class=\"btn btn-primary\" type='submit'>Szukaj</button>"),
        )

    SHOP_CHOICE = (
        (1, "Wszystkie sklepy"),
        (2, "Tylko Allegro"),
        (3, "Bez Allegro"),
    )
    CATEGORY_CHOICE = (
        ("Zdrowie", "Zdrowie"),
        ("Uroda", "Uroda"),
    )
    # product query
    q = forms.CharField(max_length=32, label="Szukaj")
    shop = forms.ChoiceField(
        choices=SHOP_CHOICE,
        widget=forms.RadioSelect(),
        initial=1,
        label="Wybierz zakres wyszukiwania:",
    )
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICE,
        widget=forms.RadioSelect(),
        initial="Zdrowie",
        label="Wybierz kategorię:",
    )


class MultiSearchFrom(forms.Form):
    title = forms.CharField(max_length=10)
    file = forms.FileField(validators=[validate_file_extension])
