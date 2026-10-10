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
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel"}),
            "organisation": forms.TextInput(attrs={"autocomplete": "organization"}),
            "message": forms.Textarea(attrs={"rows": 6}),
        }
        labels = {"name": "Your name", "email": "Email", "phone": "Phone", "topic": "What is it about?", "organisation": "Organisation", "message": "Message"}


class SubscribeForm(HoneypotMixin, forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Your email address", "autocomplete": "email"}))
