import cv2
import os
import base64
import json
import tempfile
import time
from openai import OpenAI
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    from moviepy import VideoFileClip
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()

class VideoAnalyzer:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        # 综合参考用户提供的 prompt.txt 和系统需求
        self.system_prompt = """你是一位专业的健身教练。请分析视频，提取其中演示的所有健身动作，并将其转化为结构化的训练计划。

### 约束条件：
1. **计划名称**：根据视频内容，为整个训练计划起一个简短有力、富有激励性的名称 (title)。
2. 识别视频中出现的每一个独立动作。
3. 为每个动作设置一个建议的训练组数 (total_sets) 和每组次数 (reps_per_set)。
4. 提取 3 条核心动作要领 (tips)，用分号“；”分隔。
5. **关键任务**：准确记录该动作在视频中的开始时间 (start_time) 和结束时间 (end_time)，格式为 "mm:ss"。
6. 计算该动作开始时刻距离视频开头的总秒数 (seconds)。

### 输出格式：
必须严格返回包含 "title" 和 "exercises" 键的 JSON 对象。格式如下：

{
  "title": "训练计划名称",
  "exercises": [
    {
      "id": 101,
      "name": "动作名称",
      "current_sets": 0,
      "total_sets": 5,
      "reps_per_set": 12,
      "tips": "要点1；要点2；要点3",
      "start_time": "00:15",
      "end_time": "00:45",
      "seconds": 15
    }
  ]
}"""

    def compress_video(self, input_path, output_path, target_fps=1, target_width=320):
        temp_video = tempfile.mktemp(suffix=".mp4")
        
        # --- Step 1: Process video frames using OpenCV ---
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise Exception("Could not open video file")

        original_fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        ratio = target_width / width
        target_height = int(height * ratio)
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video, fourcc, target_fps, (target_width, target_height))

        frame_count = 0
        skip_interval = max(1, int(original_fps / target_fps))

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_count % skip_interval == 0:
                    resized_frame = cv2.resize(frame, (target_width, target_height))
                    out.write(resized_frame)
                frame_count += 1
        finally:
            cap.release()
            out.release()

        # --- Step 2: Synthesize audio using MoviePy ---
        video_clip = None
        original_clip = None
        try:
            video_clip = VideoFileClip(temp_video)
            original_clip = VideoFileClip(input_path)
            
            if original_clip.audio:
                # Compatibility for MoviePy v1 and v2
                if hasattr(video_clip, 'with_audio'):
                    final_clip = video_clip.with_audio(original_clip.audio)
                    # MoviePy v2 removed verbose and logger from write_videofile
                    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
                else:
                    final_clip = video_clip.set_audio(original_clip.audio)
                    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
            else:
                if hasattr(video_clip, 'with_audio'):
                    video_clip.write_videofile(output_path, codec="libx264")
                else:
                    video_clip.write_videofile(output_path, codec="libx264", verbose=False, logger=None)
            
        except Exception as e:
            # Fallback to just the compressed video if audio processing fails
            import traceback
            traceback.print_exc()
            print(f"Audio processing failed, using silent video: {e}")
            # Close clips before renaming to avoid PermissionError on Windows
            if video_clip: video_clip.close()
            if original_clip: original_clip.close()
            video_clip = None
            original_clip = None
            
            import shutil
            shutil.copy2(temp_video, output_path)
        finally:
            if video_clip:
                video_clip.close()
            if original_clip:
                original_clip.close()
            
            # Small delay to ensure Windows releases the file handle
            import time
            time.sleep(0.1)
            if os.path.exists(temp_video):
                try:
                    os.remove(temp_video)
                except Exception as e:
                    print(f"Warning: Could not remove temp file {temp_video}: {e}")

    def analyze_video(self, input_video_path):
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as optimized_video_file:
            optimized_video_path = optimized_video_file.name

        try:
            # 1. Compress video
            self.compress_video(input_video_path, optimized_video_path)

            # 2. Convert to Base64
            with open(optimized_video_path, "rb") as f:
                video_b64 = base64.b64encode(f.read()).decode('utf-8')

            # 3. Call OpenRouter
            # 使用 google/gemini-2.0-flash-001，这是一个更稳定且支持视频的版本
            # 如果依然报错 404，可能是 OpenRouter 某些节点对 base64 视频支持不稳定
            try:
                response = self.client.chat.completions.create(
                    model="google/gemini-2.0-flash-001",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": self.system_prompt},
                                {
                                    "type": "video_url",
                                    "video_url": {"url": f"data:video/mp4;base64,{video_b64}"}
                                }
                            ]
                        }
                    ],
                    response_format={"type": "json_object"},
                    timeout=180
                )
            except Exception as e:
                if "404" in str(e) or "No endpoints found" in str(e):
                    print("尝试使用备用模型或格式...")
                    # 尝试使用 Gemini 1.5 Flash 或更改类型为 image_url (有时 OpenRouter 这样处理)
                    response = self.client.chat.completions.create(
                        model="google/gemini-flash-1.5",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": self.system_prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": f"data:video/mp4;base64,{video_b64}"}
                                    }
                                ]
                            }
                        ],
                        response_format={"type": "json_object"},
                        timeout=180
                    )
                else:
                    raise e
            
            ai_content = response.choices[0].message.content.strip()
            
            # 如果 ai_content 为空，抛出异常
            if not ai_content:
                raise Exception("AI 返回内容为空")
                
            ai_data = json.loads(ai_content)
            
            # 提取标题
            plan_title = ai_data.get("title", f"训练计划 {time.strftime('%Y-%m-%d')}")
            
            # 提取动作列表
            workout_data = []
            if isinstance(ai_data, dict):
                if "exercises" in ai_data:
                    workout_data = ai_data["exercises"]
                elif "data" in ai_data:
                    workout_data = ai_data["data"]
                else:
                    # 如果字典中没有明显的数组键，且字典本身看起来像一个动作
                    if "name" in ai_data:
                        workout_data = [ai_data]
                    else:
                        # 尝试寻找任何列表类型的字段
                        for val in ai_data.values():
                            if isinstance(val, list):
                                workout_data = val
                                break
            
            # 确保返回的是数组格式
            if not isinstance(workout_data, list):
                workout_data = []
            
            # 验证并补全字段
            for idx, exercise in enumerate(workout_data):
                if not isinstance(exercise, dict):
                    continue
                # 确保有id字段
                if "id" not in exercise:
                    exercise["id"] = 100 + idx + 1
                # 映射字段（如果 AI 使用了 prompt.txt 中的字段名）
                if "current" in exercise and "current_sets" not in exercise:
                    exercise["current_sets"] = exercise["current"]
                if "total" in exercise and "total_sets" not in exercise:
                    exercise["total_sets"] = exercise["total"]
                
                # 设置默认值
                exercise.setdefault("current_sets", 0)
                exercise.setdefault("total_sets", 5)
                exercise.setdefault("reps_per_set", 12)
                exercise.setdefault("tips", "")
                exercise.setdefault("start_time", "00:00")
                exercise.setdefault("end_time", "00:00")
                
                # 确保 seconds 字段存在且正确
                if "seconds" not in exercise or exercise["seconds"] == 0:
                    try:
                        time_parts = exercise["start_time"].split(":")
                        if len(time_parts) == 2:
                            exercise["seconds"] = int(time_parts[0]) * 60 + int(time_parts[1])
                        else:
                            exercise["seconds"] = 0
                    except:
                        exercise["seconds"] = 0
            
            return {
                "title": plan_title,
                "exercises": workout_data
            }

        finally:
            if os.path.exists(optimized_video_path):
                os.remove(optimized_video_path)

