# dwchoo.github.io

추동원 개인 홈페이지용 GitHub Pages 저장소입니다.

웹페이지: <https://dwchoo.github.io>

## 구성

- `index.html`: 영문/한글 토글을 포함한 메인 홈페이지
- `assets/css/styles.css`: 홈페이지 전용 스타일
- `assets/js/site.js`: 언어 전환, 결과 탭, HDF-EC 샘플·비교 위치 관리
- `assets/js/pointcloud-viewer.js`: 회전 전용 VGGT point cloud 뷰어와 다운로드 진행 표시
- `assets/js/reconstruction-data.js`: 변환기가 생성하는 파일 크기·해시·초기 카메라 설정
- `assets/data/vggt/`: 500,000점 `reconstruction.ply`
- `assets/vendor/three/`: Three.js 0.185.0 모듈과 MIT 라이선스
- `assets/img/research/hdf-ec/`: HDF-EC input/result 비교 viewer용 웹 이미지
- `content/home.en.md`: 영문 홈페이지 원고 기준 파일
- `content/home.kr.md`: 한글 홈페이지 원고 기준 파일
- `docker-tutorial/`: 기존 Docker tutorial 문서

## 작업 원칙

홈페이지 본문을 수정할 때는 먼저 `content/home.en.md`와 `content/home.kr.md`를 갱신한 뒤 `index.html`에 반영합니다.

현재 프로젝트는 별도 build tool 없이 정적 HTML/CSS/JavaScript로 동작합니다.

## 로컬 실행

저장소 루트에서 실행한 뒤 <http://127.0.0.1:8765>를 엽니다. ES module과 PLY를 불러오므로 `file://`로 열지 않습니다.

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

VGGT-ISAAC-SIM이 첫 번째 기본 탭입니다. 왼쪽 마우스 드래그 또는 한 손가락 터치로 회전하며 확대·이동은 지원하지 않습니다. HDF-EC 탭에는 기존 샘플 선택, 이전·다음 버튼과 비교 슬라이더가 있습니다. 탭·언어를 바꿔도 회전, 샘플, 비교 위치가 유지됩니다. 탭은 좌우 방향키·Home·End로도 선택할 수 있습니다.

두 결과의 프레임은 본문 전체 너비를 사용하며 높이는 320–680 CSS px입니다. 뷰어는 필요할 때만 렌더링하고, 비활성 탭·화면 밖·숨겨진 페이지에서는 렌더링을 중지합니다.

## 데모 출처

표시한 결과는 [공식 VGGT Kitchen 예제](https://github.com/facebookresearch/vggt/tree/main/examples/kitchen) 사진 **25장을 각각 두 번 사용한 입력 50장**의 검증 결과입니다. 서로 다른 50개 시점으로 촬영한 데이터가 아닙니다. 최종 500,000점의 좌표·RGB·순서를 보존했습니다. 출처는 영문·한글 뷰어 캡션과 Projects에도 표기했습니다.

## 다운로드 진행 표시

파일을 받는 동안 실제 수신 바이트에 따라 `50% · 3.8 / 7.5 MB` 형태로 진행률을 표시합니다. 완료 후에는 `3D 화면을 준비하는 중…`을 보여주고 검증·PLY 파싱·카메라 준비가 끝나면 진행 바를 숨깁니다. 점 개수 표시는 실제 데이터에 맞춰 갱신됩니다.

진행률은 압축 해제된 PLY 크기 기준입니다. gzip 전송이나 Content-Length가 없는 응답에서도 JS 설정에 기록한 원래 파일 크기를 사용합니다. 모듈을 불러오는 동안에는 퍼센트를 표시하지 않습니다. 파싱 단계의 별도 퍼센트를 임의로 만들지 않습니다.

## 데이터 변환

변환은 Python 가상환경과 NumPy만 필요합니다. 홈페이지 실행에는 Python이나 NumPy가 필요하지 않습니다.

```sh
python3 -m venv /tmp/homepage-viewer-venv
/tmp/homepage-viewer-venv/bin/pip install numpy==2.5.3
/tmp/homepage-viewer-venv/bin/python scripts/export_pointcloud.py \
  --source-run /home/dwchoo/omniverse/isaac_sim/sim_data/local_data/vggt_web/jobs/479b8f0c6112472ebd8eb75062d83e2b/runs/4d342425366e4788ae571c034487f0c2 \
  --output assets/data/vggt/reconstruction.ply \
  --metadata-output assets/js/reconstruction-data.js
```

`--source-run`은 `pointcloud.npz`, `run_summary.json`, `transforms.json`을 포함한 완료 run 디렉터리입니다. 스크립트는 기록된 점 수, float32 XYZ, uint8 RGB, 배열 크기·유효성, 첫 카메라의 회전 행렬과 `world_from_vggt=identity`를 검사합니다. 필터링·점 감소·메시 생성 없이 순서 그대로 little-endian PLY로 내보내며, 모든 좌표·색상의 왕복 일치와 원본 해시를 확인합니다. `--metadata-output`의 JS 설정 파일에 점 수·파일 크기·SHA-256·초기 카메라 방향을 기록합니다. 이 옵션을 생략하면 PLY 옆에 JSON을 생성합니다.

현재 PLY는 7,500,180바이트(약 7.5 MB), 500,000점입니다. 사용자가 웹앱에서 confidence percentile 50 및 500,000점 제한을 적용해 선택한 최종 NPZ를 그대로 변환합니다. 홈페이지에서는 필터링이나 점 감소를 다시 수행하지 않습니다. 대용량 데이터 파일은 `reconstruction.ply`만 게시하며, 입력 사진·NPZ·USD는 포함하지 않습니다. 원본과 출력 해시, 좌표·색상 처리 및 vendor 출처는 [데이터 기록](docs/pointcloud-provenance.md)에 있습니다.

## 검증

```sh
/tmp/homepage-viewer-venv/bin/python scripts/test_export_pointcloud.py
/tmp/homepage-viewer-venv/bin/pip install playwright
/tmp/homepage-viewer-venv/bin/playwright install chromium
/tmp/homepage-viewer-venv/bin/python scripts/verify_homepage.py
/tmp/homepage-viewer-venv/bin/python scripts/verify_loading_progress.py
```

브라우저 검증 스크립트는 임시 로컬 HTTP server를 시작하고 종료합니다. 루트 및 `/preview/` 하위 경로, 데스크톱·모바일 터치, 상태 보존, 오류 안내와 자원 정리를 검사하며 `docs/verification/`에 결과와 스크린샷을 저장합니다. 진행 바 검증은 전송을 중간에 멈춘 HTTP 응답, gzip, 불완전 다운로드, 로딩 중 제거를 사용합니다. Playwright는 검증용 가상환경에만 설치합니다.

[검증 기록과 스크린샷](docs/verification/README.md)을 참고하세요. 모바일은 Chromium 터치 에뮬레이션으로 확인했으며, 실제 휴대폰·Safari에서의 결과와 인터넷 다운로드 시간은 별도 확인 대상입니다.

## 배포

기존 `master` 기반 GitHub Pages 흐름을 사용합니다. `master`에 커밋을 push하면 GitHub Pages에서 게시합니다. `_config.yml`과 `docker-tutorial/`은 유지합니다.

배포 시 HTML/CSS/JS와 `assets/data/vggt/`, `assets/vendor/three/`를 함께 포함합니다. 모든 뷰어 모듈·데이터 경로는 상대 경로 또는 `import.meta.url` 기준이므로 저장소 하위 경로에서도 동작합니다. 브라우저가 이전 파일을 재사용하지 않도록 HTML의 CSS·site.js와 뷰어 설정 import에 버전 쿼리를 사용합니다. 같은 경로의 구현·데이터를 교체할 때는 해당 버전도 함께 갱신합니다. 커밋 전 `git status --short`로 대상 파일을 확인하고 `.serena/` 등 작업 도구 생성물은 제외합니다.
