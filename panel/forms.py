from django import forms
from panel.models import InstagramAccount, Proxy, EngagementTarget, BotTask

class AccountForm(forms.ModelForm):
    class Meta:
        model = InstagramAccount
        fields = ['username', 'password', 'email', 'email_password', 'phone', 'proxy', 'status']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. john_doe'}),
            'password': forms.PasswordInput(render_value=True, attrs={'class': 'form-input', 'placeholder': '••••••••••••'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'e.g. john@example.com'}),
            'email_password': forms.PasswordInput(render_value=True, attrs={'class': 'form-input', 'placeholder': '••••••••••••'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. +1234567890'}),
            'proxy': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class ProxyForm(forms.ModelForm):
    class Meta:
        model = Proxy
        fields = ['ip', 'port', 'protocol', 'username', 'password', 'is_active']
        widgets = {
            'ip': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 192.168.1.1'}),
            'port': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 8080'}),
            'protocol': forms.Select(attrs={'class': 'form-select'}),
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Proxy user (optional)'}),
            'password': forms.PasswordInput(render_value=True, attrs={'class': 'form-input', 'placeholder': '••••••••••••'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

class TargetForm(forms.ModelForm):
    class Meta:
        model = EngagementTarget
        fields = ['username', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. nike'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = BotTask
        fields = ['task_type', 'account', 'target', 'comment_text']
        widgets = {
            'task_type': forms.Select(attrs={'class': 'form-select', 'id': 'task-type-select'}),
            'account': forms.Select(attrs={'class': 'form-select'}),
            'target': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username (for follow/like/comment)'}),
            'comment_text': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Enter comment text (only for comment task)'}),
        }

class ImportCSVForm(forms.Form):
    csv_file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-file-input', 'accept': '.csv'}))

class SettingsForm(forms.Form):
    captcha_service = forms.ChoiceField(
        choices=[('capmonster', 'CapMonster'), ('anticaptcha', 'AntiCaptcha')], 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    captcha_api_key = forms.CharField(
        max_length=200, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter Captcha Service API Key'})
    )
    sms_service = forms.ChoiceField(
        choices=[('5sim', '5sim'), ('smsactivate', 'SMS-Activate')], 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sms_api_key = forms.CharField(
        max_length=200, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter SMS Service API Key'})
    )
    email_service = forms.ChoiceField(
        choices=[('mailtm', 'Mail.tm (Recommended)'), ('1secmail', '1secmail.com (Legacy)')], 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    use_random_user_agent = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}))
    rotate_proxies = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}))
    wait_range_min = forms.IntegerField(min_value=0, max_value=60, widget=forms.NumberInput(attrs={'class': 'form-input'}))
    wait_range_max = forms.IntegerField(min_value=0, max_value=60, widget=forms.NumberInput(attrs={'class': 'form-input'}))
    
    browser_type = forms.ChoiceField(
        choices=[('chromium', 'Chromium / Google Chrome (Recommended)'), ('firefox', 'Firefox')], 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    browser_path = forms.CharField(
        max_length=300, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Leave empty for auto-detection (e.g. /usr/bin/google-chrome)'})
    )
    headless_mode = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}))
