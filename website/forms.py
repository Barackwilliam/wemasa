from django import forms

from .models import ContactMessage


class HoneypotMixin(forms.Form):
    # Hidden from people with CSS; bots that fill every field are ignored.
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    def is_spam(self):
        return bool(self.cleaned_data.get("website"))


class ContactForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "organisation", "topic", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your full name", "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"placeholder": "+255 ...", "autocomplete": "tel"}),
            "organisation": forms.TextInput(attrs={"placeholder": "Optional", "autocomplete": "organization"}),
            "message": forms.Textarea(attrs={"rows": 6, "placeholder": "How can we work together?"}),
        }
        labels = {"topic": "What is this about?", "organisation": "Organisation"}


class SubscribeForm(HoneypotMixin, forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Your email address", "autocomplete": "email"}))
