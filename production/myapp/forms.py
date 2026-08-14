from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser , Product , Machine , Color, Thickness , Density, Size, Length, Height, Width 


class CustomUserCreateForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        }),
        help_text="Minimum 8 characters."
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        }),
        help_text="Enter the same password again."
    )
    class Meta:
        model = CustomUser
        fields = [
            'username',
            'full_name',
            'email',
            'contact',
            'role',
            'dob',
            'password1',
            'password2'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'username','full_name','email','contact','role','dob',
        ]


# class ProductForm(forms.ModelForm):
#     # Explicitly add the ID field
#     id = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly'}))

#     class Meta:
#         model = Product
#         fields = ['id', 'product_name', 'category']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category',
            'color',
            'thickness',
            'density',
            'size',
            'length',
            'width',
            'height',
            'stamp',
        ]
        widgets = {
            'color': forms.Select(attrs={'class': 'form-control'}),
            'thickness': forms.Select(attrs={'class': 'form-control'}),
            'density': forms.Select(attrs={'class': 'form-control'}),
            'size': forms.Select(attrs={'class': 'form-control'}),
            'length': forms.Select(attrs={'class': 'form-control'}),
            'width': forms.Select(attrs={'class': 'form-control'}),
            'height': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter dropdowns to show only active items
        self.fields['color'].queryset = Color.objects.filter(is_active=True)
        self.fields['thickness'].queryset = Thickness.objects.filter(is_active=True, thickness__lte=36)
        self.fields['density'].queryset = Density.objects.filter(is_active=True)
        self.fields['size'].queryset = Size.objects.filter(is_active=True)
        self.fields['length'].queryset = Length.objects.filter(is_active=True)
        self.fields['width'].queryset = Width.objects.filter(is_active=True, width__gte=48)
        self.fields['height'].queryset = Height.objects.filter(is_active=True, height__lte=46)

    

class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ['name','category','is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Machine Name'
            })
        }

