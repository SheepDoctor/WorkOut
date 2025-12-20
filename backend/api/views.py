import re
import requests
from bs4 import BeautifulSoup
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
import cv2
import mediapipe as mp
import numpy as np
from django.http import JsonResponse
import base64


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
    try:
        image_data = request.data.get('image', '')
        exercise_type = request.data.get('exercise_type', 'general') # 获取动作类型
        
        if not image_data:
            return Response({
                'success': False,
                'error': '请提供图像数据'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 解码base64图像
        try:
            # 移除data:image/jpeg;base64,前缀（如果存在）
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return Response({
                    'success': False,
                    'error': '无法解码图像'
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'图像解码失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取当前线程的 Pose 检测器
        pose_detector = get_pose_detector()
        
        # 转换BGR到RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose_detector.process(image_rgb)
        
        # 准备返回数据
        feedback = []
        pose_state = "UNKNOWN"
        pose_angle = 0
        landmarks_detected = False
        
        annotated_image = image.copy()

        # 检测是否检测到人体
        if results.pose_landmarks:
            landmarks_detected = True
            
            # 提取关键点
            landmarks = results.pose_landmarks.landmark
            
            # 绘制姿态
            mp_drawing.draw_landmarks(
                annotated_image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
            )

            # 根据动作类型进行分析
            if exercise_type == 'squat':
                state, angle, msg = detect_squat(landmarks)
                if state:
                    pose_state = state
                    pose_angle = angle
                    feedback.append({'type': 'info', 'message': msg})
                else:
                    feedback.append({'type': 'warning', 'message': msg})
                    
            elif exercise_type == 'curl':
                state, angle, msg = detect_curl(landmarks)
                if state:
                    pose_state = state
                    pose_angle = angle
                    feedback.append({'type': 'info', 'message': msg})
                else:
                    feedback.append({'type': 'warning', 'message': msg})
                    
            elif exercise_type == 'press':
                state, angle, msg = detect_press(landmarks)
                if state:
                    pose_state = state
                    pose_angle = angle
                    feedback.append({'type': 'info', 'message': msg})
                else:
                    feedback.append({'type': 'warning', 'message': msg})
            
            else: # general
                feedback = analyze_pose_quality(landmarks, image.shape)
        else:
            feedback.append({'type': 'warning', 'message': '未检测到人体，请调整站位'})

        # 无论是否检测到，都返回图像，确保前端画面流畅
        _, buffer = cv2.imencode('.jpg', annotated_image)
        annotated_image_base64 = base64.b64encode(buffer).decode('utf-8')
        
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
