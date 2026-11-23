from io import BytesIO

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from PIL import Image, ImageOps, UnidentifiedImageError

from .models import Student, StudentGroup, Teacher


class AccountProfileForm(forms.ModelForm):
    photo = forms.FileField(
        label='Profil rasmi', required=False,
        widget=forms.FileInput(attrs={'accept': 'image/jpeg,image/png,image/webp'}),
        help_text='JPG, PNG yoki WebP. Maksimal hajmi 5 MB.',
    )

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name')
        labels = {'first_name': 'Ism', 'last_name': 'Familiya'}
        widgets = {
            'first_name': forms.TextInput(attrs={'autocomplete': 'given-name'}),
            'last_name': forms.TextInput(attrs={'autocomplete': 'family-name'}),
        }

    def clean_photo(self):
        upload = self.cleaned_data['photo']
        if not upload:
            return None
        if upload.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Rasm hajmi 5 MB dan oshmasligi kerak.')
        try:
            with Image.open(upload, formats=('JPEG', 'PNG', 'WEBP')) as source:
                if source.width * source.height > 16_000_000:
                    raise forms.ValidationError('Rasm o‘lchami juda katta.')
                image = ImageOps.exif_transpose(source)
                image.thumbnail((512, 512))
                output = BytesIO()
                image.convert('RGB').save(output, format='JPEG', quality=88)
                return output.getvalue()
        except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError, SyntaxError) as exc:
            raise forms.ValidationError('Yaroqli JPG, PNG yoki WebP rasm tanlang.') from exc


class CrmPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Joriy parol'
        self.fields['new_password1'].label = 'Yangi parol'
        self.fields['new_password2'].label = 'Yangi parolni tasdiqlash'


class StudentForm(forms.ModelForm):
    age = forms.IntegerField(label='Yoshi', min_value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].required = True

    class Meta:
        model = Student
        fields = ('name', 'surname', 'phone', 'age', 'course', 'group')
        labels = {'name': 'Ismi', 'surname': 'Familiyasi', 'phone': 'Telefon', 'course': 'Kurs', 'group': 'Guruh'}
        widgets = {'phone': forms.TextInput(attrs={'type': 'tel'})}


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ('name', 'surname', 'specialty', 'phone')
        labels = {'name': 'Ismi', 'surname': 'Familiyasi', 'specialty': 'Mutaxassisligi', 'phone': 'Telefon'}
        widgets = {'phone': forms.TextInput(attrs={'type': 'tel'})}


class StudentGroupForm(forms.ModelForm):
    class Meta:
        model = StudentGroup
        fields = ('name',)
