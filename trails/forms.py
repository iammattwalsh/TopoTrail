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
                'placeholder': 'Trail name',
            }),
            'desc': Textarea(attrs={
                'class': '',
                'placeholder': 'Trail description',
            }),
            'trail_file': FileInput(attrs={
                'class': '',
            })
        }