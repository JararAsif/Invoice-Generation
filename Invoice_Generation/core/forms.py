from django import forms
from .models import User,product

class Create_User(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password"
    )

    class Meta:
        model = User
        fields = ('email', 'name', 'address', 'password')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'})
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'client'
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class AddProduct(forms.ModelForm):
    class Meta:
        model = product
        fields = ('name','description','price', 'quantity')
        widgets ={
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),

        }
        