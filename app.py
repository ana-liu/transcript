import streamlit as st
import re
import time
import json
import pandas as pd

# ==========================================
# 1. 页面基本配置
# ==========================================
st.set_page_config(
    page_title="访谈音频转写与整理工具",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ 访谈音频转写与整理工具")
st.caption("支持音频上传、说话人识别、语气词自动过滤与结果导出")

# ==========================================
# 2. 工具函数定义
# ==========================================
def clean_filler_words(text: str) -> str:
    """
    过滤常见的中文语气词与停顿词
    """
    if not text:
        return ""
    # 匹配常见的语气词模式
    pattern = r'(嗯+|啊+|呃+|那个+|这个+|就是说?|嗯嗯|哈+)'
    cleaned = re.sub(pattern, '', text)
    # 清理连续的标点或多余空格
    cleaned = re.sub(r'([，。？！,?!])\1+', r'\1', cleaned)
    cleaned = re.sub(r'^\s*[,，。？！]\s*', '', cleaned)
    return cleaned.strip()

def mock_audio_transcription(file_name):
    """
    模拟调用 API 返回转写结果（含说话人分离）
    实际开发时替换为：阿里云/腾讯云/API 的真实调用
    """
    time.sleep(2)  # 模拟网络延时
    return [
        {"speaker": "访谈员 (Speaker 0)", "start_time": "00:00:02", "text": "嗯……今天非常感谢您接受我们的访谈，这个，我们先聊聊项目的整体进展吧。"},
        {"speaker": "受访者 A (Speaker 1)", "start_time": "00:00:08", "text": "好的，那个……我们目前第一阶段已经完成了，总体的进度还算符合预期吧。"},
        {"speaker": "受访者 B (Speaker 2)", "start_time": "00:00:18", "text": "对对，呃，关于数据收集那块，就是说，我们已经拿到了基本的数据集。"},
        {"speaker": "访谈员 (Speaker 0)", "start_time": "00:00:27", "text": "明白，那在这个过程中，有没有遇到什么特别大的挑战呢？"},
        {"speaker": "受访者 A (Speaker 1)", "start_time": "00:00:35", "text": "那个，主要还是人力资源的调配问题，嗯，初期协调起来稍微有点吃力。"}
    ]

# ==========================================
# 3. 侧边栏配置
# ==========================================
with st.sidebar:
    st.header("⚙️ 参数与设置")
    
    # 选项：是否开启语气词过滤
    enable_filter = st.checkbox("自动过滤无意义语气词", value=True, help="过滤 '嗯、啊、这个、那个' 等停顿词")
    
    # 说话人重命名设置
    st.subheader("👥 说话人重命名")
    speaker_0_name = st.text_input("Speaker 0 标签", value="访谈员")
    speaker_1_name = st.text_input("Speaker 1 标签", value="受访者 A")
    speaker_2_name = st.text_input("Speaker 2 标签", value="受访者 B")
    
    speaker_map = {
        "访谈员 (Speaker 0)": f"{speaker_0_name} (Speaker 0)",
        "受访者 A (Speaker 1)": f"{speaker_1_name} (Speaker 1)",
        "受访者 B (Speaker 2)": f"{speaker_2_name} (Speaker 2)",
    }

# ==========================================
# 4. 主界面：文件上传与处理
# ==========================================
uploaded_file = st.file_uploader("上传访谈音频文件 (支持 mp3, wav, m4a)", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/mp3")
    
    # 触发转写按钮
    if st.button("开始转写与文本整理", type="primary"):
        with st.spinner("正在上传音频并调用 API 转写中（含说话人识别）..."):
            # 调用转写逻辑（替换为真实 API 逻辑）
            raw_data = mock_audio_transcription(uploaded_file.name)
            st.session_state['transcription_result'] = raw_data
            st.success("转写完成！")

# ==========================================
# 5. 结果展示与导出
# ==========================================
if 'transcription_result' in st.session_state:
    data = st.session_state['transcription_result']
    
    st.divider()
    st.subheader("📄 转写结果预览")
    
    # 整理显示文本
    processed_results = []
    
    for item in data:
        # 映射说话人名称
        speaker = speaker_map.get(item["speaker"], item["speaker"])
        # 处理文本（根据勾选状态决定是否过滤语气词）
        raw_text = item["text"]
        display_text = clean_filler_words(raw_text) if enable_filter else raw_text
        
        processed_results.append({
            "speaker": speaker,
            "time": item["start_time"],
            "text": display_text
        })
        
        # 对话卡片展示
        with st.chat_message("user" if "访谈员" in speaker else "assistant"):
            st.markdown(f"**[{item['start_time']}] {speaker}**")
            st.write(display_text)
            
    st.divider()
    
    # 导出功能
    st.subheader("💾 导出整理结果")
    col1, col2 = st.columns(2)
    
    # 生成 TXT 内容
    txt_content = ""
    for r in processed_results:
        txt_content += f"[{r['time']}] {r['speaker']}:\n{r['text']}\n\n"
        
    with col1:
        st.download_button(
            label="📥 导出为 TXT 文本",
            data=txt_content,
            file_name=f"{uploaded_file.name.split('.')[0]}_转写文本.txt",
            mime="text/plain"
        )
        
    # 生成 JSON 内容
    json_content = json.dumps(processed_results, ensure_ascii=False, indent=2)
    with col2:
        st.download_button(
            label="📥 导出为 JSON 数据",
            data=json_content,
            file_name=f"{uploaded_file.name.split('.')[0]}_转写数据.json",
            mime="application/json"
        )
