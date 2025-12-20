from django.db import models

class WorkoutPlan(models.Model):
    """训练计划"""
    title = models.CharField(max_length=200, verbose_name="计划名称")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_default = models.BooleanField(default=False, verbose_name="是否默认计划")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "训练计划"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

class WorkoutExercise(models.Model):
    """训练计划中的具体动作"""
    plan = models.ForeignKey(WorkoutPlan, related_name='exercises', on_delete=models.CASCADE, verbose_name="所属计划")
    name = models.CharField(max_length=200, verbose_name="动作名称")
    total_sets = models.IntegerField(default=3, verbose_name="总组数")
    reps_per_set = models.IntegerField(default=12, verbose_name="每组次数")
    current_sets = models.IntegerField(default=0, verbose_name="当前已完成组数")
    tips = models.TextField(null=True, blank=True, verbose_name="动作要领")
    start_time = models.CharField(max_length=10, default="00:00", verbose_name="开始时间")
    end_time = models.CharField(max_length=10, default="00:00", verbose_name="结束时间")
    seconds = models.IntegerField(default=0, verbose_name="开始秒数")
    gif_url = models.URLField(max_length=500, null=True, blank=True, verbose_name="动作演示GIF")
    category = models.CharField(max_length=50, null=True, blank=True, verbose_name="动作类别")
    muscle_group = models.CharField(max_length=50, null=True, blank=True, verbose_name="训练部位")
    order = models.IntegerField(default=0, verbose_name="排序")

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "训练动作"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.plan.title} - {self.name}"

class WorkoutLog(models.Model):
    """训练执行日志"""
    STATUS_CHOICES = [
        ('completed', '已完成'),
        ('interrupted', '已中断'),
        ('failed', '失败'),
    ]

    plan_title = models.CharField(max_length=200, verbose_name="关联计划")
    action_name = models.CharField(max_length=200, null=True, blank=True, verbose_name="动作名称")
    set_index = models.IntegerField(null=True, blank=True, verbose_name="组数索引")
    reps_count = models.IntegerField(default=0, verbose_name="完成次数")
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="开始时间")
    duration = models.IntegerField(default=0, verbose_name="训练时长(秒)")
    # 从 data_snapshot 提取的字段
    exercise_id = models.IntegerField(null=True, blank=True, verbose_name="动作ID")
    target_reps = models.IntegerField(null=True, blank=True, verbose_name="目标次数")
    target_sets = models.IntegerField(null=True, blank=True, verbose_name="目标组数")
    data_snapshot = models.JSONField(null=True, blank=True, verbose_name="完成情况快照") # 已废弃，保留用于兼容
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='interrupted')
    
    # AI 评价扩展
    ai_score = models.FloatField(null=True, blank=True, verbose_name="AI评分")
    ai_feedback = models.TextField(null=True, blank=True, verbose_name="AI建议")
    set_feedback = models.JSONField(null=True, blank=True, verbose_name="每组AI反馈") # [{action_id, set_index, score, is_standard, feedback, errors}]

    class Meta:
        ordering = ['-start_time']
        verbose_name = "训练记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        desc = f"{self.plan_title}"
        if self.action_name:
            desc += f" - {self.action_name}"
        if self.set_index:
            desc += f" (第{self.set_index}组)"
        return f"{desc} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
