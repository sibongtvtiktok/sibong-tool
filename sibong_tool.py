import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import requests

st.set_page_config(page_title="시봉 레코즈 전용 스크립트 추출기 v4", layout="wide")

def get_video_info(url):
    try:
        response = requests.get(f"https://www.youtube.com/oembed?url={url}&format=json")
        data = response.json()
        return data['title']
    except:
        return "제목을 불러올 수 없음"

def format_time(s):
    td_mins = int(s // 60)
    td_secs = int(s % 60)
    return f"[{td_mins:02d}:{td_secs:02d}]"

st.title("🎬 시봉 레코즈 전용 스크립트 추출기 v4")
st.write("---")

# 1. 주소 입력창
url = st.text_input("유튜브 URL을 입력하세요:", placeholder="https://www.youtube.com/watch?v=...")

# 2. 주소창 바로 밑에 옵션 배치 (한 줄에 나란히)
col_opt1, col_opt2, _ = st.columns([1, 1, 2])
with col_opt1:
    include_info = st.checkbox("제목과 주소 포함", value=True)
with col_opt2:
    include_timestamps = st.checkbox("타임스탬프 포함", value=True)

st.write("") # 간격 조절

# 3. 추출 버튼
if st.button("스크립트 따오기! 🚀", use_container_width=True):
    if url:
        try:
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            else:
                video_id = url.split("/")[-1]

            with st.spinner('데이터 추출 중...'):
                # 제목 가져오기
                title = get_video_info(url)
                
                # 자막 가져오기
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                transcript = transcript_list.find_transcript(['en', 'ko']).fetch()

                # 텍스트 조립 logic
                final_output = ""
                
                # 상단 정보 추가 여부
                if include_info:
                    final_output += f"제목: {title}\n"
                    final_output += f"주소: {url}\n\n"
                
                # 타임스탬프 유무에 따른 본문 조립
                if include_timestamps:
                    # [00:00] 내용 형식
                    content = "\n".join([f"{format_time(t['start'])} {t['text']}" for t in transcript])
                else:
                    # 내용만 쭉 이어지는 형식
                    content = " ".join([t['text'] for t in transcript])
                
                final_output += content

                st.success("추출 완료!")
                
                # 4. 결과 출력
                st.subheader("📋 결과 리포트")
                st.caption("오른쪽 상단 아이콘을 누르면 바로 복사됩니다.")
                st.code(final_output, language="text")
                
        except Exception as e:
            st.error(f"오류 발생: {e}")
    else:
        st.warning("유튜브 주소를 먼저 입력해 주세요!")