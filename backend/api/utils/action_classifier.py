import numpy as np

ACTION_CATEGORIES = {
    "elbow_dominant": {
        "name": "Elbow Dominant",
        "detection_type": "angle",
        "landmarks": {
            "point1": "LEFT_SHOULDER",
            "point2": "LEFT_ELBOW",
            "point3": "LEFT_WRIST"
        },
        "thresholds": {
            "start_condition": {"operator": "<", "value": 60},
            "end_condition": {"operator": ">", "value": 140}
        }
    },
    "shoulder_dominant": {
        "name": "Shoulder Dominant",
        "detection_type": "height",
        "landmarks": {
            "point1": "LEFT_SHOULDER",
            "point2": "LEFT_WRIST"
        },
        "thresholds": {
            "start_condition": {"operator": "<", "value": -0.2},
            "end_condition": {"operator": ">", "value": 0.02}
        }
    },
    "knee_dominant": {
        "name": "Knee Dominant",
        "detection_type": "angle",
        "landmarks": {
            "point1": "LEFT_HIP",
            "point2": "LEFT_KNEE",
            "point3": "LEFT_ANKLE"
        },
        "thresholds": {
            "start_condition": {"operator": "<", "value": 90},
            "end_condition": {"operator": ">", "value": 160}
        }
    },
    "hip_dominant": {
        "name": "Hip Dominant",
        "detection_type": "angle",
        "landmarks": {
            "point1": "LEFT_SHOULDER",
            "point2": "LEFT_HIP",
            "point3": "LEFT_KNEE"
        },
        "thresholds": {
            "start_condition": {"operator": "<", "value": 120},
            "end_condition": {"operator": ">", "value": 170}
        }
    },
    "core_dominant": {
        "name": "Core Dominant",
        "detection_type": "angle",
        "landmarks": {
            "point1": "LEFT_SHOULDER",
            "point2": "LEFT_HIP",
            "point3": "LEFT_KNEE"
        },
        "thresholds": {
            "start_condition": {"operator": "<", "value": 100},
            "end_condition": {"operator": ">", "value": 160}
        }
    }
}

def calculate_angle(p1, p2, p3):
    """计算三点之间的角度"""
    a = np.array([p1.x, p1.y])
    b = np.array([p2.x, p2.y])
    c = np.array([p3.x, p3.y])
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
    
    return angle

def get_landmark(landmarks, name, mp_pose):
    """根据名称获取 MediaPipe 关键点"""
    return landmarks[getattr(mp_pose.PoseLandmark, name).value]

def detect_action(category_key, landmarks, mp_pose):
    """
    通用动作检测函数
    返回: (state, value, message)
    """
    if category_key not in ACTION_CATEGORIES:
        return None, 0, "未知动作类型"
    
    config = ACTION_CATEGORIES[category_key]
    lms = config['landmarks']
    thresholds = config['thresholds']
    
    try:
        if config['detection_type'] == 'angle':
            p1 = get_landmark(landmarks, lms['point1'], mp_pose)
            p2 = get_landmark(landmarks, lms['point2'], mp_pose)
            p3 = get_landmark(landmarks, lms['point3'], mp_pose)
            
            if p1.visibility < 0.5 or p2.visibility < 0.5 or p3.visibility < 0.5:
                return None, 0, "关键点不可见"
            
            val = calculate_angle(p1, p2, p3)
            
            start_cond = thresholds['start_condition']
            end_cond = thresholds['end_condition']
            
            # 这里简单处理 state：start_condition 满足为 DOWN/START，end_condition 满足为 UP/END
            # 实际上不同的动作可能相反，这里根据 JSON 的逻辑判断
            
            is_start = False
            if start_cond['operator'] == '<':
                is_start = val < start_cond['value']
            elif start_cond['operator'] == '>':
                is_start = val > start_cond['value']
                
            is_end = False
            if end_cond['operator'] == '<':
                is_end = val < end_cond['value']
            elif end_cond['operator'] == '>':
                is_end = val > end_cond['value']
                
            if is_start:
                return "DOWN", val, f"{config['name']} 动作到位"
            elif is_end:
                return "UP", val, f"{config['name']} 准备/起始"
            else:
                return "TRANSITION", val, f"{config['name']} 运动中"

        elif config['detection_type'] == 'height':
            p1 = get_landmark(landmarks, lms['point1'], mp_pose)
            p2 = get_landmark(landmarks, lms['point2'], mp_pose)
            
            if p1.visibility < 0.5 or p2.visibility < 0.5:
                return None, 0, "关键点不可见"
            
            # 高度差 (y 坐标越小越高)
            val = p1.y - p2.y
            
            start_cond = thresholds['start_condition']
            end_cond = thresholds['end_condition']
            
            is_start = False
            if start_cond['operator'] == '<':
                is_start = val < start_cond['value']
            elif start_cond['operator'] == '>':
                is_start = val > start_cond['value']
                
            is_end = False
            if end_cond['operator'] == '<':
                is_end = val < end_cond['value']
            elif end_cond['operator'] == '>':
                is_end = val > end_cond['value']
                
            if is_start:
                return "DOWN", val, f"{config['name']} 准备/起始"
            elif is_end:
                return "UP", val, f"{config['name']} 动作到位"
            else:
                return "TRANSITION", val, f"{config['name']} 运动中"
                
    except Exception as e:
        return None, 0, f"检测出错: {str(e)}"
    
    return "UNKNOWN", 0, "无法判断状态"

