# FDAM 영문 사이트 자동화 (en.fdam.co.kr)

한국어 블로그(fdam.co.kr/blog)에 새 글이 올라오면 **매일 새벽 5시(한국 시간)** 자동으로:

1. 새 한국어 글을 가져오고 (`build/sync_blog.py`)
2. Claude API로 영어 번역 (`build/translate_new.py`, 모델 `claude-opus-5-5`, 한 번에 최대 5개)
3. 영문 사이트·블로그를 다시 만들고 (`build/build_en.py`, `build/build_blog.py`)
4. GitHub Pages로 en.fdam.co.kr에 배포합니다.

번역 결과는 저장소(`build/blog/en/`)에 자동 커밋되어, 같은 글을 다시 번역하지 않습니다.

## 처음 한 번만 하는 설정

1. **GitHub 저장소** — `cho-seongjin/fdam-en-site` (Public). 회사 계정이 생기면 Settings → Transfer로 옮길 수 있습니다(옮긴 뒤 DNS CNAME 대상도 새 계정으로 변경).
   - 무료 계정에서 GitHub Pages를 쓰려면 저장소가 **Public**이어야 합니다(유료 조직이면 Private 가능). 저장소에는 공개 사이트 내용과 스크립트만 있고, API 키는 들어가지 않습니다.
2. **API 키 등록** — 저장소 Settings → Secrets and variables → Actions → New repository secret
   - 이름 `ANTHROPIC_API_KEY`, 값: console.anthropic.com에서 발급한 회사 API 키
3. **Pages 켜기** — Settings → Pages → Build and deployment → Source: **GitHub Actions**
4. **도메인 연결** — Settings → Pages → Custom domain에 `en.fdam.co.kr` 입력 후 저장, **Enforce HTTPS** 체크
5. **DNS 변경(내부 직원)** — en.fdam.co.kr의 DNS 레코드를 아래로 바꿉니다.
   - `CNAME  en  →  cho-seongjin.github.io`
   - 기존 A 레코드(222.239.220.203)는 삭제. 변경 후 반영까지 수 분~수 시간.
6. **첫 실행** — Actions 탭 → "Sync English blog" → **Run workflow**

## 운영

- 수동 실행: Actions → Sync English blog → Run workflow (새 글을 바로 반영하고 싶을 때)
- 실패 알림: 실행이 실패하면 GitHub가 저장소 관리자에게 이메일을 보냅니다. 번역에 실패한 글은 다음 날 자동으로 다시 시도합니다.
- 번역 수정: `build/blog/en/<글번호>.json`의 title/description/html을 고쳐 커밋하면 자동으로 다시 배포됩니다.
- 한국어 메인·서브페이지를 바꿨을 때: `ko-src/`를 새 dist로 교체하고, 바뀐 문구 번역을 `build/tr_extra.json`(한국어 원문 → 영어)에 추가한 뒤 커밋합니다. 빌드 로그의 `missing translations`가 0인지 확인합니다(이 작업은 요청 주시면 처리).

## 비용

- GitHub Actions, GitHub Pages: 무료
- Claude API: 새 글 1개 번역마다 사용료 발생(입력 $4 / 출력 $20 per 100만 토큰 기준, 글 길이에 따라 대략 글당 $0.2~0.4 수준 예상). 한 번 실행에 최대 5개로 제한되어 있어 하루 비용이 크게 늘지 않습니다.
