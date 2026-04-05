import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="시봉 레코즈 전용 스크립트 추출기 v6", layout="wide")

st.title("🎬 시봉 레코즈 전용 스크립트 추출기 v6")

# --- 입력 창 ---
url_input = st.text_input("유튜브 URL을 입력하세요:", "https://www.youtube.com/watch?v=TyElNayCFQ4")

col1, col2 = st.columns(2)
with col1:
    include_title_url = st.checkbox("제목과 주소 포함", value=True)
with col2:
    include_timestamp = st.checkbox("타임스탬프 포함", value=True)

st.markdown("---")

# --- 실행 버튼 ---
if st.button("스크립트 따오기! 🚀"):
    if not url_input:
        st.warning("URL을 입력해주세요.")
    else:
        try:
            # 1. 유튜브 URL에서 비디오 ID만 깔끔하게 빼내기
            parsed_url = urlparse(url_input)
            video_id = ""
            
            if parsed_url.hostname == 'youtu.be':
                video_id = parsed_url.path[1:]
            elif parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
                if parsed_url.path == '/watch':
                    video_id = parse_qs(parsed_url.query)['v'][0]
                elif parsed_url.path.startswith('/embed/'):
                    video_id = parsed_url.path.split('/')[2]
                elif parsed_url.path.startswith('/v/'):
                    video_id = parsed_url.path.split('/')[2]
                    
            if not video_id:
                st.error("올바른 유튜브 URL이 아닙니다. 다시 확인해주세요.")
            else:
                # 2. 자막 추출 (에러 안 나는 최신/가장 안전한 방식)
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
                
                # 3. 텍스트 예쁘게 조립하기
                result_text = ""
                if include_title_url:
                    result_text += f"영상 주소: {url_input}\n\n"
                    
                for item in transcript:
                    text = item['text']
                    if include_timestamp:
                        start_time = int(item['start'])
                        minutes = start_time // 60
                        seconds = start_time % 60
                        result_text += f"[{minutes:02d}:{seconds:02d}] {text}\n"
                    else:
                        result_text += f"{text}\n"
                        
                # 4. 화면에 출력
                st.success("스크립트 추출 완료! 🎉")
                st.text_area("추출된 스크립트", result_text, height=500)
                
        except Exception as e:
            # 에러 발생 시 빨간 창 띄우기 (기존 스샷과 동일하게)
            st.error(f"오류 발생: {e}\n\n(참고: 자막 기능이 아예 막힌 영상일 수 있습니다.)")
