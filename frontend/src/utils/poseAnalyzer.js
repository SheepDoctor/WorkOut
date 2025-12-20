import { Pose } from '@mediapipe/pose';
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils';
import { POSE_CONNECTIONS } from '@mediapipe/pose';
import actionCategories from './action_categories.json';

// 动作分类配置（从配置文件导入）
const ACTION_CATEGORIES = actionCategories;

// MediaPipe PoseLandmark 枚举
const PoseLandmark = {
  NOSE: 0,
  LEFT_EYE_INNER: 1,
  LEFT_EYE: 2,
  LEFT_EYE_OUTER: 3,
  RIGHT_EYE_INNER: 4,
  RIGHT_EYE: 5,
  RIGHT_EYE_OUTER: 6,
  LEFT_EAR: 7,
  RIGHT_EAR: 8,
  MOUTH_LEFT: 9,
  MOUTH_RIGHT: 10,
  LEFT_SHOULDER: 11,
  RIGHT_SHOULDER: 12,
  LEFT_ELBOW: 13,
  RIGHT_ELBOW: 14,
  LEFT_WRIST: 15,
  RIGHT_WRIST: 16,
  LEFT_PINKY: 17,
  RIGHT_PINKY: 18,
  LEFT_INDEX: 19,
  RIGHT_INDEX: 20,
  LEFT_THUMB: 21,
  RIGHT_THUMB: 22,
  LEFT_HIP: 23,
  RIGHT_HIP: 24,
  LEFT_KNEE: 25,
  RIGHT_KNEE: 26,
  LEFT_ANKLE: 27,
  RIGHT_ANKLE: 28,
  LEFT_HEEL: 29,
  RIGHT_HEEL: 30,
  LEFT_FOOT_INDEX: 31,
  RIGHT_FOOT_INDEX: 32
};

function calculateAngle(p1, p2, p3) {
  const a = [p1.x, p1.y];
  const b = [p2.x, p2.y];
  const c = [p3.x, p3.y];
  
  const radians = Math.atan2(c[1] - b[1], c[0] - b[0]) - Math.atan2(a[1] - b[1], a[0] - b[0]);
  let angle = Math.abs(radians * 180.0 / Math.PI);
  
  if (angle > 180.0) {
    angle = 360 - angle;
  }
  
  return angle;
}

function getLandmark(landmarks, name) {
  return landmarks[PoseLandmark[name]];
}

function detectAction(categoryKey, landmarks) {
  if (!categoryKey || !ACTION_CATEGORIES[categoryKey]) {
    return { state: null, value: 0, leftValue: null, rightValue: null, message: "未知动作类型" };
  }

  const config = ACTION_CATEGORIES[categoryKey];

  try {
    if (config.detection_type === 'angle') {
      // 计算左右两侧的角度
      const leftConfig = {
        point1: config.landmarks.point1.replace('LEFT_', 'LEFT_'),
        point2: config.landmarks.point2.replace('LEFT_', 'LEFT_'),
        point3: config.landmarks.point3.replace('LEFT_', 'LEFT_')
      };

      const rightConfig = {
        point1: config.landmarks.point1.replace('LEFT_', 'RIGHT_'),
        point2: config.landmarks.point2.replace('LEFT_', 'RIGHT_'),
        point3: config.landmarks.point3.replace('LEFT_', 'RIGHT_')
      };

      // 计算左侧角度
      let leftVal = null;
      try {
        const p1L = getLandmark(landmarks, leftConfig.point1);
        const p2L = getLandmark(landmarks, leftConfig.point2);
        const p3L = getLandmark(landmarks, leftConfig.point3);

        if (p1L.visibility > 0.5 && p2L.visibility > 0.5 && p3L.visibility > 0.5) {
          leftVal = calculateAngle(p1L, p2L, p3L);
        }
      } catch (e) {
        // 左侧角度计算失败
      }

      // 计算右侧角度
      let rightVal = null;
      try {
        const p1R = getLandmark(landmarks, rightConfig.point1);
        const p2R = getLandmark(landmarks, rightConfig.point2);
        const p3R = getLandmark(landmarks, rightConfig.point3);

        if (p1R.visibility > 0.5 && p2R.visibility > 0.5 && p3R.visibility > 0.5) {
          rightVal = calculateAngle(p1R, p2R, p3R);
        }
      } catch (e) {
        // 右侧角度计算失败
      }

      if (leftVal === null && rightVal === null) {
        return { state: null, value: 0, leftValue: null, rightValue: null, message: "关键点不可见" };
      }

      // 使用平均值作为主要值
      const avgVal = [leftVal, rightVal].filter(v => v !== null).reduce((a, b) => a + b, 0) /
                     [leftVal, rightVal].filter(v => v !== null).length;

      // 简单的状态判断（这里可以根据阈值进一步优化）
      return {
        state: "DETECTED",
        value: avgVal,
        leftValue: leftVal,
        rightValue: rightVal,
        message: `${config.name} 检测中`
      };

    } else if (config.detection_type === 'height') {
      // 计算左右两侧的高度差
      let leftVal = null;
      let rightVal = null;

      try {
        const p1L = getLandmark(landmarks, config.landmarks.point1.replace('LEFT_', 'LEFT_'));
        const p2L = getLandmark(landmarks, config.landmarks.point2.replace('LEFT_', 'LEFT_'));

        if (p1L.visibility > 0.5 && p2L.visibility > 0.5) {
          leftVal = p1L.y - p2L.y;
        }
      } catch (e) {
        // 左侧高度计算失败
      }

      try {
        const p1R = getLandmark(landmarks, config.landmarks.point1.replace('LEFT_', 'RIGHT_'));
        const p2R = getLandmark(landmarks, config.landmarks.point2.replace('LEFT_', 'RIGHT_'));

        if (p1R.visibility > 0.5 && p2R.visibility > 0.5) {
          rightVal = p1R.y - p2R.y;
        }
      } catch (e) {
        // 右侧高度计算失败
      }

      if (leftVal === null && rightVal === null) {
        return { state: null, value: 0, leftValue: null, rightValue: null, message: "关键点不可见" };
      }

      // 使用平均值作为主要值
      const avgVal = [leftVal, rightVal].filter(v => v !== null).reduce((a, b) => a + b, 0) /
                     [leftVal, rightVal].filter(v => v !== null).length;

      return {
        state: "DETECTED",
        value: avgVal,
        leftValue: leftVal,
        rightValue: rightVal,
        message: `${config.name} 检测中`
      };
    }
  } catch (e) {
    return { state: null, value: 0, leftValue: null, rightValue: null, message: `检测出错: ${e.message}` };
  }

  return { state: "UNKNOWN", value: 0, leftValue: null, rightValue: null, message: "无法判断状态" };
}

function detectSquat(landmarks) {
  const leftHip = landmarks[PoseLandmark.LEFT_HIP];
  const leftKnee = landmarks[PoseLandmark.LEFT_KNEE];
  const leftAnkle = landmarks[PoseLandmark.LEFT_ANKLE];
  
  const rightHip = landmarks[PoseLandmark.RIGHT_HIP];
  const rightKnee = landmarks[PoseLandmark.RIGHT_KNEE];
  const rightAnkle = landmarks[PoseLandmark.RIGHT_ANKLE];
  
  if (leftHip.visibility < 0.5 || leftKnee.visibility < 0.5 || leftAnkle.visibility < 0.5) {
    return { state: null, value: 0, message: "未检测到完整的腿部，请调整站位" };
  }
  
  const leftAngle = calculateAngle(leftHip, leftKnee, leftAnkle);
  const rightAngle = calculateAngle(rightHip, rightKnee, rightAnkle);
  const avgAngle = (leftAngle + rightAngle) / 2;
  
  let state = "UNKNOWN";
  let message = "";
  
  if (avgAngle > 150) {
    state = "UP";
    message = "站立准备";
  } else if (avgAngle < 130) {
    state = "DOWN";
    message = "下蹲到位";
  } else {
    state = "TRANSITION";
    message = "动作进行中";
  }
  
  return { state, value: avgAngle, message };
}

function detectCurl(landmarks) {
  const leftShoulder = landmarks[PoseLandmark.LEFT_SHOULDER];
  const leftElbow = landmarks[PoseLandmark.LEFT_ELBOW];
  const leftWrist = landmarks[PoseLandmark.LEFT_WRIST];
  
  const rightShoulder = landmarks[PoseLandmark.RIGHT_SHOULDER];
  const rightElbow = landmarks[PoseLandmark.RIGHT_ELBOW];
  const rightWrist = landmarks[PoseLandmark.RIGHT_WRIST];
  
  let angle = 0;
  let targetArm = "right";
  
  if (rightShoulder.visibility > 0.5 && rightElbow.visibility > 0.5 && rightWrist.visibility > 0.5) {
    targetArm = "right";
    angle = calculateAngle(rightShoulder, rightElbow, rightWrist);
  } else if (leftShoulder.visibility > 0.5 && leftElbow.visibility > 0.5 && leftWrist.visibility > 0.5) {
    targetArm = "left";
    angle = calculateAngle(leftShoulder, leftElbow, leftWrist);
  } else {
    return { state: null, value: 0, message: "未检测到手臂" };
  }
  
  let state = "UNKNOWN";
  let message = "";
  
  if (angle > 145) {
    state = "DOWN";
    message = "手臂已放下";
  } else if (angle < 85) {
    state = "UP";
    message = "弯举到位";
  } else {
    state = "TRANSITION";
    message = "弯举中";
  }
  
  return { state, value: angle, message };
}

function detectPress(landmarks) {
  const leftShoulder = landmarks[PoseLandmark.LEFT_SHOULDER];
  const leftElbow = landmarks[PoseLandmark.LEFT_ELBOW];
  const leftWrist = landmarks[PoseLandmark.LEFT_WRIST];
  
  const rightShoulder = landmarks[PoseLandmark.RIGHT_SHOULDER];
  const rightElbow = landmarks[PoseLandmark.RIGHT_ELBOW];
  const rightWrist = landmarks[PoseLandmark.RIGHT_WRIST];
  
  const leftVisible = leftShoulder.visibility > 0.5 && leftElbow.visibility > 0.5 && leftWrist.visibility > 0.5;
  const rightVisible = rightShoulder.visibility > 0.5 && rightElbow.visibility > 0.5 && rightWrist.visibility > 0.5;
  
  if (!leftVisible && !rightVisible) {
    return { state: null, value: 0, message: "未检测到手臂" };
  }
  
  const angles = [];
  
  if (leftVisible && leftWrist.y < leftShoulder.y) {
    angles.push(calculateAngle(leftShoulder, leftElbow, leftWrist));
  }
  
  if (rightVisible && rightWrist.y < rightShoulder.y) {
    angles.push(calculateAngle(rightShoulder, rightElbow, rightWrist));
  }
  
  if (angles.length === 0) {
    return { state: null, value: 0, message: "请举起双手至肩部以上" };
  }
  
  const avgAngle = angles.reduce((a, b) => a + b, 0) / angles.length;
  
  let state = "UNKNOWN";
  let message = "";
  
  if (avgAngle > 150) {
    state = "UP";
    message = "推举到位";
  } else if (avgAngle < 100) {
    state = "DOWN";
    message = "下放到位";
  } else {
    state = "TRANSITION";
    message = "发力中";
  }
  
  return { state, value: avgAngle, message };
}

function analyzePoseQuality(landmarks) {
  const feedback = [];
  
  const leftShoulder = landmarks[PoseLandmark.LEFT_SHOULDER];
  const leftElbow = landmarks[PoseLandmark.LEFT_ELBOW];
  const leftWrist = landmarks[PoseLandmark.LEFT_WRIST];
  
  const rightShoulder = landmarks[PoseLandmark.RIGHT_SHOULDER];
  const rightElbow = landmarks[PoseLandmark.RIGHT_ELBOW];
  const rightWrist = landmarks[PoseLandmark.RIGHT_WRIST];
  
  const leftHip = landmarks[PoseLandmark.LEFT_HIP];
  const leftKnee = landmarks[PoseLandmark.LEFT_KNEE];
  const leftAnkle = landmarks[PoseLandmark.LEFT_ANKLE];
  
  const rightHip = landmarks[PoseLandmark.RIGHT_HIP];
  const rightKnee = landmarks[PoseLandmark.RIGHT_KNEE];
  const rightAnkle = landmarks[PoseLandmark.RIGHT_ANKLE];
  
  // 分析左臂角度
  if (leftShoulder.visibility > 0.5 && leftElbow.visibility > 0.5 && leftWrist.visibility > 0.5) {
    const leftArmAngle = calculateAngle(leftShoulder, leftElbow, leftWrist);
    if (leftArmAngle < 150) {
      feedback.push({
        type: 'warning',
        message: '左臂可以更伸直一些',
        body_part: 'left_arm'
      });
    } else if (leftArmAngle > 180) {
      feedback.push({
        type: 'info',
        message: '左臂姿势良好',
        body_part: 'left_arm'
      });
    }
  }
  
  // 分析右臂角度
  if (rightShoulder.visibility > 0.5 && rightElbow.visibility > 0.5 && rightWrist.visibility > 0.5) {
    const rightArmAngle = calculateAngle(rightShoulder, rightElbow, rightWrist);
    if (rightArmAngle < 150) {
      feedback.push({
        type: 'warning',
        message: '右臂可以更伸直一些',
        body_part: 'right_arm'
      });
    } else if (rightArmAngle > 180) {
      feedback.push({
        type: 'info',
        message: '右臂姿势良好',
        body_part: 'right_arm'
      });
    }
  }
  
  // 分析左腿角度
  if (leftHip.visibility > 0.5 && leftKnee.visibility > 0.5 && leftAnkle.visibility > 0.5) {
    const leftLegAngle = calculateAngle(leftHip, leftKnee, leftAnkle);
    if (leftLegAngle < 150) {
      feedback.push({
        type: 'warning',
        message: '左腿可以更伸直一些',
        body_part: 'left_leg'
      });
    }
  }
  
  // 分析右腿角度
  if (rightHip.visibility > 0.5 && rightKnee.visibility > 0.5 && rightAnkle.visibility > 0.5) {
    const rightLegAngle = calculateAngle(rightHip, rightKnee, rightAnkle);
    if (rightLegAngle < 150) {
      feedback.push({
        type: 'warning',
        message: '右腿可以更伸直一些',
        body_part: 'right_leg'
      });
    }
  }
  
  // 分析身体平衡
  if (leftShoulder.visibility > 0.5 && rightShoulder.visibility > 0.5 &&
      leftHip.visibility > 0.5 && rightHip.visibility > 0.5) {
    const shoulderDiff = Math.abs(leftShoulder.y - rightShoulder.y);
    const hipDiff = Math.abs(leftHip.y - rightHip.y);
    
    if (shoulderDiff > 0.05 || hipDiff > 0.05) {
      feedback.push({
        type: 'warning',
        message: '注意保持身体平衡，肩膀和髋部应该在同一水平线上',
        body_part: 'balance'
      });
    } else {
      feedback.push({
        type: 'success',
        message: '身体平衡良好',
        body_part: 'balance'
      });
    }
  }
  
  if (feedback.length === 0) {
    feedback.push({
      type: 'info',
      message: '姿态检测正常，继续保持',
      body_part: 'general'
    });
  }
  
  return feedback;
}

export class PoseAnalyzer {
  constructor() {
    this.pose = null;
    this.isInitialized = false;
    this.initPromise = null;
    this.currentResolve = null;
    this.currentExerciseType = null;
    this.currentCanvas = null;
    this.currentVideo = null;
  }

  async initialize() {
    if (this.isInitialized) {
      return;
    }

    if (this.initPromise) {
      return this.initPromise;
    }

    this.initPromise = this._initPose();
    return this.initPromise;
  }

  async _initPose() {
    try {
      // 使用更稳定的 MediaPipe 初始化方式
      this.pose = new Pose({
        locateFile: (file) => {
          // 使用广泛测试的稳定版本
          return `https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.4.1633558788/${file}`;
        }
      });

      // 等待初始化完成
      await this.pose.initialize();

      // 设置选项，使用更保守的参数避免 WASM 问题
      this.pose.setOptions({
        modelComplexity: 0, // 使用最简单的模型以提高稳定性
        smoothLandmarks: false, // 关闭平滑以减少内存使用
        enableSegmentation: false,
        smoothSegmentation: false,
        minDetectionConfidence: 0.5, // 提高置信度阈值
        minTrackingConfidence: 0.5
      });

      // 设置持续的回调
      this.pose.onResults((results) => {
        if (this.currentResolve && this.currentCanvas && this.currentVideo) {
          try {
            this.processResults(results);
          } catch (error) {
            console.error('Error processing pose results:', error);
            this.currentResolve({
              feedback: [{ type: 'error', message: '姿态分析处理出错' }],
              annotatedImage: null,
              landmarksDetected: false,
              poseState: 'UNKNOWN',
              poseAngle: 0,
              leftValue: null,
              rightValue: null,
              exerciseType: this.currentExerciseType
            });
          }
        }
      });

      this.isInitialized = true;
      console.log('MediaPipe Pose initialized successfully');
    } catch (error) {
      console.error('Failed to initialize MediaPipe Pose:', error);
      // 重置状态以便重试
      this.isInitialized = false;
      this.initPromise = null;
      throw error;
    }
  }
  
  processResults(results) {
    console.log('--- PoseAnalyzer.processResults ---');
    const feedback = [];
    let poseState = "UNKNOWN";
    let poseAngle = 0;
    let landmarksDetected = false;
    
    if (results.poseLandmarks) {
      landmarksDetected = true;
      
      // 绘制姿态
      const ctx = this.currentCanvas.getContext('2d');
      ctx.save();
      ctx.clearRect(0, 0, this.currentCanvas.width, this.currentCanvas.height);
      ctx.drawImage(this.currentVideo, 0, 0, this.currentCanvas.width, this.currentCanvas.height);
      
      // 根据动作类型进行分析
      if (this.currentExerciseType && ACTION_CATEGORIES[this.currentExerciseType]) {
        const result = detectAction(this.currentExerciseType, results.poseLandmarks);
        if (result.state) {
          poseState = result.state;
          poseAngle = result.value;
          feedback.push({ type: 'info', message: result.message });
        } else {
          feedback.push({ type: 'warning', message: result.message });
        }

        // 绘制辅助点和辅助线
        this.drawActionHelpers(ctx, results.poseLandmarks, this.currentExerciseType);
      } else {
        // 通用姿态分析
        feedback.push(...analyzePoseQuality(results.poseLandmarks));
      }
      
      ctx.restore();
    } else {
      feedback.push({ type: 'warning', message: '未检测到人体，请调整站位' });
      poseState = "UNKNOWN";
    }
    
    const resolve = this.currentResolve;
    const canvas = this.currentCanvas;
    const exerciseType = this.currentExerciseType;

    // 清除当前状态
    this.currentResolve = null;
    this.currentCanvas = null;
    this.currentVideo = null;
    this.currentExerciseType = null;

    resolve({
      feedback,
      annotatedImage: canvas.toDataURL('image/jpeg'),
      landmarksDetected,
      poseState,
      poseAngle,
      leftValue: poseAngle, // 暂时使用相同的值，需要进一步优化
      rightValue: poseAngle,
      exerciseType
    });
  }
  
  async analyzeFrame(videoElement, canvasElement, exerciseType) {
    console.log('--- PoseAnalyzer.analyzeFrame ---');
    console.log(`Exercise Type: ${exerciseType}`);
    // 确保 MediaPipe 已初始化
    await this.initialize();

    return new Promise((resolve, reject) => {
      try {
        // 检查 pose 对象是否可用
        if (!this.pose) {
          reject(new Error('Pose analyzer not initialized'));
          return;
        }

        // 保存当前状态
        this.currentResolve = resolve;
        this.currentCanvas = canvasElement;
        this.currentVideo = videoElement;
        this.currentExerciseType = exerciseType;

        // 处理视频帧
        this.pose.send({ image: videoElement });
      } catch (error) {
        console.error('Error sending image to MediaPipe:', error);
        reject(error);
      }
    });
  }
  
  // 绘制动作辅助点和辅助线
  drawActionHelpers(ctx, landmarks, exerciseType) {
    if (!ACTION_CATEGORIES[exerciseType]) {
      return;
    }

    const config = ACTION_CATEGORIES[exerciseType];
    const canvasWidth = ctx.canvas.width;
    const canvasHeight = ctx.canvas.height;

    // 保存上下文状态
    ctx.save();

    try {
      if (config.detection_type === 'angle' && config.landmarks.point1 && config.landmarks.point2 && config.landmarks.point3) {
        // 绘制角度辅助线
        this.drawAngleHelper(ctx, landmarks, config.landmarks, canvasWidth, canvasHeight);
      } else if (config.detection_type === 'height' && config.landmarks.point1 && config.landmarks.point2) {
        // 绘制高度辅助线
        this.drawHeightHelper(ctx, landmarks, config.landmarks, canvasWidth, canvasHeight);
      }
    } catch (error) {
      console.warn('Error drawing action helpers:', error);
    }

    // 恢复上下文状态
    ctx.restore();
  }

  // 绘制角度辅助线
  drawAngleHelper(ctx, landmarks, landmarkConfig, canvasWidth, canvasHeight) {
    const p1 = getLandmark(landmarks, landmarkConfig.point1);
    const p2 = getLandmark(landmarks, landmarkConfig.point2);
    const p3 = getLandmark(landmarks, landmarkConfig.point3);

    if (p1.visibility < 0.5 || p2.visibility < 0.5 || p3.visibility < 0.5) {
      return;
    }

    // 转换为画布坐标
    const scaleX = canvasWidth;
    const scaleY = canvasHeight;

    const point1 = { x: p1.x * scaleX, y: p1.y * scaleY };
    const point2 = { x: p2.x * scaleX, y: p2.y * scaleY };
    const point3 = { x: p3.x * scaleX, y: p3.y * scaleY };

    // 绘制连接线
    ctx.strokeStyle = '#00FF00';
    ctx.lineWidth = 3;
    ctx.setLineDash([]);

    // 绘制三点连线
    ctx.beginPath();
    ctx.moveTo(point1.x, point1.y);
    ctx.lineTo(point2.x, point2.y);
    ctx.lineTo(point3.x, point3.y);
    ctx.stroke();

    // 绘制延长线（用于角度可视化）
    this.drawExtendedLines(ctx, point1, point2, point3);

    // 绘制关键点
    this.drawHelperPoints(ctx, [point1, point2, point3], '#00FF00');

    // 计算并显示角度
    const angle = calculateAngle(p1, p2, p3);
    this.drawAngleText(ctx, point2, angle);
  }

  // 绘制高度辅助线
  drawHeightHelper(ctx, landmarks, landmarkConfig, canvasWidth, canvasHeight) {
    const p1 = getLandmark(landmarks, landmarkConfig.point1);
    const p2 = getLandmark(landmarks, landmarkConfig.point2);

    if (p1.visibility < 0.5 || p2.visibility < 0.5) {
      return;
    }

    const scaleX = canvasWidth;
    const scaleY = canvasHeight;

    const point1 = { x: p1.x * scaleX, y: p1.y * scaleY };
    const point2 = { x: p2.x * scaleX, y: p2.y * scaleY };

    // 绘制垂直参考线
    ctx.strokeStyle = '#FF6B35';
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);

    ctx.beginPath();
    ctx.moveTo(point1.x, 0);
    ctx.lineTo(point1.x, canvasHeight);
    ctx.stroke();

    // 绘制连接线
    ctx.strokeStyle = '#00FF00';
    ctx.lineWidth = 3;
    ctx.setLineDash([]);

    ctx.beginPath();
    ctx.moveTo(point1.x, point1.y);
    ctx.lineTo(point2.x, point2.y);
    ctx.stroke();

    // 绘制关键点
    this.drawHelperPoints(ctx, [point1, point2], '#00FF00');

    // 显示高度差
    const heightDiff = (p1.y - p2.y).toFixed(3);
    this.drawHeightText(ctx, point2, heightDiff);
  }

  // 绘制延长线用于角度可视化
  drawExtendedLines(ctx, point1, point2, point3) {
    // 计算延长线的方向
    const extensionLength = 50;

    // 从 point1 到 point2 的向量
    const v1 = { x: point2.x - point1.x, y: point2.y - point1.y };
    const len1 = Math.sqrt(v1.x * v1.x + v1.y * v1.y);
    const unitV1 = { x: v1.x / len1, y: v1.y / len1 };

    // 从 point3 到 point2 的向量
    const v2 = { x: point2.x - point3.x, y: point2.y - point3.y };
    const len2 = Math.sqrt(v2.x * v2.x + v2.y * v2.y);
    const unitV2 = { x: v2.x / len2, y: v2.y / len2 };

    // 绘制延长线
    ctx.strokeStyle = '#FFFF00';
    ctx.lineWidth = 2;
    ctx.setLineDash([3, 3]);

    // 第一条延长线
    ctx.beginPath();
    ctx.moveTo(point1.x, point1.y);
    ctx.lineTo(point1.x - unitV1.x * extensionLength, point1.y - unitV1.y * extensionLength);
    ctx.stroke();

    // 第二条延长线
    ctx.beginPath();
    ctx.moveTo(point3.x, point3.y);
    ctx.lineTo(point3.x - unitV2.x * extensionLength, point3.y - unitV2.y * extensionLength);
    ctx.stroke();
  }

  // 绘制辅助点
  drawHelperPoints(ctx, points, color) {
    ctx.fillStyle = color;
    points.forEach(point => {
      ctx.beginPath();
      ctx.arc(point.x, point.y, 6, 0, 2 * Math.PI);
      ctx.fill();

      // 添加白色边框
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 2;
      ctx.stroke();
    });
  }

  // 绘制角度文本
  drawAngleText(ctx, centerPoint, angle) {
    ctx.fillStyle = '#FFFFFF';
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 3;
    ctx.font = '16px Arial';
    ctx.textAlign = 'center';

    const text = `${angle.toFixed(1)}°`;
    const textX = centerPoint.x;
    const textY = centerPoint.y - 20;

    // 绘制文本背景
    const textMetrics = ctx.measureText(text);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(textX - textMetrics.width / 2 - 5, textY - 16, textMetrics.width + 10, 20);

    // 绘制文本
    ctx.fillStyle = '#FFFFFF';
    ctx.fillText(text, textX, textY);
  }

  // 绘制高度文本
  drawHeightText(ctx, point, heightDiff) {
    ctx.fillStyle = '#FFFFFF';
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 3;
    ctx.font = '14px Arial';
    ctx.textAlign = 'left';

    const text = `高度差: ${heightDiff}`;
    const textX = point.x + 10;
    const textY = point.y;

    // 绘制文本背景
    const textMetrics = ctx.measureText(text);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(textX - 5, textY - 16, textMetrics.width + 10, 20);

    // 绘制文本
    ctx.fillStyle = '#FFFFFF';
    ctx.fillText(text, textX, textY);
  }

  close() {
    if (this.pose) {
      try {
        this.pose.close();
      } catch (error) {
        console.warn('Error closing MediaPipe pose:', error);
      }
      this.pose = null;
    }
    this.isInitialized = false;
    this.initPromise = null;
    this.currentResolve = null;
    this.currentCanvas = null;
    this.currentVideo = null;
    this.currentExerciseType = null;
  }
}

