from django import forms
from .models import Channel, Post


class ChannelCreateForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter channel name',
            'autocomplete': 'off'
        })
    )
    description = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'placeholder': 'Describe your channel (optional)',
            'rows': 4
        })
    )
    is_private = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        })
    )

    class Meta:
        model = Channel
        fields = ('name', 'description', 'is_private')


class PostCreateForm(forms.ModelForm):
    content = forms.CharField(
        max_length=2000,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'placeholder': 'Share your thoughts anonymously...',
            'rows': 4,
            'id': 'postContent'
        })
    )

    class Meta:
        model = Post
        fields = ('content',)
