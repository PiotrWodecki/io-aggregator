from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.urls import reverse_lazy, reverse


class SearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse("search")
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Szukaj"))

    SHOP_CHOICE = (
        (1, "Tylko Allegro"),
        (2, "Bez Allegro"),
        (3, "Wszystkie sklepy"),
    )

    search_item = forms.CharField(max_length=32)
    options = forms.ChoiceField(
        choices=SHOP_CHOICE,
        widget=forms.RadioSelect(),
    )
    # rename variable in frontend
    search_item.label = "Szukany przedmiot"
    options.label = "Opcje Allegro:"
