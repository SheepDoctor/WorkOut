from django.db import models

class WorkoutHistory(models.Model):
    title = models.CharField(max_length=200, verbose_name="训练名称")
    data = models.JSONField(verbose_name="训练数据")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "训练历史"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

