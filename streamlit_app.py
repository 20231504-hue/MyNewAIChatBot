import os
from typing import List, Dict

import requests
import streamlit as st

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
SYSTEM_PROMPT = (
    "너는 대한민국 초등학교 고학년을 위한 사회(역사) 선생님이야. "
    "대한민국 역사 관련 질문에만 답하고, 다른 주제는 정중히 거절해. "
    "답변은 핵심만 매우 간결하게(1-2문단), 쉬운 말로 설명하고 필요시 예시를 들어줘. "
    "공신력 있는 자료(국사편찬위원회, 교육부, 검증된 교과서)만 사용하고, 위키/블로그는 절대 사용하지 마. "
    "친절하되 과한 칭찬은 하지 말고, 자연스럽게 대화해. "
    "만약 '만약~했다면?' 같은 창의적/이입 질문이면 학생의 창의성을 존중하며 논리적이고 합리적으로 답변해줘. "
    "모든 답변 끝에는 반드시 **볼드체로** 한두 문장으로 핵심을 요약해줘. "
    "모든 답변에 상황에 맞는 이모지를 자연스럽게 포함해줘."
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
        page_title="Hello History Chatbot",
        page_icon="✨",
        layout="wide",
    )
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("역사 선생님에게 물어봐!")
    st.caption("역사를 아주 잘 아는 AI 선생님과 대화해 보세요.")

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
            st.markdown(message["text"])

    prompt = st.chat_input("무엇이 궁금한가요?")

    if prompt:
        if not api_key:
            st.warning("먼저 Google API Key를 입력하세요.")
            return

        st.session_state.messages.append({"role": "user", "text": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

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
            st.markdown(answer)


if __name__ == "__main__":
    main()

