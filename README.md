# 소득세 챗봇 🤖

소득세법 전문 지식을 기반으로 사용자의 질문에 정확하게 답변하는 AI 챗봇입니다.

배포 링크: https://hnjee-tax-chatbot.streamlit.app/


## 주요 기능

### 📚 RAG (Retrieval-Augmented Generation)
- **Pinecone 벡터 데이터베이스**를 활용한 소득세법 정보 검색
- **OpenAI text-embedding-3-large** 모델로 고품질 임베딩 생성
- 질문과 가장 관련성 높은 상위 3개 법률 문서 자동 검색

### 💬 대화 히스토리 관리
- 이전 대화 맥락을 고려한 질문 재구성
- 세션 기반 대화 히스토리 유지
- 대화 흐름에 맞는 자연스러운 답변 제공

### 🎯 Few-Shot Learning
- 실제 소득세법 질의응답 예시를 학습 데이터로 활용
- 일관된 답변 형식과 톤 유지
- 법조문 인용 형식 (예: "소득세법 제XX조에 따르면...")으로 신뢰성 향상

### 🔍 지능형 쿼리 처리
- 키워드 사전 기반 질문 최적화 (예: "사람" → "거주자")
- 맥락을 고려한 질문 재구성
- 대화 히스토리 기반 의도 파악



## 사용 방법

1. 웹 브라우저에서 애플리케이션 접속
2. 채팅 입력창에 소득세 관련 질문 입력
3. AI가 소득세법 조항을 기반으로 답변 제공
4. 추가 질문을 통해 대화 이어가기 가능

## 질문 예시
- "연봉 5000만원인 직장인의 소득세는 얼마인가요?" 
- "소득은 어떻게 구분되나요?"
- "소득세의 과세 기간은 어떻게 되나요?"
- "원천징수 영수증은 언제 발급받을 수 있나요?"
- "근로소득공제는 어떻게 계산하나요?"





## 기술 스택

- **프론트엔드**: Streamlit
- **LLM**: OpenAI GPT-4o-mini
- **임베딩**: OpenAI text-embedding-3-large
- **벡터 DB**: Pinecone
- **프레임워크**: LangChain
- **Python**: 3.11+
- **패키지 관리**: uv

## 사용 라이브러리 
- `langchain`: LLM 체인 구성 및 관리
- `langchain-openai`: OpenAI 모델 통합
- `langchain-pinecone`: Pinecone 벡터 스토어 통합
- `streamlit`: 웹 UI 프레임워크
- `python-dotenv`: 환경변수 관리

## 프로젝트 구조

```
tax-chatbot/
├── main.py           # Streamlit 웹 애플리케이션 메인 파일
├── llm.py            # LLM 체인 및 RAG 로직 구현
├── config.py         # Few-shot 예시 및 설정
├── pyproject.toml    # 프로젝트 의존성 관리
└── .env              # 환경변수 (API 키 등)
```

## 로컬 설치 및 실행 방법 

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd tax-chatbot

# 의존성 설치 (uv 사용)
uv sync
```

### 2. 환경변수 설정

`.env` 파일을 프로젝트 루트에 생성하고 다음 내용을 입력하세요:

```bash
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
```

### 3. 애플리케이션 실행

```bash
uv run streamlit run main.py
```

브라우저에서 자동으로 `http://localhost:8501`이 열립니다.
