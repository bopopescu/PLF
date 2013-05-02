from django import forms
from django.forms.fields import DateField
from django.contrib.admin.widgets import AdminDateWidget 
from django.forms import extras
import PIL
import datetime

STATUS=[('Lost', 'Lost'), ('Found', 'Found')]
CATEGORIES = (('Clothing', 'Clothing'), ('Wallet/Keys/Prox', 'Wallet/Keys/Prox'), ('Phone', 'Phone'), ('Charger', 'Charger'), ('Electronics', 'Electronics'), ('Accessories', 'Accessories'), ('Textbook', 'Textbook'), ('Backpack', 'Backpack'), ('Other', 'Other'))

now = datetime.datetime.today()

class SubmitForm(forms.Form):
    status = forms.ChoiceField(choices=STATUS, widget=forms.RadioSelect())
    category = forms.ChoiceField(choices=CATEGORIES)
    location = forms.CharField(required=False)
    event_date = forms.DateField(initial=now, widget=extras.SelectDateWidget(years=range(datetime.date.today().year, 2026)), required=False)
    desc = forms.CharField(widget=forms.TextInput(attrs={'size':'100'}))
    picture = forms.ImageField(required=False)
    #netid = forms.CharField()

	#def clean_message(self):
    #    message = self.cleaned_data['message']
    #    num_words = len(message.split())
    #    if num_words < 4:
    #        raise forms.ValidationError("Not enough words!")
    #    return message