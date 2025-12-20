import re
import requests
import os
import tempfile
import uuid
from django.conf import settings
from bs4 import BeautifulSoup
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
import json
import cv2
import mediapipe as mp
import numpy as np
import base64
from .utils.video_analyzer import VideoAnalyzer
from .utils.coach_agent import CoachAgent
from .utils.action_classifier import detect_action, ACTION_CATEGORIES
from .models import WorkoutPlan, WorkoutLog

from rest_framework import viewsets
from .serializers import WorkoutPlanSerializer, WorkoutLogSerializer

class WorkoutPlanViewSet(viewsets.ModelViewSet):
    queryset = WorkoutPlan.objects.all()
    serializer_class = WorkoutPlanSerializer
    
    def list(self, request, *args, **kwargs):
        try:
            print("Fetching all workout plans...")
            return super().list(request, *args, **kwargs)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)

class WorkoutLogViewSet(viewsets.ModelViewSet):
    queryset = WorkoutLog.objects.all()
    serializer_class = WorkoutLogSerializer
    
    def get_queryset(self):
        print('[WorkoutLogViewSet.get_queryset] ========== 构建查询集 ==========')
        try:
            print('[WorkoutLogViewSet.get_queryset] 步骤1: 获取所有日志...')
            queryset = WorkoutLog.objects.all()
            
            print('[WorkoutLogViewSet.get_queryset] 步骤2: 计算初始数量...')
            try:
                initial_count = queryset.count()
                print(f'[WorkoutLogViewSet.get_queryset] 初始查询集数量: {initial_count}')
            except Exception as count_error:
                print(f'[WorkoutLogViewSet.get_queryset] ⚠ 计算数量时出错: {count_error}')
                # 继续执行，不因为计数失败而中断
            
            # 支持按 exercise_id 过滤
            exercise_id = self.request.query_params.get('exercise_id', None)
            if exercise_id:
                print(f'[WorkoutLogViewSet.get_queryset] 步骤3: 按 exercise_id 过滤: {exercise_id}')
                try:
                    queryset = queryset.filter(exercise_id=exercise_id)
                    filtered_count = queryset.count()
                    print(f'[WorkoutLogViewSet.get_queryset] 过滤后数量: {filtered_count}')
                except Exception as filter_error:
                    print(f'[WorkoutLogViewSet.get_queryset] ⚠ exercise_id 过滤失败: {filter_error}')
                    # 如果过滤失败，返回空查询集
                    return WorkoutLog.objects.none()
            
            # 支持按 action_name 过滤
            action_name = self.request.query_params.get('action_name', None)
            if action_name:
                print(f'[WorkoutLogViewSet.get_queryset] 步骤4: 按 action_name 过滤: {action_name}')
                try:
                    queryset = queryset.filter(action_name=action_name)
                    filtered_count = queryset.count()
                    print(f'[WorkoutLogViewSet.get_queryset] 过滤后数量: {filtered_count}')
                except Exception as filter_error:
                    print(f'[WorkoutLogViewSet.get_queryset] ⚠ action_name 过滤失败: {filter_error}')
                    # 如果过滤失败，返回空查询集
                    return WorkoutLog.objects.none()
            
            # 默认按时间倒序
            print('[WorkoutLogViewSet.get_queryset] 步骤5: 按时间排序...')
            try:
                queryset = queryset.order_by('-start_time')
                final_count = queryset.count()
                print(f'[WorkoutLogViewSet.get_queryset] ✓ 查询集构建完成，最终数量: {final_count}')
            except Exception as order_error:
                print(f'[WorkoutLogViewSet.get_queryset] ⚠ 排序失败: {order_error}')
                # 如果排序失败，尝试不排序
                print('[WorkoutLogViewSet.get_queryset] 尝试不排序返回...')
                final_count = queryset.count()
                print(f'[WorkoutLogViewSet.get_queryset] ✓ 查询集构建完成（无排序），最终数量: {final_count}')
            
            return queryset
        except Exception as e:
            import traceback
            print(f'[WorkoutLogViewSet.get_queryset] ✗ 严重错误: {e}')
            traceback.print_exc()
            return WorkoutLog.objects.none()
    
    def list(self, request, *args, **kwargs):
        print('[WorkoutLogViewSet] ========== 获取训练日志列表 ==========')
        print(f'[WorkoutLogViewSet] 请求参数: {request.query_params}')
        try:
            # 获取查询集
            print('[WorkoutLogViewSet] 步骤1: 获取查询集...')
            queryset = self.get_queryset()
            print('[WorkoutLogViewSet] 步骤2: 计算查询集数量...')
            queryset_count = queryset.count()
            print(f'[WorkoutLogViewSet] 查询集数量: {queryset_count}')
            
            # 序列化 - 逐个处理以避免单个记录导致全部失败
            print('[WorkoutLogViewSet] 步骤3: 开始序列化...')
            serializer = self.get_serializer(queryset, many=True)
            print('[WorkoutLogViewSet] 步骤4: 序列化完成，检查数据...')
            
            # 验证序列化数据
            serialized_data = serializer.data
            print(f'[WorkoutLogViewSet] 序列化完成，数据条数: {len(serialized_data)}')
            
            # 检查序列化数据是否有问题
            for idx, item in enumerate(serialized_data):
                if idx < 3:  # 只打印前3条
                    print(f'[WorkoutLogViewSet] 日志 {idx}: id={item.get("id")}, action_name={item.get("action_name")}, status={item.get("status")}')
            
            print('[WorkoutLogViewSet] ✓ 成功返回数据')
            return Response(serialized_data, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            error_msg = str(e)
            error_type = type(e).__name__
            print(f'[WorkoutLogViewSet] ✗ 错误类型: {error_type}')
            print(f'[WorkoutLogViewSet] ✗ 错误消息: {error_msg}')
            print('[WorkoutLogViewSet] 完整堆栈:')
            traceback.print_exc()
            
            # 返回详细的错误信息
            error_response = {
                "error": error_msg,
                "error_type": error_type,
                "detail": "获取训练日志列表时发生错误，请查看后端日志获取详细信息"
            }
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """删除训练记录"""
        try:
            instance = self.get_object()
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error in destroy: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def analyze_video_content(request):
    """
    分析上传的视频，提取健身动作
    """
    try:
        video_file = request.FILES.get('video')
        if not video_file:
            return Response({
                'success': False,
                'error': '请上传视频文件'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 确保媒体目录存在
        gif_dir = os.path.join(settings.MEDIA_ROOT, 'workout_gifs')
        if not os.path.exists(gif_dir):
            os.makedirs(gif_dir)

        # 保存临时文件
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
            for chunk in video_file.chunks():
                temp_video.write(chunk)
            temp_video_path = temp_video.name

        try:
            analyzer = VideoAnalyzer()
            workout_data = analyzer.analyze_video(temp_video_path)
            
            if workout_data:
                # 为每个动作生成 GIF
                exercises = workout_data.get('exercises', [])
                for exercise in exercises:
                    start_time = exercise.get('start_time', '00:00')
                    end_time = exercise.get('end_time', '00:05')
                    
                    # 生成唯一的 GIF 文件名
                    gif_filename = f"ex_{uuid.uuid4().hex[:8]}.gif"
                    gif_path = os.path.join(gif_dir, gif_filename)
                    
                    if analyzer.create_gif(temp_video_path, start_time, end_time, gif_path):
                        # 记录 GIF 的相对 URL
                        exercise['gif_url'] = request.build_absolute_uri(settings.MEDIA_URL + 'workout_gifs/' + gif_filename)
                
                return Response({
                    'success': True,
                    'data': workout_data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': '视频分析失败，请稍后重试'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if os.path.exists(temp_video_path):
                import time
                time.sleep(0.2) # 给 Windows 一点时间释放句柄
                try:
                    os.remove(temp_video_path)
                except Exception as e:
                    print(f"Warning: Could not remove temp video {temp_video_path}: {e}")

    except Exception as e:
        import traceback
        traceback.print_exc()  # 打印详细堆栈到终端
        return Response({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def evaluate_complete_training(request):
    """
    评价完整的训练视频，给出AI综合反馈
    请求参数：
    - video: 训练视频文件
    - workout_plan: 训练计划信息（JSON字符串，包含所有动作信息）
    - plan_id: 训练计划ID（可选，用于关联）
    - log_id: 训练记录ID（可选，如果提供则更新该记录）
    """
    try:
        video_file = request.FILES.get('video')
        workout_plan_str = request.data.get('workout_plan', '[]')
        plan_id = request.data.get('plan_id')
        log_id = request.data.get('log_id')

        if not video_file:
            return Response({
                'success': False,
                'error': '请提供视频文件'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 保存临时视频文件
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
            for chunk in video_file.chunks():
                temp_video.write(chunk)
            temp_video_path = temp_video.name

        # 解析训练计划
        try:
            workout_plan = json.loads(workout_plan_str) if workout_plan_str else []
        except json.JSONDecodeError:
            return Response({
                'success': False,
                'error': '训练计划数据格式错误'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 调用CoachAgent进行综合评价
            coach = CoachAgent()
            feedback_data = coach.analyze_complete_training(
                temp_video_path,
                workout_plan
            )

            # 添加计划相关信息
            feedback_data['plan_id'] = plan_id
            feedback_data['log_id'] = log_id

            # 保存 AI 评价到 WorkoutLog
            if log_id:
                try:
                    workout_log = WorkoutLog.objects.get(id=log_id)
                    workout_log.ai_score = feedback_data.get('score', 0)
                    workout_log.ai_feedback = feedback_data.get('improvement_advice', '') + "\n\n" + feedback_data.get('coach_comment', '')
                    workout_log.save(update_fields=['ai_score', 'ai_feedback'])
                    feedback_data['log_id'] = workout_log.id
                except WorkoutLog.DoesNotExist:
                    pass

            return Response({
                'success': True,
                'data': feedback_data
            }, status=status.HTTP_200_OK)

        finally:
            # 清理临时文件
            if os.path.exists(temp_video_path):
                import time
                time.sleep(0.2)  # 给Windows一点时间释放句柄
                try:
                    os.remove(temp_video_path)
                except Exception as e:
                    print(f"Warning: Could not remove temp video {temp_video_path}: {e}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def analyze_douyin(request):
    """
    分析抖音链接，提取视频或图文信息
    """
    try:
        url = request.data.get('url', '')
        
        if not url:
            return Response({
                'success': False,
                'error': '请提供有效的抖音链接'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证是否为抖音链接
        if 'douyin.com' not in url and 'iesdouyin.com' not in url:
            return Response({
                'success': False,
                'error': '请输入有效的抖音链接'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 提取视频ID
        video_id = None
        patterns = [
            r'/video/(\d+)',
            r'share/video/(\d+)',
            r'v\.douyin\.com/(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                break
        
        # 尝试获取视频信息
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            html = response.text
            
            # 解析HTML获取基本信息
            soup = BeautifulSoup(html, 'html.parser')
            
            # 尝试提取标题
            title = None
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
            
            # 尝试提取描述
            description = None
            desc_tag = soup.find('meta', {'name': 'description'})
            if desc_tag:
                description = desc_tag.get('content', '')
            
            # 尝试提取视频URL或图片URL
            video_url = None
            image_url = None
            
            # 查找视频标签
            video_tag = soup.find('video')
            if video_tag:
                video_url = video_tag.get('src') or video_tag.get('data-src')
            
            # 查找图片标签
            img_tag = soup.find('img')
            if img_tag:
                image_url = img_tag.get('src') or img_tag.get('data-src')
            
            # 检查是否为图文
            is_image_post = image_url and not video_url
            
            result = {
                'success': True,
                'data': {
                    'video_id': video_id,
                    'title': title or '未找到标题',
                    'description': description or '未找到描述',
                    'type': 'image' if is_image_post else 'video',
                    'video_url': video_url,
                    'image_url': image_url,
                    'original_url': url,
                }
            }
            
            return Response(result, status=status.HTTP_200_OK)
            
        except requests.RequestException as e:
            return Response({
                'success': False,
                'error': f'无法访问链接: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': f'分析失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 初始化 MediaPipe 模块
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# 使用线程局部存储，确保多线程环境下的安全性
import threading
thread_local = threading.local()

def get_pose_detector():
    """获取当前线程的 Pose 检测器实例"""
    if not hasattr(thread_local, 'pose_detector'):
        # model_complexity: 0=Lite, 1=Full, 2=Heavy. 
        # 实时应用建议使用 0 或 1。此处改为 1 平衡速度与精度。
        thread_local.pose_detector = mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.3 # 降低置信度阈值，提高检出率
        )
    return thread_local.pose_detector

@api_view(['POST'])
def analyze_pose(request):
    """
    分析用户动作，提供AI指导
    """
    import time
    start_time = time.time()
    print('[AnalyzePose] ========== 收到姿态分析请求 ==========')
    
    try:
        image_data = request.data.get('image', '')
        exercise_type = request.data.get('exercise_type', 'general') # 获取动作类型
        
        print(f'[AnalyzePose] 动作类型: {exercise_type}')
        print(f'[AnalyzePose] 图像数据长度: {len(image_data) if image_data else 0} 字符')
        
        if not image_data:
            print('[AnalyzePose] ✗ 错误: 未提供图像数据')
            return Response({
                'success': False,
                'error': '请提供图像数据'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 解码base64图像
        decode_start = time.time()
        try:
            # 移除data:image/jpeg;base64,前缀（如果存在）
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            print(f'[AnalyzePose] Base64解码完成，图像字节数: {len(image_bytes)}')
            
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                print('[AnalyzePose] ✗ 错误: 无法解码图像')
                return Response({
                    'success': False,
                    'error': '无法解码图像'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            decode_duration = time.time() - decode_start
            print(f'[AnalyzePose] ✓ 图像解码成功，耗时: {decode_duration*1000:.2f}ms')
            print(f'[AnalyzePose] 图像尺寸: {image.shape[1]}x{image.shape[0]}')
            
        except Exception as e:
            print(f'[AnalyzePose] ✗ 图像解码失败: {str(e)}')
            import traceback
            traceback.print_exc()
            return Response({
                'success': False,
                'error': f'图像解码失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取当前线程的 Pose 检测器
        pose_detector = get_pose_detector()
        print('[AnalyzePose] Pose检测器已获取')
        
        # 转换BGR到RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        process_start = time.time()
        results = pose_detector.process(image_rgb)
        process_duration = time.time() - process_start
        print(f'[AnalyzePose] MediaPipe处理完成，耗时: {process_duration*1000:.2f}ms')
        
        # 准备返回数据
        feedback = []
        pose_state = "UNKNOWN"
        pose_angle = 0
        landmarks_detected = False
        
        annotated_image = image.copy()

        # 检测是否检测到人体
        if results.pose_landmarks:
            landmarks_detected = True
            print(f'[AnalyzePose] ✓ 检测到人体姿态，关键点数量: {len(results.pose_landmarks.landmark)}')
            
            # 提取关键点
            landmarks = results.pose_landmarks.landmark
            
            # 绘制姿态 (已禁用辅助点和辅助线展示)
            # mp_drawing.draw_landmarks(
            #     annotated_image,
            #     results.pose_landmarks,
            #     mp_pose.POSE_CONNECTIONS,
            #     mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            #     mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
            # )

            # 根据动作类型进行分析
            analyze_start = time.time()
            if exercise_type in ACTION_CATEGORIES:
                print(f'[AnalyzePose] 使用动作分类器分析: {exercise_type}')
                state, val, msg = detect_action(exercise_type, landmarks, mp_pose)
                if state:
                    pose_state = state
                    pose_angle = val
                    feedback.append({'type': 'info', 'message': msg})
                    print(f'[AnalyzePose] ✓ 动作检测成功 - 状态: {pose_state}, 角度: {pose_angle:.2f}°, 消息: {msg}')
                else:
                    feedback.append({'type': 'warning', 'message': msg})
                    print(f'[AnalyzePose] ⚠ 动作检测失败 - 消息: {msg}')
            elif exercise_type == 'squat':
                print(f'[AnalyzePose] 使用深蹲检测器')
                state, angle, msg = detect_squat(landmarks)
                if state:
                    pose_state = state
                    pose_angle = angle
                    feedback.append({'type': 'info', 'message': msg})
                    print(f'[AnalyzePose] ✓ 深蹲检测成功 - 状态: {pose_state}, 角度: {pose_angle:.2f}°, 消息: {msg}')
                else:
                    feedback.append({'type': 'warning', 'message': msg})
                    print(f'[AnalyzePose] ⚠ 深蹲检测失败 - 消息: {msg}')
                    
            elif exercise_type == 'curl':
                print(f'[AnalyzePose] 使用弯举检测器')
                state, angle, msg = detect_curl(landmarks)
                if state:
                    pose_state = state
                    pose_angle = angle
                    feedback.append({'type': 'info', 'message': msg})
                    print(f'[AnalyzePose] ✓ 弯举检测成功 - 状态: {pose_state}, 角度: {pose_angle:.2f}°, 消息: {msg}')
                else:
                    feedback.append({'type': 'warning', 'message': msg})
                    print(f'[AnalyzePose] ⚠ 弯举检测失败 - 消息: {msg}')
                    
            elif exercise_type == 'press':
                print(f'[AnalyzePose] 使用推举检测器')
                state, angle, msg = detect_press(landmarks)
                if state:
                    pose_state = state
                    pose_angle = angle
                    feedback.append({'type': 'info', 'message': msg})
                    print(f'[AnalyzePose] ✓ 推举检测成功 - 状态: {pose_state}, 角度: {pose_angle:.2f}°, 消息: {msg}')
                else:
                    feedback.append({'type': 'warning', 'message': msg})
                    print(f'[AnalyzePose] ⚠ 推举检测失败 - 消息: {msg}')
            
            else: # general
                print(f'[AnalyzePose] 使用通用姿态质量分析')
                feedback = analyze_pose_quality(landmarks, image.shape)
                print(f'[AnalyzePose] ✓ 通用分析完成，反馈数量: {len(feedback)}')
            
            analyze_duration = time.time() - analyze_start
            print(f'[AnalyzePose] 动作分析耗时: {analyze_duration*1000:.2f}ms')
        else:
            print('[AnalyzePose] ⚠ 未检测到人体姿态')
            feedback.append({'type': 'warning', 'message': '未检测到人体，请调整站位'})

        # 无论是否检测到，都返回图像，确保前端画面流畅
        encode_start = time.time()
        _, buffer = cv2.imencode('.jpg', annotated_image)
        annotated_image_base64 = base64.b64encode(buffer).decode('utf-8')
        encode_duration = time.time() - encode_start
        print(f'[AnalyzePose] 图像编码完成，耗时: {encode_duration*1000:.2f}ms')
        
        total_duration = time.time() - start_time
        print(f'[AnalyzePose] ========== 分析完成，总耗时: {total_duration*1000:.2f}ms ==========')
        print(f'[AnalyzePose] 返回数据 - 状态: {pose_state}, 角度: {pose_angle:.2f}°, 反馈数: {len(feedback)}')
        
        return Response({
            'success': True,
            'data': {
                'feedback': feedback,
                'annotated_image': f'data:image/jpeg;base64,{annotated_image_base64}',
                'landmarks_detected': landmarks_detected,
                'pose_state': pose_state,
                'pose_angle': pose_angle,
                'exercise_type': exercise_type
            }
        }, status=status.HTTP_200_OK)
            
    except Exception as e:
        total_duration = time.time() - start_time
        print(f'[AnalyzePose] ✗ 错误: {str(e)}')
        print(f'[AnalyzePose] 错误发生前耗时: {total_duration*1000:.2f}ms')
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': f'姿态分析失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def calculate_angle(point1, point2, point3):
    """计算三点之间的角度"""
    a = np.array([point1.x, point1.y])
    b = np.array([point2.x, point2.y])
    c = np.array([point3.x, point3.y])
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
    
    return angle


def analyze_pose_quality(landmarks, image_shape):
    """
    分析姿态质量，提供AI指导
    """
    feedback = []
    
    # 获取关键点索引
    mp_pose = mp.solutions.pose
    
    # 左肩、左肘、左手腕
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    
    # 右肩、右肘、右手腕
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
    
    # 左髋、左膝、左脚踝
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    
    # 右髋、右膝、右脚踝
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    
    # 分析左臂角度
    if (left_shoulder.visibility > 0.5 and left_elbow.visibility > 0.5 and 
        left_wrist.visibility > 0.5):
        left_arm_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
        if left_arm_angle < 150:
            feedback.append({
                'type': 'warning',
                'message': '左臂可以更伸直一些',
                'body_part': 'left_arm'
            })
        elif left_arm_angle > 180:
            feedback.append({
                'type': 'info',
                'message': '左臂姿势良好',
                'body_part': 'left_arm'
            })
    
    # 分析右臂角度
    if (right_shoulder.visibility > 0.5 and right_elbow.visibility > 0.5 and 
        right_wrist.visibility > 0.5):
        right_arm_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
        if right_arm_angle < 150:
            feedback.append({
                'type': 'warning',
                'message': '右臂可以更伸直一些',
                'body_part': 'right_arm'
            })
        elif right_arm_angle > 180:
            feedback.append({
                'type': 'info',
                'message': '右臂姿势良好',
                'body_part': 'right_arm'
            })
    
    # 分析左腿角度
    if (left_hip.visibility > 0.5 and left_knee.visibility > 0.5 and 
        left_ankle.visibility > 0.5):
        left_leg_angle = calculate_angle(left_hip, left_knee, left_ankle)
        if left_leg_angle < 150:
            feedback.append({
                'type': 'warning',
                'message': '左腿可以更伸直一些',
                'body_part': 'left_leg'
            })
    
    # 分析右腿角度
    if (right_hip.visibility > 0.5 and right_knee.visibility > 0.5 and 
        right_ankle.visibility > 0.5):
        right_leg_angle = calculate_angle(right_hip, right_knee, right_ankle)
        if right_leg_angle < 150:
            feedback.append({
                'type': 'warning',
                'message': '右腿可以更伸直一些',
                'body_part': 'right_leg'
            })
    
    # 分析身体平衡
    if (left_shoulder.visibility > 0.5 and right_shoulder.visibility > 0.5 and
        left_hip.visibility > 0.5 and right_hip.visibility > 0.5):
        shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
        hip_diff = abs(left_hip.y - right_hip.y)
        
        if shoulder_diff > 0.05 or hip_diff > 0.05:
            feedback.append({
                'type': 'warning',
                'message': '注意保持身体平衡，肩膀和髋部应该在同一水平线上',
                'body_part': 'balance'
            })
        else:
            feedback.append({
                'type': 'success',
                'message': '身体平衡良好',
                'body_part': 'balance'
            })
    
    if not feedback:
        feedback.append({
            'type': 'info',
            'message': '姿态检测正常，继续保持',
            'body_part': 'general'
        })
    
    return feedback


def detect_squat(landmarks):
    """
    检测深蹲动作
    返回: (state, angle, feedback)
    state: 'UP' (站立), 'DOWN' (下蹲)
    """
    mp_pose = mp.solutions.pose
    
    # 获取髋、膝、踝
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    
    # 确保关键点可见
    if (left_hip.visibility < 0.5 or left_knee.visibility < 0.5 or left_ankle.visibility < 0.5):
        return None, 0, "未检测到完整的腿部，请调整站位"

    # 计算膝盖角度
    left_angle = calculate_angle(left_hip, left_knee, left_ankle)
    right_angle = calculate_angle(right_hip, right_knee, right_ankle)
    
    avg_angle = (left_angle + right_angle) / 2
    
    state = "UNKNOWN"
    feedback = ""
    
    if avg_angle > 150:
        state = "UP"
        feedback = "站立准备"
    elif avg_angle < 130:
        state = "DOWN"
        feedback = "下蹲到位"
    else:
        state = "TRANSITION"
        feedback = "动作进行中"
        
    return state, avg_angle, feedback


def detect_curl(landmarks):
    """
    检测哑铃弯举动作 (检测主要活动的手臂)
    返回: (state, angle, feedback)
    state: 'DOWN' (放下), 'UP' (举起)
    """
    mp_pose = mp.solutions.pose
    
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
    
    # 判断哪只手臂在运动（可以通过手腕高度或变化幅度，简单起见检测可见度高且角度小的那只）
    # 这里简单处理：优先检测右臂，如果右臂不可见则检测左臂
    
    target_arm = "right"
    angle = 0
    
    if right_shoulder.visibility > 0.5 and right_elbow.visibility > 0.5 and right_wrist.visibility > 0.5:
        target_arm = "right"
        angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
    elif left_shoulder.visibility > 0.5 and left_elbow.visibility > 0.5 and left_wrist.visibility > 0.5:
        target_arm = "left"
        angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
    else:
        return None, 0, "未检测到手臂"

    state = "UNKNOWN"
    feedback = ""
    
    if angle > 145:
        state = "DOWN"
        feedback = "手臂已放下"
    elif angle < 85: # 放宽判定，小于85度即算到位
        state = "UP"
        feedback = "弯举到位"
    else:
        state = "TRANSITION"
        feedback = "弯举中"
        
    return state, angle, feedback


def detect_press(landmarks):
    """
    检测哑铃推肩动作
    返回: (state, angle, feedback)
    state: 'DOWN' (放下/准备), 'UP' (推起)
    """
    mp_pose = mp.solutions.pose
    
    # 获取关键点
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
    
    # 检查可见性
    left_visible = left_shoulder.visibility > 0.5 and left_elbow.visibility > 0.5 and left_wrist.visibility > 0.5
    right_visible = right_shoulder.visibility > 0.5 and right_elbow.visibility > 0.5 and right_wrist.visibility > 0.5
    
    if not left_visible and not right_visible:
        return None, 0, "未检测到手臂"
        
    # 计算角度和位置
    angles = []
    
    # 关键判定：手腕必须高于肩膀 (y坐标更小)
    # 如果手腕低于肩膀，说明手臂是垂下的，不是推肩姿势
    
    if left_visible and left_wrist.y < left_shoulder.y:
        angles.append(calculate_angle(left_shoulder, left_elbow, left_wrist))
        
    if right_visible and right_wrist.y < right_shoulder.y:
        angles.append(calculate_angle(right_shoulder, right_elbow, right_wrist))
        
    if not angles:
        return None, 0, "请举起双手至肩部以上"
        
    avg_angle = sum(angles) / len(angles)
    
    state = "UNKNOWN"
    feedback = ""
    
    if avg_angle > 150:
        state = "UP"
        feedback = "推举到位"
    elif avg_angle < 100:
        state = "DOWN"
        feedback = "下放到位"
    else:
        state = "TRANSITION"
        feedback = "发力中"
        
    return state, avg_angle, feedback


