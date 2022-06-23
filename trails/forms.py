from django.forms import ModelForm, TextInput, Textarea, FileInput, Select

from .models import Trail, Photo, Comment

SHARE_SETTINGS = (
    ('private','Private'),
    ('public','Public'),
    ('link','Share with link'),
)
class NewTrailForm(ModelForm):
    class Meta:
        model = Trail
        fields = [
            'name',
            'desc',
            'trail_file',
            'share_future',
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
            }),
            'share_future': Select(choices=SHARE_SETTINGS),
        }

class AddTrailPhoto(ModelForm):
    class Meta:
        model = Photo
        fields = ['photo',]
        widgets = {
            'photo': FileInput(attrs={
                'class':'',
            })
        }

class AddTrailComment(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment',]
        widgets = {
            'comment': Textarea(attrs={
                'class': '',
                'data-length': 500,
            })
        }

class EditPhotoCaption(ModelForm):
    class Meta:
        model = Photo
        fields = ['caption',]
        widgets = {
            'comment': Textarea(attrs={
                'class':'',
                'data-length': 100,
            })
        }