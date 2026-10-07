from django import forms
from .models import Review, Poster


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'review_text')
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'review_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this wall poster (print quality, colors, paper thickness, packaging)...'
            }),
        }


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject / Order ID'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'How can we help you?'}))
