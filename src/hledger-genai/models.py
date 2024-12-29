from pydantic import BaseModel, Field
import datetime
from typing_extensions import List, TypedDict
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_core.runnables import Runnable

class EntryModel(BaseModel):
    account: str = Field(default="", title="계정 과목")
    debit_amount: int = Field(default=0, title="차변 금액")
    credit_amount: int = Field(default=0, title="대변 금액")


class TransactionModel(BaseModel):
    transaction_date: datetime.datetime = Field(title="거래일시")
    transaction_code: str = Field(default=None, title="승인번호(혹은 거래번호)")
    payee: str = Field(default="", title="거래처")
    description: str = Field(title="적요")
    entries: list[EntryModel] = Field(title="전표 분개")

    def to_hledger_tx(self, comments: str = None, currency: str = "KRW") -> str:
        txcode = f"({self.transaction_code})" if self.transaction_code else ""
        txcomments = f"    ; {comments}" if comments else ""
        
        tx = f"\n{self.transaction_date.strftime('%Y-%m-%d')} {txcode} {self.payee} | {self.description} {txcomments}\n"
        for entry in self.entries:
            amount = f"{entry.debit_amount}" if entry.debit_amount > 0 and entry.credit_amount == 0 else f"-{entry.credit_amount}"
            tx += f"    {entry.account}                 {amount} {currency}\n"
        tx += "\n"
        return tx

class State(TypedDict):
    question: str
    context: List[Document]
    accounts: List[str]
    answer: TransactionModel
    image_url: str
    vectorstore: VectorStore
    llmrunnable: Runnable

class AppConfigLedger(BaseModel):
    journal_path: str
    currency: str
    accounts_path: str

class AppConfigVectorStore(BaseModel):
    path: str
    input: List[str]
class AppConfig(BaseModel):
    ledger: AppConfigLedger
    vectorstore: AppConfigVectorStore