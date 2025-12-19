# WorkOut - 健身指导Web应用

一个基于Django + Vue的Web应用，提供抖音链接分析和AI动作指导功能。

## 功能特性

1. **抖音链接分析**
   - 输入抖音视频或图文链接
   - 自动提取视频/图文信息
   - 显示标题、描述、视频ID等详细信息

2. **AI动作指导**
   - 实时摄像头调用
   - 使用MediaPipe进行姿态检测
   - AI实时分析用户动作
   - 提供个性化的动作指导反馈

3. **3D肌肉群可视化**
   - 交互式3D人体模型
   - 鼠标悬停查看肌肉详细信息
   - 支持旋转、缩放、平移操作
   - 显示肌肉名称、分类、描述和训练动作

## 技术栈

### 后端
- Django 4.2.7
- Django REST Framework
- MediaPipe (姿态检测)
- OpenCV (图像处理)
- BeautifulSoup4 (网页解析)

### 前端
- Vue 3
- Vite
- Axios
- Vue Router
- Three.js (3D可视化)
- Tailwind CSS (样式)

## 项目结构

```
WorkOut/
├── backend/                 # Django后端
│   ├── workout_app/        # Django项目配置
│   ├── api/                # API应用
│   │   ├── views.py        # API视图
│   │   └── urls.py         # URL路由
│   ├── manage.py
│   └── requirements.txt
├── frontend/               # Vue前端
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   │   ├── DouyinAnalyzer.vue
│   │   │   └── PoseAnalyzer.vue
│   │   ├── router/         # 路由配置
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 安装和运行

### 后端设置

1. 进入后端目录：
```bash
cd backend
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 运行数据库迁移：
```bash
python manage.py migrate
```

5. 启动Django开发服务器：
```bash
python manage.py runserver
```

后端将在 `http://localhost:8000` 运行

### 前端设置

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

前端将在 `http://localhost:5173` 运行

## API端点

### 1. 分析抖音链接
- **URL**: `/api/analyze-douyin/`
- **方法**: POST
- **请求体**:
```json
{
  "url": "https://www.douyin.com/video/..."
}
```
- **响应**:
```json
{
  "success": true,
  "data": {
    "video_id": "123456789",
    "title": "视频标题",
    "description": "视频描述",
    "type": "video",
    "video_url": "...",
    "image_url": "...",
    "original_url": "..."
  }
}
```

### 2. 分析动作姿态
- **URL**: `/api/analyze-pose/`
- **方法**: POST
- **请求体**:
```json
{
  "image": "data:image/jpeg;base64,..."
}
```
- **响应**:
```json
{
  "success": true,
  "data": {
    "feedback": [
      {
        "type": "warning",
        "message": "左臂可以更伸直一些",
        "body_part": "left_arm"
      }
    ],
    "annotated_image": "data:image/jpeg;base64,...",
    "landmarks_detected": true
  }
}
```

## 使用说明

### 抖音链接分析

1. 在首页输入抖音视频或图文链接
2. 点击"分析链接"按钮
3. 查看分析结果，包括类型、标题、描述等信息

### AI动作指导

1. 点击"动作指导"标签页
2. 点击"启动摄像头"按钮，允许浏览器访问摄像头
3. 调整姿势，点击"分析当前动作"按钮
4. 查看AI提供的动作指导反馈
5. 根据反馈调整动作，重复分析直到满意

### 3D肌肉群可视化

1. 点击"3D肌肉图"标签页
2. 使用鼠标左键拖动旋转模型
3. 使用鼠标滚轮缩放
4. 将鼠标悬停在肌肉上查看详细信息
5. 左侧面板显示选中肌肉的详细信息和训练动作

## 注意事项

1. **摄像头权限**: 使用动作指导功能需要授予浏览器摄像头访问权限
2. **抖音链接**: 由于抖音的反爬虫机制，某些链接可能无法完全解析
3. **网络要求**: 确保后端服务正常运行，前端才能正常调用API
4. **浏览器兼容性**: 建议使用Chrome、Edge等现代浏览器

## 开发说明

### 后端开发
- 主要逻辑在 `backend/api/views.py`
- 可以扩展更多的姿态分析算法
- 可以添加更多的动作指导规则

### 前端开发
- 页面组件在 `frontend/src/views/`
- 可以自定义UI样式和交互
- 可以添加更多功能页面

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

