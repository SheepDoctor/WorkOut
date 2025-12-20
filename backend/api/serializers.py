from rest_framework import serializers
from .models import WorkoutPlan, WorkoutLog, WorkoutExercise

class WorkoutExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutExercise
        fields = ['id', 'name', 'total_sets', 'reps_per_set', 'current_sets', 'tips', 'start_time', 'end_time', 'seconds', 'gif_url', 'category', 'muscle_group', 'order']

class WorkoutPlanSerializer(serializers.ModelSerializer):
    exercises = WorkoutExerciseSerializer(many=True, required=False)
    
    class Meta:
        model = WorkoutPlan
        fields = ['id', 'title', 'created_at', 'is_default', 'exercises']

    def create(self, validated_data):
        exercises_data = validated_data.pop('exercises', [])
        plan = WorkoutPlan.objects.create(**validated_data)
        
        # 获取模型的所有有效字段名
        model_fields = [f.name for f in WorkoutExercise._meta.get_fields()]
        
        for exercise_data in exercises_data:
            # 过滤掉不在模型中的字段，增强鲁棒性
            valid_fields = {k: v for k, v in exercise_data.items() if k in model_fields}
            WorkoutExercise.objects.create(plan=plan, **valid_fields)
        return plan

    def update(self, instance, validated_data):
        exercises_data = validated_data.pop('exercises', None)
        
        # Update plan basic info
        instance.title = validated_data.get('title', instance.title)
        instance.is_default = validated_data.get('is_default', instance.is_default)
        instance.save()

        # 获取模型的所有有效字段名
        model_fields = [f.name for f in WorkoutExercise._meta.get_fields()]

        # Update exercises if provided
        if exercises_data is not None:
            instance.exercises.all().delete()
            for exercise_data in exercises_data:
                valid_fields = {k: v for k, v in exercise_data.items() if k in model_fields}
                WorkoutExercise.objects.create(plan=instance, **valid_fields)
        
        return instance

class WorkoutLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutLog
        fields = '__all__'
    
    def to_representation(self, instance):
        """自定义序列化，确保 JSONField 正确序列化"""
        log_id = getattr(instance, "id", "unknown")
        print(f'[WorkoutLogSerializer] ========== 序列化日志 ID: {log_id} ==========')
        try:
            # 检查实例是否有效
            if instance is None:
                print('[WorkoutLogSerializer] ⚠ 实例为 None')
                return None
            
            # 尝试获取基本数据
            print(f'[WorkoutLogSerializer] 步骤1: 调用父类序列化...')
            try:
                data = super().to_representation(instance)
                print(f'[WorkoutLogSerializer] ✓ 基础序列化成功，字段数: {len(data)}')
            except Exception as e:
                print(f'[WorkoutLogSerializer] ✗ 基础序列化失败: {e}')
                import traceback
                traceback.print_exc()
                # 如果基础序列化失败，手动构建
                print('[WorkoutLogSerializer] 尝试手动构建数据...')
                data = {}
            
            # 确保 JSONField 字段正确序列化
            print(f'[WorkoutLogSerializer] 步骤2: 处理 set_feedback...')
            if hasattr(instance, 'set_feedback'):
                try:
                    if instance.set_feedback is None:
                        data['set_feedback'] = None
                    elif isinstance(instance.set_feedback, (dict, list)):
                        data['set_feedback'] = instance.set_feedback
                    else:
                        # 如果是字符串，尝试解析
                        import json
                        try:
                            data['set_feedback'] = json.loads(instance.set_feedback) if isinstance(instance.set_feedback, str) else instance.set_feedback
                        except:
                            data['set_feedback'] = None
                except Exception as e:
                    print(f'[WorkoutLogSerializer] ⚠ set_feedback 处理失败: {e}')
                    data['set_feedback'] = None
            else:
                data['set_feedback'] = None
            
            print(f'[WorkoutLogSerializer] 步骤3: 处理 data_snapshot...')
            if hasattr(instance, 'data_snapshot'):
                try:
                    if instance.data_snapshot is None:
                        data['data_snapshot'] = None
                    elif isinstance(instance.data_snapshot, (dict, list)):
                        data['data_snapshot'] = instance.data_snapshot
                    else:
                        # 如果是字符串，尝试解析
                        import json
                        try:
                            data['data_snapshot'] = json.loads(instance.data_snapshot) if isinstance(instance.data_snapshot, str) else instance.data_snapshot
                        except:
                            data['data_snapshot'] = None
                except Exception as e:
                    print(f'[WorkoutLogSerializer] ⚠ data_snapshot 处理失败: {e}')
                    data['data_snapshot'] = None
            else:
                data['data_snapshot'] = None
            
            # 确保 start_time 正确序列化
            print(f'[WorkoutLogSerializer] 步骤4: 处理 start_time...')
            if 'start_time' in data:
                try:
                    if data['start_time'] is None:
                        data['start_time'] = None
                    # 如果已经是字符串，保持不变
                    elif isinstance(data['start_time'], str):
                        pass
                    # 如果是 datetime 对象，转换为 ISO 格式
                    elif hasattr(data['start_time'], 'isoformat'):
                        data['start_time'] = data['start_time'].isoformat()
                    # 如果是其他类型，尝试转换
                    else:
                        data['start_time'] = str(data['start_time'])
                except Exception as e:
                    print(f'[WorkoutLogSerializer] ⚠ start_time 处理失败: {e}')
                    data['start_time'] = None
            
            print(f'[WorkoutLogSerializer] ✓ 序列化完成，字段数: {len(data)}')
            return data
        except Exception as e:
            import traceback
            print(f'[WorkoutLogSerializer] ✗ 序列化错误: {e}')
            traceback.print_exc()
            # 返回基本字段，避免完全失败
            try:
                # 尝试手动构建基本字段
                start_time_str = None
                if hasattr(instance, 'start_time') and instance.start_time:
                    try:
                        if hasattr(instance.start_time, 'isoformat'):
                            start_time_str = instance.start_time.isoformat()
                        else:
                            start_time_str = str(instance.start_time)
                    except:
                        start_time_str = None
                
                return {
                    'id': getattr(instance, 'id', None),
                    'plan_title': getattr(instance, 'plan_title', ''),
                    'action_name': getattr(instance, 'action_name', None),
                    'set_index': getattr(instance, 'set_index', None),
                    'reps_count': getattr(instance, 'reps_count', 0),
                    'start_time': start_time_str,
                    'duration': getattr(instance, 'duration', 0),
                    'exercise_id': getattr(instance, 'exercise_id', None),
                    'target_reps': getattr(instance, 'target_reps', None),
                    'target_sets': getattr(instance, 'target_sets', None),
                    'status': getattr(instance, 'status', 'interrupted'),
                    'ai_score': getattr(instance, 'ai_score', None),
                    'ai_feedback': getattr(instance, 'ai_feedback', None),
                    'set_feedback': None,
                    'data_snapshot': None,
                }
            except Exception as e2:
                # 如果连基本字段都获取失败，返回最小信息
                print(f'[WorkoutLogSerializer] ✗ 手动构建也失败: {e2}')
                return {
                    'id': getattr(instance, 'id', None) if hasattr(instance, 'id') else None,
                    'error': f'Serialization error: {str(e)}'
                }