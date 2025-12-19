# 智能健身助手 (WorkOut Assistant)

一个功能强大的Android健身应用，可以分析抖音视频、生成健身笔记，并通过摄像头实时指导用户的健身动作。

## 功能特性

### 🎥 视频分析
- 分析抖音视频或本地视频
- 自动识别视频中的健身动作
- 生成详细的健身笔记，包含动作步骤和要点

### 📷 实时动作指导
- 使用摄像头实时检测用户动作
- 与标准动作进行对比
- 提供实时反馈和纠正建议
- 支持多种健身动作的指导

### 📝 笔记管理
- 保存和管理健身笔记
- 查看动作详细步骤和要点
- 支持动作示意图展示

## 技术栈

- **语言**: Kotlin
- **UI框架**: Material Design 3
- **架构**: MVVM (Model-View-ViewModel)
- **导航**: Navigation Component
- **相机**: CameraX
- **AI/ML**: ML Kit Pose Detection
- **异步**: Kotlin Coroutines & Flow
- **图片加载**: Coil

## 项目结构

```
app/src/main/java/com/example/workout/
├── MainActivity.kt                    # 主Activity
├── data/
│   └── model/
│       ├── Exercise.kt               # 动作数据模型
│       └── WorkoutNote.kt           # 笔记数据模型
└── ui/
    ├── home/
    │   └── HomeFragment.kt          # 主页Fragment
    ├── video/
    │   ├── VideoAnalysisFragment.kt  # 视频分析Fragment
    │   └── VideoAnalysisViewModel.kt # 视频分析ViewModel
    ├── camera/
    │   ├── CameraCoachFragment.kt    # 摄像头指导Fragment
    │   └── CameraCoachViewModel.kt   # 摄像头指导ViewModel
    └── notes/
        ├── NotesFragment.kt          # 笔记列表Fragment
        ├── NotesViewModel.kt         # 笔记列表ViewModel
        ├── NoteDetailFragment.kt     # 笔记详情Fragment
        ├── NoteDetailViewModel.kt    # 笔记详情ViewModel
        └── NotesAdapter.kt           # 笔记列表适配器
```

## 安装和运行

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd WorkOut
   ```

2. **使用Android Studio打开项目**
   - 打开Android Studio
   - 选择 "Open an existing project"
   - 选择项目目录

3. **同步Gradle**
   - Android Studio会自动同步Gradle依赖
   - 如果遇到问题，点击 "Sync Project with Gradle Files"

4. **运行应用**
   - 连接Android设备或启动模拟器（API 31+）
   - 点击运行按钮或按 `Shift+F10`

## 权限说明

应用需要以下权限：
- **摄像头权限**: 用于实时动作指导功能
- **存储权限**: 用于选择和分析本地视频文件
- **网络权限**: 用于下载和分析在线视频

## 使用说明

### 视频分析
1. 在主页点击"视频分析"
2. 输入抖音视频链接或选择本地视频
3. 点击"分析视频"按钮
4. 等待分析完成
5. 点击"生成笔记"保存分析结果

### 实时动作指导
1. 在主页点击"动作指导"
2. 允许摄像头权限
3. 点击"开始指导"按钮
4. 站在摄像头前，应用会实时检测你的动作
5. 根据屏幕上的反馈调整动作
6. 点击"停止指导"结束

### 查看笔记
1. 在主页点击"我的笔记"
2. 查看所有保存的健身笔记
3. 点击笔记查看详细信息

## 开发说明

### 视频分析实现
当前版本使用模拟数据进行演示。实际实现需要：
- 视频帧提取
- ML Kit Pose Detection分析每一帧
- 动作识别和分类
- 关键帧提取和示意图生成

### 动作对比算法
- 使用ML Kit检测33个关键点
- 计算关键点之间的距离误差
- 根据误差阈值提供反馈

### 扩展功能建议
- 添加数据库持久化（Room）
- 集成真实的视频下载和分析API
- 添加更多动作类型支持
- 实现动作示意图生成
- 添加用户账户和云端同步

## 注意事项

- 确保设备支持CameraX（Android 5.0+）
- ML Kit需要Google Play Services
- 视频分析功能需要网络连接
- 建议在真实设备上测试摄像头功能

## 许可证

本项目为黑客松比赛项目，仅供学习和演示使用。

## 贡献

欢迎提交Issue和Pull Request！

