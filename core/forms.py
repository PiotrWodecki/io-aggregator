from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, HTML, Submit
from django.urls import reverse, reverse_lazy

from core.validators import validate_multi_search_file


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
    q = forms.CharField(max_length=32, label="")
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
    helper = FormHelper()
    helper.form_action = reverse_lazy("multi_product")
    helper.form_method = "POST"
    helper.add_input(Submit("submit", "Wyszukaj"))

    file = forms.FileField(validators=[validate_multi_search_file], label="")
