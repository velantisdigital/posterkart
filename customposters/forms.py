from django import forms
from django.core.exceptions import ValidationError
from .models import CustomPoster
from store.models import PosterSize, FrameOption
import os


class CustomPosterForm(forms.ModelForm):
    size = forms.ModelChoiceField(
        queryset=PosterSize.objects.filter(is_active=True),
        empty_label=None,
        widget=forms.RadioSelect(attrs={'class': 'custom-size-radio'})
    )
    frame = forms.ModelChoiceField(
        queryset=FrameOption.objects.filter(is_active=True),
        empty_label=None,
        widget=forms.RadioSelect(attrs={'class': 'custom-frame-radio'})
    )
    uploaded_image = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'd-none',
            'id': 'customPosterFileInput',
            'accept': 'image/jpeg,image/png,image/jpg,image/webp'
        })
    )
    custom_text = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'e.g. "To the Moon and Back" or "Studio 1989" (Optional)'
        })
    )
    special_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'e.g. "Please center-crop and keep a 2cm white border margin"'
        })
    )
    quantity = forms.IntegerField(
        min_value=1,
        max_value=50,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control text-center', 'value': '1', 'min': '1', 'max': '50'})
    )

    class Meta:
        model = CustomPoster
        fields = ('uploaded_image', 'size', 'frame', 'custom_text', 'special_instructions', 'quantity')

    def clean_uploaded_image(self):
        image = self.cleaned_data.get('uploaded_image')
        if image:
            # Validate max file size 10MB
            max_size_mb = 10
            if image.size > max_size_mb * 1024 * 1024:
                raise ValidationError(f"Image file size is too large (Max {max_size_mb} MB).")
            
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                raise ValidationError("Only JPG, JPEG, PNG and WEBP image files are allowed.")
        return image
