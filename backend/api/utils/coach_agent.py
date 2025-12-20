import os
import base64
import json
import tempfile
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class CoachAgent:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.coach_prompt_template = """你是一位严厉且专业的私人健身教练。我会为你提供某个动作的【标准要领】以及我【实际练习的视频】。

### 判分标准（基于以下要领）：
{action_tips}

### 你的任务：
1. **动作对齐**：判断视频中的动作是否就是"{action_name}"。
2. **标准度审计**：严格对照【标准要领】，观察我的肢体关节位置、背部曲线、运动轨迹等。
3. **发现问题**：如果动作不标准，请指出具体的错误部位（如：腰部塌陷、膝盖内扣等）。
4. **改进建议**：给出 1-2 条易于执行的改进指令。

### 输出格式（严格 JSON）：
{{
  "is_standard": false,
  "score": 85,
  "detected_errors": ["错误1", "错误2"],
  "improvement_advice": "请在下一次练习时，尝试...",
  "coach_comment": "整体不错，但后半程核心有些松懈。"
}}"""

    def analyze_form(self, video_path, action_name, action_tips):
        """
        分析用户的训练视频，给出评价和反馈
        
        Args:
            video_path: 训练视频路径
            action_name: 动作名称
            action_tips: 动作要领（用分号分隔的字符串）
        
        Returns:
            dict: 包含评分、错误、建议等的反馈字典
        """
        try:
            # 1. 准备prompt
            final_prompt = self.coach_prompt_template.format(
                action_name=action_name,
                action_tips=action_tips
            )

            # 2. 压缩视频（如果需要）
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
                temp_video_path = temp_video.name
            
            try:
                # 简单处理：如果视频太大，可以考虑压缩
                # 这里先直接使用原视频，如果API报错再考虑压缩
                video_to_use = video_path
                
                # 3. 视频转Base64
                with open(video_to_use, "rb") as f:
                    video_b64 = base64.b64encode(f.read()).decode('utf-8')

                # 4. 调用OpenRouter API
                response = self.client.chat.completions.create(
                    model="google/gemini-3-flash-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": final_prompt},
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
                
                # 5. 解析返回结果
                raw_content = response.choices[0].message.content.strip()
                
                # 移除可能的markdown代码块标记
                if raw_content.startswith("```json"):
                    raw_content = raw_content[7:]
                if raw_content.startswith("```"):
                    raw_content = raw_content[3:]
                if raw_content.endswith("```"):
                    raw_content = raw_content[:-3]
                raw_content = raw_content.strip()
                
                parsed_result = json.loads(raw_content)
                
                # 如果返回的是列表，取第一个元素
                if isinstance(parsed_result, list):
                    if len(parsed_result) > 0:
                        final_analysis = parsed_result[0]
                    else:
                        final_analysis = {
                            "is_standard": False,
                            "score": 0,
                            "detected_errors": ["AI返回了空列表"],
                            "improvement_advice": "请重新录制视频",
                            "coach_comment": "无法分析视频内容"
                        }
                else:
                    final_analysis = parsed_result
                
                # 确保所有必需字段都存在
                if "is_standard" not in final_analysis:
                    final_analysis["is_standard"] = False
                if "score" not in final_analysis:
                    final_analysis["score"] = 0
                if "detected_errors" not in final_analysis:
                    final_analysis["detected_errors"] = []
                if "improvement_advice" not in final_analysis:
                    final_analysis["improvement_advice"] = "请继续练习"
                if "coach_comment" not in final_analysis:
                    final_analysis["coach_comment"] = "动作需要改进"
                
                return final_analysis
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_video_path) and temp_video_path != video_path:
                    try:
                        os.remove(temp_video_path)
                    except Exception as e:
                        print(f"Warning: Could not remove temp file {temp_video_path}: {e}")
                        
        except Exception as e:
            import traceback
            traceback.print_exc()
            # 返回错误反馈
            return {
                "is_standard": False,
                "score": 0,
                "detected_errors": [f"分析失败: {str(e)}"],
                "improvement_advice": "请检查视频格式或重新录制",
                "coach_comment": "无法完成视频分析，请稍后重试"
            }
