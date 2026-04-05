import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import requests

st.set_page_config(page_title="시봉 레코즈 전용 스크립트 추출기 v6", layout="wide")

def get_video_info(url):
    try:
        response = requests.get(f"https://www.youtube.com/oembed?url={url}&format=json")
        return response.json().get('title', '제목 없음')
    except:
        return "제목 없음"

def format_time(s):
    mins = int(s // 60)
    secs = int(s % 60)
    return f"[{mins:02d}:{secs:02d}]"

st.title("🎬 시봉 레코즈 전용 스크립트 추출기 v6")
st.write("---")

url = st.text_input("유튜브 URL을 입력하세요:", placeholder="https://www.youtube.com/watch?v=...")

col_opt1, col_opt2, _ = st.columns([1, 1, 2])
with col_opt1:
    include_info = st.checkbox("제목과 주소 포함", value=True)
with col_opt2:
    include_timestamps = st.checkbox("타임스탬프 포함", value=True)

if st.button("스크립트 따오기! 🚀", use_container_width=True):
    if url:
        try:
            # 1. ID 추출 로직 강화
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                video_id = url.split("youtu.be/")[1].split("?")[0]
            else:
                video_id = url.split("/")[-1]

            with st.spinner('데이터 추출 중...'):
                # 2. 제목 가져오기
                title = get_video_info(url)
                
                # 3. 자막 가져오기 (가장 확실한 명령어로 변경)
                # 한국어 시도 -> 안되면 영어 시도 -> 안되면 그냥 되는대로 가져오기
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
                except:
                    # 모든 자막 목록을 가져와서 첫 번째 것을 무조건 선택
                    # 이 부분이 list_transcripts 에러를 피하는 핵심입니다.
                    from youtube_transcript_api import YouTubeTranscriptApi as yta
                    all_transcripts = yta.list_transcripts(video_id)
                    transcript = all_transcripts.find_transcript(['ko', 'en']).fetch()

                # 4. 결과물 조립
                final_output = ""
                if include_info:
                    final_output += f"제목: {title}\n주소: {url}\n\n"
                
                if include_timestamps:
                    content = "\n".join([f"{format_time(t['start'])} {t['text']}" for t in transcript])
                else:
                    content = " ".join([t['text'] for t in transcript])
                
                final_output += content

                st.success("추출 완료!")
                st.code(final_output, language="text")
                
        except Exception as e:
            st.error(f"오류 발생: {e}\n\n(참고: 자막 기능이 아예 막힌 영상일 수 있습니다.)")
    else:
        st.warning("주소를 입력해 주세요!")
