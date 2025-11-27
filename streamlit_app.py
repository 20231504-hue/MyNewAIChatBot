import os
from typing import List, Dict

import requests
import streamlit as st

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
SYSTEM_PROMPT = (
    "너는 대한민국 초등학교에서 사회(역사) 영역을 가르치는 친절한 선생님이에요. "
    "대한민국 역사 교육과정과 직접적으로 관련된 질문에만 답변하고, 다른 주제는 정중히 거절해야 해요. "
    "대답할 때는 쉬운 말로 부드럽게 설명하고, 학생을 칭찬하며 격려해주세요. "
    "항상 공신력 있는 자료(예: 국사편찬위원회, 교육부, 정부/공공기관 발행 자료, 검증된 교과서)에서 확인된 정보만 사용하고, "
    "출처가 불분명한 위키나 블로그 등의 정보는 절대 활용하지 마세요. "
    "가능하다면 대한민국의 역사적 사실과 문화적 맥락을 예시로 들어 주세요. "
    "모든 문장에는 상황에 맞는 이모지를 자연스럽게 포함해 주세요."
)


def _convert_messages_for_api(messages: List[Dict[str, str]]):
    contents = [
        {
            "role": "user",
            "parts": [{"text": SYSTEM_PROMPT}],
        }
    ]

    for msg in messages:
        if msg.get("internal"):
            continue
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": msg["text"]}]})

    return contents


def call_gemini(api_key: str, messages: List[Dict[str, str]]) -> str:
    payload = {"contents": _convert_messages_for_api(messages)}

    response = requests.post(
        f"{ENDPOINT}?key={api_key}",
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    return (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "응답을 이해하지 못했습니다.")
    )


def main() -> None:
    st.set_page_config(
        page_title="Hello Vibe Coding - Gemini Chatbot",
        page_icon="✨",
        layout="wide",
    )
    st.title("Hello Vibe Coding")
    st.caption("Gemini 1.5 Flash 모델과 대화해 보세요.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "text": "안녕하세요! Google API Key를 입력한 뒤 질문을 보내보세요. 😊",
                "internal": True,
            }
        ]

    with st.sidebar:
        st.header("설정")
        api_key = st.text_input(
            "Google API Key",
            value=os.getenv("GOOGLE_API_KEY", ""),
            type="password",
            help="브라우저/세션에만 저장되며 서버에 보관되지 않습니다.",
        )
        st.markdown(
            "[API 키 발급 안내](https://makersuite.google.com/app/apikey)"
        )

    st.subheader("대화")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["text"])

    prompt = st.chat_input("무엇이 궁금한가요?")

    if prompt:
        if not api_key:
            st.warning("먼저 Google API Key를 입력하세요.")
            return

        st.session_state.messages.append({"role": "user", "text": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner("Gemini에 요청 중..."):
            try:
                answer = call_gemini(api_key, st.session_state.messages)
            except requests.HTTPError as http_err:
                answer = f"HTTP 오류가 발생했습니다: {http_err}"
            except requests.RequestException as req_err:
                answer = f"요청 실패: {req_err}"
            except Exception as err:
                answer = f"예상치 못한 오류: {err}"

        st.session_state.messages.append({"role": "assistant", "text": answer})
        with st.chat_message("assistant"):
            st.write(answer)


if __name__ == "__main__":
    main()

