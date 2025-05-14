文件名：app.py
代码：将之前后端代码的功能整合到Streamlit应用中。以下是一个示例：
import streamlit as st
import os
import whisper
import subprocess
from werkzeug.utils import secure_filename

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def transcribe_video(filepath):
    try:
        # 提取音频
        audio_path = os.path.join(UPLOAD_FOLDER, 'temp_audio.wav')
        subprocess.run([
            'ffmpeg', '-i', filepath, '-vn', '-acodec', 'pcm_s16le',
            '-ar', '16000', '-ac', '1', '-y', audio_path
        ], check=True)

        # 加载Whisper模型
        model = whisper.load_model("base")

        # 转录音频
        result = model.transcribe(audio_path)
        transcript = result['text']

        # 保存转录结果
        transcript_filename = os.path.splitext(os.path.basename(filepath))[0] + '_转录.txt'
        transcript_path = os.path.join(UPLOAD_FOLDER, transcript_filename)
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(transcript)

        # 清理临时音频文件
        if os.path.exists(audio_path):
            os.remove(audio_path)

        return transcript, transcript_path
    except Exception as e:
        st.error(f'转录失败: {str(e)}')
        return None, None

def process_transcript(transcript, instructions):
    if not transcript:
        st.error('没有转录文本')
        return None, None
    try:
        # 这里可以根据用户指令处理文本
        processed_text = transcript
        if instructions == 'summary':
            # 简单总结逻辑
            sentences = transcript.split('.')
            processed_text = '. '.join(sentences[:3]) + '.'
        elif instructions == 'bullet_points':
            # 转换为要点
            sentences = transcript.split('.')
            processed_text = '\n'.join([f'- {s.strip()}' for s in sentences if s.strip()])

        # 保存处理后的文本
        processed_filename = '处理后的文本.txt'
        processed_path = os.path.join(UPLOAD_FOLDER, processed_filename)
        with open(processed_path, 'w', encoding='utf-8') as f:
            f.write(processed_text)

        return processed_text, processed_path
    except Exception as e:
        st.error(f'处理失败: {str(e)}')
        return None, None

st.title('视频转文字工具')

# 上传视频
uploaded_file = st.file_uploader("上传视频", type=list(ALLOWED_EXTENSIONS))

if uploaded_file is not None:
    if allowed_file(uploaded_file.name):
        filename = secure_filename(uploaded_file.name)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        st.success('文件上传成功')

        # 转录视频
        if st.button('开始转录'):
            transcript, transcript_path = transcribe_video(filepath)
            if transcript:
                st.text_area('转录文本', transcript)
                st.download_button('下载转录文本', open(transcript_path, 'rb').read(), file_name=os.path.basename(transcript_path))

                # 处理文本
                process_option = st.radio('整理内容', ['原始文本', '摘要', '要点'])
                if st.button('处理文本'):
                    if process_option == '原始文本':
                        instructions = 'original'
                    elif process_option == '摘要':
                        instructions = 'summary'
                    elif process_option == '要点':
                        instructions = 'bullet_points'
                    processed_text, processed_path = process_transcript(transcript, instructions)
                    if processed_text:
                        st.text_area('处理后的文本', processed_text)
                        st.download_button('下载处理后的文本', open(processed_path, 'rb').read(), file_name=os.path.basename(processed_path))
    else:
        st.error('文件类型不支持')