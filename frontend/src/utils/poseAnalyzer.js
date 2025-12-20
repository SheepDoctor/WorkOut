import actionCategories from './action_categories.json';
import posePackageInfo from '@mediapipe/pose/package.json';

// 动态导入 MediaPipe 以避免 Vite 的 ES 模块解析问题
let Pose, drawConnectors, drawLandmarks;
let mediaPipeLoaded = false;

async function loadMediaPipeModules() {
  if (!mediaPipeLoaded) {
    try {
      // 从包根目录导入
      const poseModule = await import('@mediapipe/pose');
      Pose =
        poseModule.Pose ||
        poseModule.default?.Pose ||
        poseModule.default ||
        globalThis.Pose;
      
      const drawingUtilsModule = await import('@mediapipe/drawing_utils');
      drawConnectors =
        drawingUtilsModule.drawConnectors ||
        drawingUtilsModule.default?.drawConnectors ||
        globalThis.drawConnectors;
      drawLandmarks =
        drawingUtilsModule.drawLandmarks ||
        drawingUtilsModule.default?.drawLandmarks ||
        globalThis.drawLandmarks;
      
      mediaPipeLoaded = true;
    } catch (error) {
      console.error('Failed to load MediaPipe modules:', error);
      throw error;
    }
  }
  return { Pose, drawConnectors, drawLandmarks };
}

// 手动定义 POSE_CONNECTIONS（如果从包中导入失败）
// MediaPipe Pose 的 33 个关键点之间的连接关系
const POSE_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 7], // 面部
  [0, 4], [4, 5], [5, 6], [6, 8], // 面部
  [9, 10], // 嘴部
  [11, 12], // 肩膀
  [11, 13], [13, 15], // 左臂
  [15, 17], [15, 19], [15, 21], [17, 19], // 左手
  [12, 14], [14, 16], // 右臂
  [16, 18], [16, 20], [16, 22], [18, 20], // 右手
  [11, 23], [12, 24], // 躯干
  [23, 24], // 臀部
  [23, 25], [25, 27], // 左腿
  [27, 29], [27, 31], [29, 31], // 左脚
  [24, 26], [26, 28], // 右腿
  [28, 30], [28, 32], [30, 32]  // 右脚
];

// 只包含四肢的连接（不包含面部 0-10）
const LIMBS_CONNECTIONS = [
  [11, 12], // 肩膀
  [11, 13], [13, 15], // 左臂
  [15, 17], [15, 19], [15, 21], [17, 19], // 左手
  [12, 14], [14, 16], // 右臂
  [16, 18], [16, 20], [16, 22], [18, 20], // 右手
  [11, 23], [12, 24], // 躯干
  [23, 24], // 臀部
  [23, 25], [25, 27], // 左腿
  [27, 29], [27, 31], [29, 31], // 左脚
  [24, 26], [26, 28], // 右腿
  [28, 30], [28, 32], [30, 32]  // 右脚
];

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

function calculateHeightDiff(p1, p2) {
  return p2.y - p1.y;
}

function getLandmark(landmarks, name) {
  return landmarks[PoseLandmark[name]];
}

// Action Counter 类 - 移植自 Python 代码
class ActionCounter {
  constructor(actionCategory) {
    this.actionCategory = actionCategory;
    this.actionCount = 0;
    this.leftState = "start";
    this.rightState = "start";
    this.lastCountTime = 0;
    this.startTime = Date.now();
    this.startupDelay = 3000; // 3秒启动延迟
    
    // 历史记录用于平滑
    this.leftHistory = [];
    this.rightHistory = [];
    this.valueHistory = [];
    this.maxHistoryLength = 5;
    
    // 速度过滤窗口
    this.leftValWindow = [];
    this.rightValWindow = [];
    this.maxWindowLength = 10;
    this.timeWindow = 400; // 400ms
    this.maxVelocity = {
      angle: 500.0,
      height: 5.0
    };
    
    // 获取检测参数
    if (actionCategory && actionCategories[actionCategory]) {
      this.config = actionCategories[actionCategory];
    } else {
      this.config = null;
    }
  }

  // 检查速度窗口 - 移植自 Python
  checkAccelerationWindow(currentVal, valWindow, maxVelocity) {
    const currentTime = Date.now();
    
    // 添加当前值到窗口
    valWindow.push({ time: currentTime, value: currentVal });
    
    // 保持窗口大小
    if (valWindow.length > this.maxWindowLength) {
      valWindow.shift();
    }
    
    // 移除超出时间窗口的旧值
    while (valWindow.length > 1 && (currentTime - valWindow[0].time > this.timeWindow)) {
      valWindow.shift();
    }
    
    // 至少需要2个点来计算速度
    if (valWindow.length < 2) {
      return true;
    }
    
    const dt = (valWindow[valWindow.length - 1].time - valWindow[0].time) / 1000.0; // 转换为秒
    if (dt < 0.05) {
      return true;
    }
    
    const deltaVal = Math.abs(valWindow[valWindow.length - 1].value - valWindow[0].value);
    const velocity = deltaVal / dt;
    
    if (velocity > maxVelocity) {
      return false;
    }
    
    return true;
  }

  // 平滑处理
  smoothValue(value, history) {
    history.push(value);
    if (history.length > this.maxHistoryLength) {
      history.shift();
    }
    const sum = history.reduce((a, b) => a + b, 0);
    return sum / history.length;
  }

  // 尝试增加计数（带时间限制）
  tryIncrementCount() {
    const currentTime = Date.now();
    if (currentTime - this.lastCountTime >= 1000) { // 1秒内最多计数一次
      this.actionCount++;
      this.lastCountTime = currentTime;
      return true;
    }
    return false;
  }

  // 检测肘部主导动作
  detectElbowDominant(landmarks) {
    const config = this.config;
    if (!config || config.detection_type !== 'angle') return null;

    // 获取左侧关键点
    const leftP1 = getLandmark(landmarks, config.landmarks.point1);
    const leftP2 = getLandmark(landmarks, config.landmarks.point2);
    const leftP3 = getLandmark(landmarks, config.landmarks.point3);
    
    // 获取右侧关键点
    const rightP1Name = config.landmarks.point1.replace('LEFT_', 'RIGHT_');
    const rightP2Name = config.landmarks.point2.replace('LEFT_', 'RIGHT_');
    const rightP3Name = config.landmarks.point3.replace('LEFT_', 'RIGHT_');
    const rightP1 = getLandmark(landmarks, rightP1Name);
    const rightP2 = getLandmark(landmarks, rightP2Name);
    const rightP3 = getLandmark(landmarks, rightP3Name);

      let leftVal = null;
      let rightVal = null;

    // 计算左侧角度
    if (leftP1 && leftP2 && leftP3 &&
        leftP1.visibility > 0.5 && leftP2.visibility > 0.5 && leftP3.visibility > 0.5) {
      leftVal = calculateAngle(leftP1, leftP2, leftP3);
      leftVal = this.smoothValue(leftVal, this.leftHistory);
    }

    // 计算右侧角度
    if (rightP1 && rightP2 && rightP3 &&
        rightP1.visibility > 0.5 && rightP2.visibility > 0.5 && rightP3.visibility > 0.5) {
      rightVal = calculateAngle(rightP1, rightP2, rightP3);
      rightVal = this.smoothValue(rightVal, this.rightHistory);
    }

    // 速度过滤
    let isSafeLeft = true;
    let isSafeRight = true;
    if (leftVal !== null) {
      isSafeLeft = this.checkAccelerationWindow(leftVal, this.leftValWindow, this.maxVelocity.angle);
    }
    if (rightVal !== null) {
      isSafeRight = this.checkAccelerationWindow(rightVal, this.rightValWindow, this.maxVelocity.angle);
    }

    // 阈值
    const startVal = config.thresholds.start_condition.value;
    const endVal = config.thresholds.end_condition.value;

    // 左侧状态机
    if (leftVal !== null && isSafeLeft) {
      if (leftVal < startVal && this.leftState === "end") {
        this.leftState = "start";
      } else if (leftVal > endVal && this.leftState === "start") {
        this.leftState = "end";
        this.tryIncrementCount();
      }
    }

    // 右侧状态机
    if (rightVal !== null && isSafeRight) {
      if (rightVal < startVal && this.rightState === "end") {
        this.rightState = "start";
      } else if (rightVal > endVal && this.rightState === "start") {
        this.rightState = "end";
        this.tryIncrementCount();
      }
    }

    const vals = [];
    if (leftVal !== null) vals.push(leftVal);
    if (rightVal !== null) vals.push(rightVal);
      return {
      value: vals.length > 0 ? vals.reduce((a, b) => a + b, 0) / vals.length : 0,
        leftValue: leftVal,
        rightValue: rightVal,
      leftState: this.leftState,
      rightState: this.rightState
    };
  }

  // 检测肩部主导动作
  detectShoulderDominant(landmarks) {
    const config = this.config;
    if (!config || config.detection_type !== 'height') return null;

    const leftP1 = getLandmark(landmarks, config.landmarks.point1);
    const leftP2 = getLandmark(landmarks, config.landmarks.point2);
    
    const rightP1Name = config.landmarks.point1.replace('LEFT_', 'RIGHT_');
    const rightP2Name = config.landmarks.point2.replace('LEFT_', 'RIGHT_');
    const rightP1 = getLandmark(landmarks, rightP1Name);
    const rightP2 = getLandmark(landmarks, rightP2Name);

    let leftVal = null;
    let rightVal = null;

    if (leftP1 && leftP2 && leftP1.visibility > 0.5 && leftP2.visibility > 0.5) {
      leftVal = calculateHeightDiff(leftP1, leftP2);
      leftVal = this.smoothValue(leftVal, this.leftHistory);
    }

    if (rightP1 && rightP2 && rightP1.visibility > 0.5 && rightP2.visibility > 0.5) {
      rightVal = calculateHeightDiff(rightP1, rightP2);
      rightVal = this.smoothValue(rightVal, this.rightHistory);
    }

    // 速度过滤
    let isSafeLeft = true;
    let isSafeRight = true;
    if (leftVal !== null) {
      isSafeLeft = this.checkAccelerationWindow(leftVal, this.leftValWindow, this.maxVelocity.height);
    }
    if (rightVal !== null) {
      isSafeRight = this.checkAccelerationWindow(rightVal, this.rightValWindow, this.maxVelocity.height);
    }

    // 阈值
    const startOp = config.thresholds.start_condition.operator;
    const startVal = config.thresholds.start_condition.value;
    const endOp = config.thresholds.end_condition.operator;
    const endVal = config.thresholds.end_condition.value;

    // 左侧状态机
    if (leftVal !== null && isSafeLeft) {
      if (startOp === "<" && leftVal < startVal && this.leftState === "end") {
        this.leftState = "start";
      } else if (endOp === ">" && leftVal > endVal && this.leftState === "start") {
        this.leftState = "end";
        this.tryIncrementCount();
      }
    }

    // 右侧状态机
    if (rightVal !== null && isSafeRight) {
      if (startOp === "<" && rightVal < startVal && this.rightState === "end") {
        this.rightState = "start";
      } else if (endOp === ">" && rightVal > endVal && this.rightState === "start") {
        this.rightState = "end";
        this.tryIncrementCount();
      }
    }

    const vals = [];
    if (leftVal !== null) vals.push(leftVal);
    if (rightVal !== null) vals.push(rightVal);
    return {
      value: vals.length > 0 ? vals.reduce((a, b) => a + b, 0) / vals.length : 0,
      leftValue: leftVal,
      rightValue: rightVal,
      leftState: this.leftState,
      rightState: this.rightState
    };
  }

  // 检测膝盖主导动作
  detectKneeDominant(landmarks) {
    const config = this.config;
    if (!config || config.detection_type !== 'angle') return null;

    const leftP1 = getLandmark(landmarks, config.landmarks.point1);
    const leftP2 = getLandmark(landmarks, config.landmarks.point2);
    const leftP3 = getLandmark(landmarks, config.landmarks.point3);
    
    const rightP1Name = config.landmarks.point1.replace('LEFT_', 'RIGHT_');
    const rightP2Name = config.landmarks.point2.replace('LEFT_', 'RIGHT_');
    const rightP3Name = config.landmarks.point3.replace('LEFT_', 'RIGHT_');
    const rightP1 = getLandmark(landmarks, rightP1Name);
    const rightP2 = getLandmark(landmarks, rightP2Name);
    const rightP3 = getLandmark(landmarks, rightP3Name);

    let leftVal = null;
    let rightVal = null;

    if (leftP1 && leftP2 && leftP3 &&
        leftP1.visibility > 0.5 && leftP2.visibility > 0.5 && leftP3.visibility > 0.5) {
      leftVal = calculateAngle(leftP1, leftP2, leftP3);
      leftVal = this.smoothValue(leftVal, this.leftHistory);
    }

    if (rightP1 && rightP2 && rightP3 &&
        rightP1.visibility > 0.5 && rightP2.visibility > 0.5 && rightP3.visibility > 0.5) {
      rightVal = calculateAngle(rightP1, rightP2, rightP3);
      rightVal = this.smoothValue(rightVal, this.rightHistory);
    }

    let isSafeLeft = true;
    let isSafeRight = true;
    if (leftVal !== null) {
      isSafeLeft = this.checkAccelerationWindow(leftVal, this.leftValWindow, this.maxVelocity.angle);
    }
    if (rightVal !== null) {
      isSafeRight = this.checkAccelerationWindow(rightVal, this.rightValWindow, this.maxVelocity.angle);
    }

    const startVal = config.thresholds.start_condition.value;
    const endVal = config.thresholds.end_condition.value;

    if (leftVal !== null && isSafeLeft) {
      if (leftVal < startVal && this.leftState === "end") {
        this.leftState = "start";
      } else if (leftVal > endVal && this.leftState === "start") {
        this.leftState = "end";
        this.tryIncrementCount();
      }
    }

    if (rightVal !== null && isSafeRight) {
      if (rightVal < startVal && this.rightState === "end") {
        this.rightState = "start";
      } else if (rightVal > endVal && this.rightState === "start") {
        this.rightState = "end";
        this.tryIncrementCount();
      }
    }

    const vals = [];
    if (leftVal !== null) vals.push(leftVal);
    if (rightVal !== null) vals.push(rightVal);
    return {
      value: vals.length > 0 ? vals.reduce((a, b) => a + b, 0) / vals.length : 0,
      leftValue: leftVal,
      rightValue: rightVal,
      leftState: this.leftState,
      rightState: this.rightState
    };
  }

  // 检测髋部/核心主导动作
  detectHipCoreDominant(landmarks, isCore = false) {
    const config = this.config;
    if (!config || config.detection_type !== 'angle') return null;

    const leftP1 = getLandmark(landmarks, config.landmarks.point1);
    const leftP2 = getLandmark(landmarks, config.landmarks.point2);
    const leftP3 = getLandmark(landmarks, config.landmarks.point3);
    
    const rightP1Name = config.landmarks.point1.replace('LEFT_', 'RIGHT_');
    const rightP2Name = config.landmarks.point2.replace('LEFT_', 'RIGHT_');
    const rightP3Name = config.landmarks.point3.replace('LEFT_', 'RIGHT_');
    const rightP1 = getLandmark(landmarks, rightP1Name);
    const rightP2 = getLandmark(landmarks, rightP2Name);
    const rightP3 = getLandmark(landmarks, rightP3Name);

    let leftVal = null;
    let rightVal = null;

    if (leftP1 && leftP2 && leftP3 &&
        leftP1.visibility > 0.5 && leftP2.visibility > 0.5 && leftP3.visibility > 0.5) {
      leftVal = calculateAngle(leftP1, leftP2, leftP3);
      leftVal = this.smoothValue(leftVal, this.leftHistory);
    }

    if (rightP1 && rightP2 && rightP3 &&
        rightP1.visibility > 0.5 && rightP2.visibility > 0.5 && rightP3.visibility > 0.5) {
      rightVal = calculateAngle(rightP1, rightP2, rightP3);
      rightVal = this.smoothValue(rightVal, this.rightHistory);
    }

    let isSafeLeft = true;
    let isSafeRight = true;
    if (leftVal !== null) {
      isSafeLeft = this.checkAccelerationWindow(leftVal, this.leftValWindow, this.maxVelocity.angle);
    }
    if (rightVal !== null) {
      isSafeRight = this.checkAccelerationWindow(rightVal, this.rightValWindow, this.maxVelocity.angle);
    }

    const startVal = config.thresholds.start_condition.value;
    const endVal = config.thresholds.end_condition.value;

    if (leftVal !== null && isSafeLeft) {
      if (leftVal < startVal && this.leftState === "end") {
        this.leftState = "start";
      } else if (leftVal > endVal && this.leftState === "start") {
        this.leftState = "end";
        this.tryIncrementCount();
      }
    }

    if (rightVal !== null && isSafeRight) {
      if (rightVal < startVal && this.rightState === "end") {
        this.rightState = "start";
      } else if (rightVal > endVal && this.rightState === "start") {
        this.rightState = "end";
        this.tryIncrementCount();
      }
    }

    const vals = [];
    if (leftVal !== null) vals.push(leftVal);
    if (rightVal !== null) vals.push(rightVal);
    return {
      value: vals.length > 0 ? vals.reduce((a, b) => a + b, 0) / vals.length : 0,
      leftValue: leftVal,
      rightValue: rightVal,
      leftState: this.leftState,
      rightState: this.rightState
    };
  }

  // 检测动作（主入口）
  detectAction(landmarks) {
    // 启动延迟检查
    if (Date.now() - this.startTime < this.startupDelay) {
      return null;
    }

    if (!this.config) {
      return null;
    }

    const category = this.actionCategory;

    if (category === "elbow_dominant") {
      return this.detectElbowDominant(landmarks);
    } else if (category === "shoulder_dominant") {
      return this.detectShoulderDominant(landmarks);
    } else if (category === "knee_dominant") {
      return this.detectKneeDominant(landmarks);
    } else if (category === "hip_dominant") {
      return this.detectHipCoreDominant(landmarks, false);
    } else if (category === "core_dominant") {
      return this.detectHipCoreDominant(landmarks, true);
    }

    return null;
  }

  reset() {
    this.actionCount = 0;
    this.leftState = "start";
    this.rightState = "start";
    this.lastCountTime = 0;
    this.startTime = Date.now();
    this.leftHistory = [];
    this.rightHistory = [];
    this.valueHistory = [];
    this.leftValWindow = [];
    this.rightValWindow = [];
  }

  getCount() {
    return this.actionCount;
  }
}

// 导出的 PoseAnalyzer 类
export class PoseAnalyzer {
  constructor() {
    this.pose = null;
    this.isInitialized = false;
    this.initPromise = null;
    this.actionCounter = null;
    this.currentExerciseCategory = null;
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
    // 首先加载 MediaPipe 模块
    await loadMediaPipeModules();
    
    if (!Pose) {
      throw new Error('Failed to load Pose class from @mediapipe/pose');
    }
    
    // 使用多个 CDN 备用方案，按优先级尝试
    const assetsBaseUrl = new URL('../../node_modules/@mediapipe/pose/', import.meta.url);
    const locateFile = (file) => new URL(file, assetsBaseUrl).href;

    try {
      this.pose = new Pose({
        locateFile
      });

      await this.pose.initialize();

      this.pose.setOptions({
        modelComplexity: 1,
        smoothLandmarks: true,
        enableSegmentation: false,
        smoothSegmentation: false,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
      });

      this.isInitialized = true;
      return;
    } catch (error) {
      console.error('Failed to initialize MediaPipe locally:', error);
      if (this.pose) {
        try {
          this.pose.close();
        } catch (e) {
          // 忽略关闭错误
        }
        this.pose = null;
      }
    }

    this.isInitialized = false;
    this.initPromise = null;
    throw new Error(
      'MediaPipe initialization failed using the locally installed package. Please verify that @mediapipe/pose is installed and the node_modules assets are reachable by Vite.'
    );
  }
  
  setExerciseCategory(category) {
    this.currentExerciseCategory = category;
    if (category) {
      this.actionCounter = new ActionCounter(category);
    } else {
      this.actionCounter = null;
    }
  }

  getActionCount() {
    return this.actionCounter ? this.actionCounter.getCount() : 0;
  }

  resetCounter() {
    if (this.actionCounter) {
      this.actionCounter.reset();
    }
  }

  async analyzeFrame(videoElement, canvasElement) {
    await this.initialize();

    if (!this.pose) {
      throw new Error('Pose analyzer not initialized');
    }

    return new Promise((resolve, reject) => {
      try {
        const callback = async (results) => {
          try {
            let feedback = [];
    let poseState = "UNKNOWN";
    let poseAngle = 0;
            let leftValue = null;
            let rightValue = null;
            let leftState = null;
            let rightState = null;
    let landmarksDetected = false;
    
    if (results.poseLandmarks) {
      landmarksDetected = true;
      
      // 绘制姿态
              const ctx = canvasElement.getContext('2d');
      ctx.save();
              ctx.clearRect(0, 0, canvasElement.width, canvasElement.height);
              ctx.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);

              // 确保 drawConnectors 和 drawLandmarks 已加载
              if (!drawConnectors || !drawLandmarks) {
                await loadMediaPipeModules();
              }
              
              // 只绘制四肢的连接线（不包含面部）
              drawConnectors(ctx, results.poseLandmarks, LIMBS_CONNECTIONS, {
                color: 'rgba(224, 224, 224, 0.4)',
                lineWidth: 1.5
              });
              
              // 手动绘制四肢的关键点（索引11-32，不包含面部0-10）
              ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
              ctx.strokeStyle = 'rgba(255, 255, 255, 0.7)';
              ctx.lineWidth = 1;
              const pointRadius = 2;
              
              // 只绘制索引11-32的关键点（四肢）
              for (let i = 11; i < results.poseLandmarks.length; i++) {
                const landmark = results.poseLandmarks[i];
                if (landmark && landmark.visibility > 0.5) {
                  const x = landmark.x * canvasElement.width;
                  const y = landmark.y * canvasElement.height;
                  
                  ctx.beginPath();
                  ctx.arc(x, y, pointRadius, 0, 2 * Math.PI);
                  ctx.fill();
                }
              }

              // 如果设置了动作类别，使用 ActionCounter 检测
              if (this.actionCounter) {
                const result = this.actionCounter.detectAction(results.poseLandmarks);
                if (result) {
          poseAngle = result.value;
                  leftValue = result.leftValue;
                  rightValue = result.rightValue;
                  leftState = result.leftState;
                  rightState = result.rightState;
                  
                  // 根据状态设置 poseState
                  if (leftState === "end" || rightState === "end") {
                    poseState = "UP";
                  } else if (leftState === "start" || rightState === "start") {
                    poseState = "DOWN";
        } else {
                    poseState = "TRANSITION";
                  }

                  feedback.push({
                    type: 'info',
                    message: `${this.actionCounter.config.name} 检测中`
                  });
                } else {
                  feedback.push({
                    type: 'warning',
                    message: '正在初始化检测...'
                  });
                }
      } else {
        // 通用姿态分析
                feedback.push({
                  type: 'info',
                  message: '姿态检测正常'
                });
      }
      
      ctx.restore();
    } else {
              feedback.push({
                type: 'warning',
                message: '未检测到人体，请调整站位'
              });
            }

    resolve({
      feedback,
              annotatedImage: canvasElement.toDataURL('image/jpeg'),
      landmarksDetected,
      poseState,
      poseAngle,
              leftValue,
              rightValue,
              leftState,
              rightState,
              actionCount: this.getActionCount(),
              exerciseType: this.currentExerciseCategory
            });
          } catch (error) {
            console.error('Error processing pose results:', error);
            reject(error);
          }
        };

        // 只调用一次，使用回调
        this.pose.onResults(callback);
        this.pose.send({ image: videoElement });
      } catch (error) {
        console.error('Error sending image to MediaPipe:', error);
        reject(error);
      }
    });
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
    this.actionCounter = null;
    this.currentExerciseCategory = null;
  }
}
