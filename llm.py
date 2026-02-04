import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, FewShotChatMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from config import answer_examples

load_dotenv()

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


def get_llm(model='gpt-4o-mini'):
    llm = ChatOpenAI(model=model)
    return llm

def get_retriever():
    embedding = OpenAIEmbeddings(model='text-embedding-3-large')
    index_name = 'index-2'
    database = PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embedding
    )
    retriever = database.as_retriever(
        search_kwargs={"k": 3}
    )
    return retriever


def get_keyword_dictionary_chain():
    llm = get_llm()
    dictionary = ["사람을 나타내는 표현 -> 거주자"]

    keyword_dictionary_prompt = ChatPromptTemplate.from_template(
        f"""사용자의 질문을 보고, 키워드 사전을 참고해서 사용자의 질문을 변경해주세요. 
        만약 변경할 필요가 없다고 판단된다면, 사용자의 질문을 변경하지 않아도 됩니다. 
        그런 경우에는 질문만 리턴해주세요.
        사전: {dictionary}
        사용자의 질문: {{question}}
        """
    )
    keyword_dictionary_chain = (
        keyword_dictionary_prompt 
        | llm 
        | StrOutputParser()
    )
    return keyword_dictionary_chain


def get_chat_history_chain():
    """대화 히스토리를 고려하여 질문을 재구성하는 체인"""
    llm = get_llm()
    
    chat_history_system_prompt = (
        "이전 대화 기록과 가장 최근에 입력된 사용자 질문이 주어집니다. "
        "이 질문은 대화 기록의 맥락을 참조할 수 있습니다. "
        "대화 기록 없이도 이해할 수 있는 독립적인 질문으로 만들어주세요. "
        "질문에 답변하지 말고, 필요한 경우에만 질문을 재구성하고 "
        "필요하지 않으면 원래 질문을 그대로 반환하세요."
    )
    
    chat_history_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", chat_history_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    
    chat_history_chain = (
        chat_history_prompt 
        | llm 
        | StrOutputParser()
    )

    return chat_history_chain


def get_history_rag_chain():
    """LCEL을 사용한 RAG 체인 (히스토리 + Few-shot 포함)"""
    llm = get_llm()
    retriever = get_retriever()
    chat_history_chain = get_chat_history_chain()
        
    system_prompt = (
        "당신은 소득세법 전문가입니다. "
        "사용자의 소득세법 관련 질문에 아래 제공된 검색된 문맥을 사용하여 답변하세요. "
        "답을 모르는 경우, 모른다고 말하세요. "
        "답변을 제공할 때는 소득세법 (XX조)에 따르면 이라고 시작하면서 답변해주시고, "
        "아래 예시들을 참고하여 비슷한 형식과 톤으로 답변해주세요."
        "\n\n"
        "{context}"
    )
    

    # Few-shot 예시용 프롬프트 템플릿
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{answer}"),
        ]
    )
    
    # Few-shot 프롬프트 생성
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=answer_examples,
    )
    
    # Few-shot 예시를 포함한 프롬프트 구성
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            few_shot_prompt,  # Few-shot 예시 추가
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )

    def format_docs(docs):
        """검색된 문서들을 하나의 context 문자열로 포맷팅"""
        return "\n\n---\n\n".join([doc.page_content for doc in docs])

    def contextualized_retrieval(input_dict):
        """retriever 전에 대화 히스토리가 있으면 쿼리를 재구성하고, 없으면 원래 질문 사용"""
        query = input_dict["input"]
        chat_history = input_dict.get("chat_history", [])
        if chat_history:
            # 히스토리가 있으면 질문을 재구성
            chat_history_query = chat_history_chain.invoke({
                "chat_history": chat_history,
                "input": query
            })
            docs = retriever.invoke(chat_history_query)
        else:
            docs = retriever.invoke(query)

        return {
            "context": format_docs(docs),
            "input": query,
            "chat_history": chat_history
        }
    
    # LCEL 체인 구성
    rag_chain = (
        RunnablePassthrough()
        | RunnableLambda(contextualized_retrieval)
        | qa_prompt
        | llm
        | StrOutputParser()
    )
    
    # RunnableWithMessageHistory로 체인을 감싸서 히스토리 관리
    history_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    
    return history_rag_chain

def get_ai_response(user_message):
    """사용자 메시지를 받아 AI 응답을 스트리밍으로 반환"""
    keyword_dictionary_chain = get_keyword_dictionary_chain()
    history_rag_chain = get_history_rag_chain()

    full_chain = (
        {"input": keyword_dictionary_chain}  #RunnableWithMessageHistory는 dict를 받음
        | history_rag_chain  
    )
    
    ai_message = full_chain.stream(
        {
            "question": user_message
        },
        {
            "configurable": {"session_id": "abc123"}
        }
    )
    return ai_message
    