from django import forms

class SubmitForm(forms.Form):
    status = forms.CharField()
    category = forms.CharField()
    desc = forms.CharField()
    location = forms.CharField()
