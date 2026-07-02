# dwchoo.github.io

추동원 개인 홈페이지용 GitHub Pages 저장소입니다.

웹페이지: <https://dwchoo.github.io>

## 구성

- `index.html`: 영문/한글 토글을 포함한 메인 홈페이지
- `assets/css/styles.css`: 홈페이지 전용 스타일
- `assets/js/site.js`: 언어 전환 및 사용자 언어 선택 저장
- `assets/img/research/hdf-ec/`: HDF-EC input/result 비교 viewer용 웹 이미지
- `content/home.en.md`: 영문 홈페이지 원고 기준 파일
- `content/home.kr.md`: 한글 홈페이지 원고 기준 파일
- `docker-tutorial/`: 기존 Docker tutorial 문서

## 작업 원칙

홈페이지 본문을 수정할 때는 먼저 `content/home.en.md`와 `content/home.kr.md`를 갱신한 뒤 `index.html`에 반영합니다.

현재 프로젝트는 별도 build tool 없이 정적 HTML/CSS/JavaScript로 동작합니다.
