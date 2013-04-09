from django import forms

STATUS=[('Lost', 'Lost'), ('Found', 'Found')]

class SubmitForm(forms.Form):
    status = forms.ChoiceField(choices=STATUS, widget=forms.RadioSelect())
    category = forms.CharField()
    location = forms.CharField()
    event_date = forms.DateField()
    desc = forms.CharField(widget=forms.TextInput(attrs={'size':'100'}))

