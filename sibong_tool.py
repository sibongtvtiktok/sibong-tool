import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import requests

st.set_page_config(page_title="시봉 레코즈 전용 스크립트 추출기 v5", layout="wide")

# 제목 가져오기 함수 (안전하게 수정)
def get_video_info(url):
    try:
        response = requests.get(f"https://www.youtube.com/oembed?url={url}&format=json")
        if response.status_code == 200:
            return response.json().get('title', '제목 없음')
        return "제목을 불러올 수 없음"
    except:
        return "제목을 불러올 수 없음"

# 시간 포맷 변환 [00:00]
def format_time(s):
    mins = int(s // 60)
    secs = int(s % 60)
    return f"[{mins:02d}:{secs:02d}]"

st.title("🎬 시봉 레코즈 전용 스크립트 추출기 v5")
st.write("---")

# 1. 입력 섹션
url = st.text_input("유튜브 URL을 입력하세요:", placeholder="https://www.youtube.com/watch?v=...")

col_opt1, col_opt2, _ = st.columns([1, 1, 2])
with col_opt1:
    include_info = st.checkbox("제목과 주소 포함", value=True)
with col_opt2:
    include_timestamps = st.checkbox("타임스탬프 포함", value=True)

# 2. 실행 섹션
if st.button("스크립트 따오기! 🚀", use_container_width=True):
    if url:
        try:
            # 비디오 ID 추출
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                video_id = url.split("youtu.be/")[1].split("?")[0]
            else:
                video_id = url.split("/")[-1]

            with st.spinner('데이터 추출 중... 잠시만요!'):
                # 제목 가져오기
                title = get_video_info(url)
                
                # 자막 가져오기 (가장 안정적인 get_transcript 사용)
                # 한국어(ko) 먼저 시도하고, 없으면 영어(en)로 가져옵니다.
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
                except:
                    # 자동 생성된 자막이라도 가져오기 위해 다시 시도
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    transcript = transcript_list.find_transcript(['ko', 'en']).fetch()

                # 텍스트 조립
                final_output = ""
                if include_info:
                    final_output += f"제목: {title}\n"
                    final_output += f"주소: {url}\n\n"
                
                if include_timestamps:
                    content = "\n".join([f"{format_time(t['start'])} {t['text']}" for t in transcript])
                else:
                    content = " ".join([t['text'] for t in transcript])
                
                final_output += content

                st.success("추출 완료!")
                st.subheader("📋 결과 리포트")
                st.code(final_output, language="text")
                
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}\n\n팁: 자막(CC)이 아예 비활성화된 영상일 수 있습니다.")
    else:
        st.warning("유튜브 주소를 먼저 입력해 주세요!")
