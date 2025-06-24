from django.db import models
from apps.authx.models import User

class ResumeFile(models.Model):
    """
    Stores uploaded CVs for a user.
    """
    ResumeFileID = models.AutoField(
        primary_key=True,
        db_column='id'
    )
    UserID = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='resumes'
    )
    FilePath     = models.FileField(
        upload_to='resumes/%Y/%m/%d/',
        max_length=512,
        db_column='FilePath'
    )
    Status = models.CharField(
        max_length=50,
        db_column='status'
    )
    IsSelected = models.BooleanField(
        default=False,
        db_column='IsSelected'
    )
    UploadedAt = models.DateTimeField(
        auto_now_add=True,
        db_column='uploaded_at'
    )
    UpdatedAt = models.DateTimeField(
        auto_now=True,
        db_column='updated_at'
    )

    class Meta:
        db_table = 'ResumeFile'
        verbose_name = 'Resume File'
        verbose_name_plural = 'Resume Files'
        ordering = ['-UploadedAt']

    def __str__(self):
        return f"{self.UserID.username} – {self.FilePath.split('/')[-1]}"
    
class ParsedData(models.Model):
    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )
    ResumeID = models.ForeignKey(
        ResumeFile,
        on_delete=models.CASCADE,
        db_column='resume_file_id',
        related_name='parsed_data'
    )
    Data = models.JSONField(
        db_column='data'
    )
    ParsedAt = models.DateTimeField(
        auto_now_add=True,
        db_column='parsed_at'
    )

    class Meta:
        db_table = 'ParsedData'
        verbose_name = 'Parsed Data'
        verbose_name_plural = 'Parsed Data'
        ordering = ['-ParsedAt']
    def __str__(self):
        return f"Parsed Data for {self.ResumeID.FilePath.split('/')[-1]} at {self.ParsedAt.strftime('%Y-%m-%d %H:%M:%S')}"