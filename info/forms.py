from django import forms
from django.forms.fields import DateField
from django.contrib.admin.widgets import AdminDateWidget 
from django.forms import extras
from stdimage import StdImageField
import PIL
import datetime
import html5.forms.widgets as html5_widgets

STATUS=[('Lost', 'Lost'), ('Found', 'Found')]
CATEGORIES = (('Clothing', 'Clothing'), ('Wallet/Keys/Prox', 'Wallet/Keys/Prox'), ('Phone', 'Phone'), ('Charger', 'Charger'), ('Electronics', 'Electronics'), ('Accessories', 'Accessories'), ('Textbook', 'Textbook'), ('Backpack', 'Backpack'), ('Other', 'Other'), ('Black North Face', 'Black North Face'))

now = datetime.datetime.today()

class SubmitForm(forms.Form):
    status = forms.ChoiceField(choices=STATUS, widget=forms.RadioSelect())
    category = forms.ChoiceField(choices=CATEGORIES)
    location = forms.CharField(required=False, max_length=100)
    #event_date = forms.DateField(initial=now, widget=extras.SelectDateWidget(years=range(2012, datetime.date.today().year + 1)), required=False)
    event_date = forms.DateField(widget=html5_widgets.DateInput, required=False)
    desc = forms.CharField(widget=forms.Textarea(attrs={'rows':'2', 'cols':'40'}), max_length=250)
    picture = StdImageField(upload_to='')
    name = forms.CharField(widget=forms.TextInput(attrs={'size':'20'}), max_length=20)
    #netid = forms.CharField()

	#def clean_message(self):
    #    message = self.cleaned_data['message']
    #    num_words = len(message.split())
    #    if num_words < 4:
    #        raise forms.ValidationError("Not enough words!")
    #    return message