
from langchain.prompts import ChatPromptTemplate
from hledger_genai.models import State

def prompt():
    return ChatPromptTemplate.from_messages(
    [
        ("system", """
         기존 회계 장부, 적요, 첨부된 이미지를 기반으로, 복식부기 회계장부 전표를 생성해줘. 
         이미지에 부가세와 공급가액이 따로 나와 있으면, 각각 따로 분개처리 해줘.
         차변 금액 합계과 대변 금액 합계가 일치해야 해.
         계정 과목은 지정 계정 과목에 있는 것만 사용해.


         <기존 회계 장부>:
         {context}

         <지정 계정 과목>:
         {accounts}
         """),
        (
            "user",
            [
                {
                    "type": "text",
                    "text": "<적요>: {description}",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": "{image_url}"},
                }
            ],
        ),
    ]
)

def retrieve(state: State):
    retrieved_docs = state["vectorstore"].similarity_search(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt().invoke({"description": state["question"], "image_url": state["image_url"], "context": docs_content, "accounts": state["accounts"]})
    response = state["llmrunnable"].invoke(messages)
    return {"answer": response}


def load_accounts_for_context(accounts_journal_path: str):
    with open(accounts_journal_path, 'r') as accounts_file:
        accounts = accounts_file.readlines()
    accounts = [account.replace('account', '').split(';')[0] for account in accounts]