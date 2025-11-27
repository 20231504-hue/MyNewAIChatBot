import os
from typing import Optional

import requests
import streamlit as st

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


def call_gemini(api_key: str, prompt: str) -> str:
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ]
    }

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
            {"role": "assistant", "text": "안녕하세요! Google API Key를 입력한 뒤 질문을 보내보세요."}
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
                answer = call_gemini(api_key, prompt)
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

