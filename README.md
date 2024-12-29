# hledger-genai

Langchain, Gemini 를 활용하여 hledger 회계 장부에 거래 전표를 자동으로 생성하여 입력하는 CLI 입니다.

## config.yaml

`hledger-genai` CLI는 기존 hledger 회계 장부와 계정과목 파일을 기반으로 거래 전표를 생성하므로, 아래와 같은 형식으로 `config.yaml`을 먼저 작성해야 합니다. 

```yaml
ledger: 
  # 회계 전표를 생성하여 추가할 회계장부 journal 파일 경로
  journal_path: ../2024/revenue-business.journal 
  # 계정과목 데이터만 있는 hledger journal 파일 경로
  accounts_path: ../2024/accounts.journal
  # 전표 생성시 사용할 통화 코드
  currency: KRW
vectorstore:
  # 벡터스토어의 데이터 저장할/불러올 경로
  path: ./revenue-business-vectorstore
  # 벡터스토어에 임베딩 하여 넣을 텍스트 문서 파일 경로 (hledger journal 파일)
  input:
    - ../**/revenue-business.journal
    - ../**/accounts.journal
```
## CLI 사용
### 설치

```bash
pip install git+https://github.com/ubuntu-kr/hledger-genai.git
```

### Google API Key 환경변수 설정

Google AI Studio 혹은 Google Cloud Console 에서 API키를 발급하여 `GOOGLE_API_KEY` 환경변수로 설정 해 주세요. 필요에 따라 Generative Language API 활성화가 따로 필요할 수 있습니다.

- [Google AI Studio 에서 발급](https://aistudio.google.com/apikey)
- [Google Cloud Console 에서 API키 발급](https://console.cloud.google.com/apis/credentials)
  - 화면 상단의 `사용자 인증 정보 만들기` 누르면 나오는 드롭다운에서, `API 키`선택
- [Google Cloud Console 에서 Generative Language API 활성화](https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com)

```bash
export GOOGLE_API_KEY=<Google Cloud 에서 발급한 API키>
```

## 벡터스토어 파일 생성

전표 생성 기능 사용 전, 벡터 스토어에 텍스트 문서 파일에 해당하는 hledger journal 파일을 불러와서 임베딩 합니다. 

```bash
hledger-genai --config-path config.yaml --task embed
```

## 회계전표 생성

그 다음, 영수증 등 거래증빙 이미지 파일과 거래에 대한 적요를 입력하여 회계 전표를 생성하여 hledger journal 파일에 바로 기록할 수 있습니다.

```bash
hledger-genai --config-path config.yaml --task generate --receipt-path 영수증.png --desc "<거래 적요(설명) 입력>"
```

hledger journal 파일에 전표 기록 없이, 미리 확인만 하려면 `--dry-run` 옵션을 사용합니다.
```bash
hledger-genai --config-path config.yaml --task generate --receipt-path 영수증.png --desc "<거래 적요(설명) 입력>" --dry-run
```
