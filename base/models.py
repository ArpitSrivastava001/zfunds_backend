from django.db import models
# from django.contrib.auth import get_user_model
from django.utils import timezone

# User = get_user_model()

class BaseModel(models.Model):
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='%(class)s_created_by', null=True, blank=True)
    modified_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='%(class)s_modified_by', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.modified_at = timezone.now()
        super().save(*args, **kwargs)