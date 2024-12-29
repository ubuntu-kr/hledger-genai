from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, StateGraph
import argparse
from models import State, TransactionModel, AppConfig
from raghelpers import retrieve, generate, load_accounts_for_context
from ioutils import image_to_base64
from vecstore_loader import load_vectorstore, prepare_vectorstore
import yaml, sys


def main() -> int:  
    parser = argparse.ArgumentParser(description='hledger 전표 생성기')
    parser.add_argument('--desc', type=str, help='적요', required=False)
    parser.add_argument('--receipt-path', type=str, help='거래증빙 파일 경로', required=False)
    parser.add_argument('--config-path', type=str, help='환경설정 YAML 파일 경로', default='./config.yaml')
    parser.add_argument('--task', type=str, help='수행할 작업(embed 벡터 스토어에 문서 임베딩 작업, generate 회계 전표 생성)', required=True, default='generate', choices=['embed', 'generate'])
    parser.add_argument('--dry-run', action='store_true', help='실제 hledger 회계장부 파일에 추가하지 않고 출력만 확인')
    args = parser.parse_args()

    with open(args.config_path, 'r') as config_file:
        config_dict = yaml.safe_load(config_file)
    config = AppConfig.model_validate(config_dict)

    if args.task == "embed":
        prepare_vectorstore(config.vectorstore.path, config.vectorstore.input)
        return 0
    elif args.task == "generate":
        vectorstore = load_vectorstore(config.vectorstore.path)
    else:
        print("작업을 선택해주세요")
        return 1

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    struct_llm = llm.with_structured_output(TransactionModel)

    receipt_image = image_to_base64(args.receipt_path)
    
    # Compile application and test
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()

    response = graph.invoke({
        "question": args.desc, 
        "accounts": load_accounts_for_context(config.ledger.accounts_path),
        "image_url": receipt_image,
        "llmrunnable": struct_llm,
        "vectorstore": vectorstore})
    print(response["answer"].model_dump_json(indent=2))
    txobject = response["answer"]
    attachment_tag = f"attach:attachments/{args.receipt_path.split("/")[-1]}"
    hledgertx = txobject.to_hledger_tx(attachment_tag)
    
    if args.dry_run:
        print(hledgertx)
    else:
        with open(config.ledger.journal_path, 'a') as dest_journal:
            dest_journal.write(hledgertx)
    return 0

if __name__ == "__main__":
    sys.exit(main())