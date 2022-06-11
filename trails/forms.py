from django.forms import ModelForm, TextInput, Textarea, FileInput

from .models import Trail

class NewTrailForm(ModelForm):
    class Meta:
        model = Trail
        fields = [
            'name',
            'desc',
            'trail_file',
        ]
        widgets = {
            'name': TextInput(attrs={
                'class': '',
                'data-length': 100,
            }),
            'desc': Textarea(attrs={
                'class': 'materialize-textarea',
                'data-length': 1000,
            }),
            'trail_file': FileInput(attrs={
                'class': '',
            })
        }