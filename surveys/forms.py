from django import forms

from .models import Survey


class SurveyForm(forms.ModelForm):
    url = forms.URLField(
        label="Tautan formulir",
        max_length=500,
        assume_scheme="https",
        widget=forms.URLInput(attrs={"placeholder": "https://forms.gle/…"}),
    )

    class Meta:
        model = Survey
        fields = ["title", "url", "sender", "contact", "reward"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Misalnya, kebiasaan belajar mahasiswa",
                    "autofocus": True,
                },
            ),
            "sender": forms.TextInput(attrs={"placeholder": "Nama yang bisa dihubungi"}),
            "contact": forms.TextInput(attrs={"placeholder": "Email, WhatsApp, atau ID LINE"}),
            "reward": forms.TextInput(attrs={"placeholder": "Misalnya, undian saldo Rp50.000"}),
        }
