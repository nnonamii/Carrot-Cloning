from django import forms
from .models import Post, Oldcar, Job, Realty, Store



class CustomLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "아이디를 입력해주세요", "class": "login-input"}),
        label="아이디",
        label_suffix="",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "비밀번호를 입력해주세요", "class": "login-input"}),
        label="비밀번호",
        label_suffix="",
    )


class CustomRegistrationForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "아이디를 입력해주세요", "class": "login-input"}),
        label="아이디",
        label_suffix="",
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "비밀번호를 입력해주세요", "class": "login-input"}),
        label="비밀번호",
        label_suffix="",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "비밀번호를 다시 입력해주세요", "class": "login-input"}
        ),
        label="비밀번호 확인",
        label_suffix="",
    )


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "price", "description", "location", "images"]


class OldcarForm(forms.ModelForm):
    class Meta:
        model = Oldcar
        fields = [
            "title",
            "price",
            "description",
            "location",
            "images",
            "car_info",
            "insurance_history",
        ]



class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['store_name', 'location', 'semi_location',
                   'greetings', 'category', 'days', 
                  'open_time', 'close_time','images', 'menu_items']
        
class JobsForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title",
            "price",
            "description",
            "location",
            "images",
            "working_days",
            "working_time",
        ]


class RealtyForm(forms.ModelForm):
    class Meta:
        model = Realty
        fields = [
            "title",
            "property_type",
            "deposit",
            "monthly_rent",
            "area",
            "rooms",
            "floor",
            "description",
            "location",
            "images",
        ]
