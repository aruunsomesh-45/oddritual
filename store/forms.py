from django import forms
from bleach import clean
from .models import contactform as ContactModel

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactModel
        fields = ['name', 'email', 'message']

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        
        if len(name) > 40:
            raise forms.ValidationError("Name must be less than 40 characters long.")
            
        if not name.replace(' ', '').isalpha():
            raise forms.ValidationError("Name must contain only alphabetic characters.")
            
        return clean(name, tags=[], strip=True)

    def clean_message(self):
        message = self.cleaned_data.get('message', '')
        return clean(message, tags=[], strip=True)       