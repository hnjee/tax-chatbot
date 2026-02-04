import streamlit as st
from llm import get_ai_response

st.set_page_config(page_title="소득세 챗봇", page_icon="🤖")

st.title("소득세 챗봇 🤖") #제목 
st.caption("소득세 관련 질문을 해보세요.")  #캡션 설명 

# st.chat_input(placeholder="질문을 입력하세요.") #채팅 입력 창 
# st.chat_message("user"): #사용자 메시지 창 
# st.chat_message("ai"): #ai 메시지 창 
# st.chat_message("assistant"): #assistant 메시지 창 
# st.chat_message("system"): #system 메시지 창 
# st.chat_message("error"): #error 메시지 창 

# with 문을 사용하면 아래 들여쓰기에 있는 내용을 이 창 안에 넣어줌
# with st.chat_message("user"): #사용자 메시지 창 
#     st.write("Hello, how are you?") #사용자 메시지 창에 메시지 출력

#st.session_state
#streamlit은 채팅을 입력할 때마다 코드가 전체적으로 다시 실행된다.
#st.session_state는 코드가 다시 실행되어도 데이터를 유지해주는 특수 저장소. (새로고침 전까지 히스토리 유지)

if 'message_list' not in st.session_state:
    st.session_state.message_list = []

#기존 채팅 기록 출력
for message in st.session_state.message_list: 
    with st.chat_message(message["role"]):
        st.write(message["content"])

#채팅 입력 창에 질문이 입력되면 새로운 메세지 창 추가 
if user_question := st.chat_input(placeholder="질문을 입력하세요."): 
    with st.chat_message("user"): # 사용자 메시지 창 생성 
        st.write(user_question)  
    st.session_state.message_list.append({"role": "user", "content": user_question}) #채팅 기록 추가

    with st.spinner("답변을 준비하는 중입니다"):
        ai_response = get_ai_response(user_question)
        with st.chat_message("ai"):
            ai_message = st.write_stream(ai_response)
            st.session_state.message_list.append({"role": "ai", "content": ai_message})