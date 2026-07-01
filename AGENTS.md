# AGENTS.md

이 저장소는 `dwchoo.github.io`용 GitHub Pages 개인 홈페이지 프로젝트이다. 현재 구조는 Jekyll 기본 설정과 Markdown/정적 파일 중심으로 유지한다.

## 응답 및 문서 언어

- 사용자 응답은 한국어로 작성한다.
- 기술 용어, 라이브러리명, 코드 식별자는 원문 표기를 유지한다.
- Skills 및 MCP 관련 문서는 English를 기본으로 한다.
- 이 저장소의 일반 Markdown 문서는 사용자가 별도로 요청하지 않는 한 한국어로 작성한다.
- 홈페이지 본문 콘텐츠는 영문/한글을 모두 관리한다.

## 프로젝트 구조

- `_config.yml`: GitHub Pages/Jekyll theme 설정.
- `README.md`: 저장소 설명용 문서.
- `content/home.en.md`: 홈페이지 영문 원고의 기준 파일.
- `content/home.kr.md`: 홈페이지 한글 원고의 기준 파일.
- `docker-tutorial/`: 기존 Docker tutorial 문서. 홈페이지 개편과 무관하면 보존한다.

## 작업 원칙

- 변경 전 현재 파일 구조와 기존 콘텐츠를 먼저 확인한다.
- 홈페이지 콘텐츠를 바꿀 때는 먼저 `content/home.en.md`와 `content/home.kr.md`를 갱신한 뒤 구현 파일에 반영한다.
- 영문/한글 콘텐츠는 같은 정보 구조를 유지하되, 자연스러운 표현은 각 언어에 맞게 조정한다.
- 기존 `docker-tutorial/` 콘텐츠는 사용자가 요청하지 않는 한 수정하거나 삭제하지 않는다.
- 불필요한 framework, build tool, dependency를 추가하지 않는다.
- 현재 규모에서는 단순 정적 HTML/CSS/JavaScript 또는 Jekyll 기본 기능을 우선한다.
- Docker 또는 Docker 기반 설치 방법은 사용하지 않는다.
- `.serena/` 같은 작업 도구 생성물은 사용자가 요청하지 않는 한 stage하거나 commit하지 않는다.

## 콘텐츠 스타일

- 홈페이지는 개인 연구자/AI engineer 소개 페이지로 구성한다.
- 기본 언어는 English로 두고, Korean 버전을 함께 제공한다.
- 학력, 경력, 논문, 프로젝트, 기술 역량은 간결하게 작성한다.
- 경력/프로젝트의 한글 bullet은 이력서식 문체를 우선한다. 예: `개발`, `수행`, `기여함`.
- 회사 경력은 필요한 범위만 기술하고, 불필요하게 상세한 회사 설명은 피한다.
- 논문 목록에서는 `D. Choo`를 볼드 처리해 저자 식별성을 높인다.
- HVR-SSLE repository 링크는 상단 링크가 아니라 프로젝트 또는 논문 관련 섹션에 배치한다.

## 구현 가이드

- 메인 홈페이지 구현 시 `README.md`에 의존하지 말고 `index.html` 또는 Jekyll page를 명시적으로 만든다.
- 디자인은 연구자 개인 홈페이지에 맞게 차분하고 읽기 쉬운 구성을 우선한다.
- 언어 전환은 `EN | KR` toggle 방식이 이 저장소 규모에 적합하다.
- 반응형 레이아웃을 기본으로 하며, 모바일에서 텍스트가 겹치지 않도록 확인한다.
- 외부 링크는 GitHub, LinkedIn, HVR-SSLE 등 검증된 공개 링크만 사용한다.

## 검증

- Markdown 변경 후에는 해당 파일을 다시 읽어 오탈자와 섹션 순서를 확인한다.
- 구현 변경 후에는 가능하면 로컬에서 정적 페이지를 열거나 간단한 HTTP server로 확인한다.
- GitHub Pages/Jekyll 동작을 바꾸는 경우 `_config.yml` 영향 범위를 확인한다.
- 커밋 전에는 `git status --short`로 의도한 파일만 staged 상태인지 확인한다.
