import cv2
import os
import base64
import json
import tempfile
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
        api_key = os.getenv("OPENROUTER_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.system_prompt = """你是一位专业的健身教练。请分析视频，提取其中演示的所有健身动作，并将其转化为结构化的训练计划。

### 约束条件：
1. 识别视频中出现的每一个独立动作。
2. 为每个动作设置一个建议的训练组数（total）。
3. 提取 3 条核心动作要领（tips），用分号“；”分隔。

### 输出格式：
必须严格返回以下 JSON 数组格式，不要包含任何 markdown 标签或额外解释：

[
  {
    "id": 101,
    "name": "动作名称",
    "current": 0,
    "total": 5,
    "tips": "要点1；要点2；要点3"
  }
]"""

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
            response = self.client.chat.completions.create(
                model="google/gemini-3-flash-preview",
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
                timeout=120
            )
            
            ai_content = response.choices[0].message.content
            workout_data = json.loads(ai_content)
            
            if isinstance(workout_data, dict) and "exercises" in workout_data:
                workout_data = workout_data["exercises"]
            
            return workout_data

        finally:
            if os.path.exists(optimized_video_path):
                os.remove(optimized_video_path)

