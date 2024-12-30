from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name.isalpha():
            raise ValidationError("First name must only contain alphabetic characters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name.isalpha():
            raise ValidationError("Last name must only contain alphabetic characters.")
        return last_name
    
    def clean_email(self):
            email = self.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                raise ValidationError("A user with that email already exists.")
            return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        if commit:
            user.save()
        return user

alphabet_validator = RegexValidator(regex='^[a-zA-Z]*$', message="Only alphabetic characters are allowed.")
class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        validators=[alphabet_validator],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        validators=[alphabet_validator],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}),
        label="New Password",
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if self.instance.first_name != first_name: 
            if not first_name.isalpha():
                raise ValidationError("First name must only contain alphabetic characters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if self.instance.last_name != last_name:
            if not last_name.isalpha():
                raise ValidationError("Last name must only contain alphabetic characters.")
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        print(f"Cleaning email: {email}")
        if self.instance.email != email:
            if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
                print("Email already exists!")
                raise ValidationError("A user with that email already exists.")
        return email

class CashWithdrawalForm(forms.Form):
    CHOICES = [
        ('1000', '1,000'),
        ('2000', '2,000'),
        ('3000', '3,000'),
        ('4000', '4,000'),
        ('5000', '5,000'),
        ('10000', '10,000'),
        ('other', 'Other Amount'),
    ]

    withdrawal_choice = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, label="Select Withdrawal Amount")
    other_amount = forms.DecimalField(required=False, label="Enter Amount", min_value=1000, max_value=50000, widget=forms.NumberInput(attrs={'placeholder': 'Enter amount if selected "Other Amount"'}))

    def clean(self):
        cleaned_data = super().clean()
        withdrawal_choice = cleaned_data.get("withdrawal_choice")
        other_amount = cleaned_data.get("other_amount")

        if withdrawal_choice == 'other' and not other_amount:
            raise ValidationError("Please enter a valid amount when 'Other Amount' is selected.")
        
        return cleaned_data