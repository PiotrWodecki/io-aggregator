from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.urls import reverse_lazy


class SearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse_lazy("search")
        self.helper.form_method = "GET"
        self.helper.add_input(Submit("submit", "Submit"))

    SHOP_CHOICE = (
        (1, "Only allegro"),
        (2, "Without allegro"),
        (3, "ALL"),
    )

    search_item = forms.CharField(max_length=32)
    options = forms.ChoiceField(
        choices=SHOP_CHOICE,
        widget=forms.RadioSelect(),
    )
