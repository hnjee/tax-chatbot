import streamlit as st
from llm import get_ai_response

#uv run streamlit run main.py
def main():
    st.set_page_config(page_title="소득세 챗봇", page_icon="🤖")

    st.title("소득세 챗봇 🤖") #제목 
    st.caption("소득세 관련 질문을 해보세요.")  #캡션 설명 

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

    #PR을 위한 주석입니다
    
if __name__ == "__main__":
    main()
