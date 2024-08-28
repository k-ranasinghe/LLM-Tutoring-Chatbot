from django.db import models

# Create your models here.
class LectureMaterial(models.Model):
    file = models.FileField(upload_to='lectures/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name