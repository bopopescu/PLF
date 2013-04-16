from django import forms
import PIL

STATUS=[('Lost', 'Lost'), ('Found', 'Found')]
CATEGORIES = (('Clothing', 'Clothing'), ('Jewelry', 'Jewelry'), ('Prox', 'Prox'), ('BNF', 'Black North Face'), ('Other', 'Other'))

class SubmitForm(forms.Form):
    status = forms.ChoiceField(choices=STATUS, widget=forms.RadioSelect())
    category = forms.ChoiceField(choices=CATEGORIES)
    location = forms.CharField(required=False)
    event_date = forms.DateField(required=False)
    desc = forms.CharField(widget=forms.TextInput(attrs={'size':'100'}))
    picture = forms.ImageField(required=False)
    netid = forms.CharField()