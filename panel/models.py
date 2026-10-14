from django.db import models

class Proxy(models.Model):
    STATUS_CHOICES = [
        ('clean', 'Clean / Active'),
        ('slow', 'Slow Response'),
        ('blocked', 'Instagram Blocked'),
        ('offline', 'Offline / Unreachable'),
        ('untested', 'Untested'),
    ]

    ip = models.CharField(max_length=100)
    port = models.IntegerField()
    protocol = models.CharField(max_length=10, default='http')  # http or https
    username = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    health_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='untested')
    error_message = models.CharField(max_length=255, blank=True, null=True)
    speed = models.FloatField(blank=True, null=True, help_text="Response time in seconds")
    last_checked = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        auth_part = f"{self.username}:{self.password}@" if self.username and self.password else ""
        return f"{self.protocol}://{auth_part}{self.ip}:{self.port}"

    class Meta:
        verbose_name_plural = "Proxies"

class InstagramAccount(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('verification_needed', 'Verification Needed'),
        ('banned', 'Banned'),
        ('unverified', 'Unverified'),
    ]

    username = models.CharField(max_length=100, unique=True)
    # Stored plain/reversible because automation needs raw passwords to fill input forms in browser.
    # TODO(security): Encrypt stored passwords at rest.
    password = models.CharField(max_length=200)
    email = models.CharField(max_length=150)
    email_password = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    proxy = models.ForeignKey(Proxy, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_status_display()})"

class EngagementTarget(models.Model):
    username = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class BotTask(models.Model):
    TASK_TYPES = [
        ('create_account', 'Create Account'),
        ('follow', 'Follow User'),
        ('like', 'Like Post'),
        ('comment', 'Comment on Post'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    task_type = models.CharField(max_length=30, choices=TASK_TYPES)
    account = models.ForeignKey(InstagramAccount, on_delete=models.CASCADE, blank=True, null=True)
    target = models.CharField(max_length=150, blank=True, null=True, help_text="Target Instagram username or post identifier")
    comment_text = models.TextField(blank=True, null=True, help_text="Comment message content")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    logs = models.TextField(blank=True, default="", help_text="Automation run logs")
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_task_type_display()} ({self.get_status_display()})"

class GlobalSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.key
