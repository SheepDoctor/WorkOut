# Generated migration to clean up data_snapshot field

from django.db import migrations


def cleanup_data_snapshot(apps, schema_editor):
    """
    清理 data_snapshot 字段，只保留必要的ID和关键信息
    移除完整的卡片信息（如 tips, order 等）
    """
    WorkoutLog = apps.get_model('api', 'WorkoutLog')
    
    for log in WorkoutLog.objects.all():
        if not log.data_snapshot:
            continue
            
        snapshot = log.data_snapshot
        
        # 构建新的精简快照，只保留必要字段
        new_snapshot = {}
        
        # 保留必要的字段
        if 'exercise_id' in snapshot:
            new_snapshot['exercise_id'] = snapshot['exercise_id']
        elif 'id' in snapshot:
            new_snapshot['exercise_id'] = snapshot['id']
            
        if 'target_reps' in snapshot:
            new_snapshot['target_reps'] = snapshot['target_reps']
        elif 'reps_per_set' in snapshot:
            new_snapshot['target_reps'] = snapshot['reps_per_set']
            
        if 'target_sets' in snapshot:
            new_snapshot['target_sets'] = snapshot['target_sets']
        elif 'total_sets' in snapshot:
            new_snapshot['target_sets'] = snapshot['total_sets']
            
        if 'reps_done' in snapshot:
            new_snapshot['reps_done'] = snapshot['reps_done']
            
        if 'final_status' in snapshot:
            new_snapshot['final_status'] = snapshot['final_status']
        elif log.status:
            new_snapshot['final_status'] = log.status
            
        # 更新记录
        log.data_snapshot = new_snapshot
        log.save(update_fields=['data_snapshot'])


def reverse_cleanup(apps, schema_editor):
    """
    反向迁移：无法完全恢复，因为原始数据已丢失
    这里不做任何操作
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_remove_workoutplan_data_workoutexercise'),
    ]

    operations = [
        migrations.RunPython(cleanup_data_snapshot, reverse_cleanup),
    ]

