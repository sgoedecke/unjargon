from django import forms
from .models import JargonText

class JargonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs) #do init stuff
        self.fields['text'].label = '' #black out text label.
    class Meta:
        model = JargonText
        fields = ('text',)
