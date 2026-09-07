# dwchoo.github.io

추동원 개인 홈페이지용 GitHub Pages 저장소입니다.

웹페이지: <https://dwchoo.github.io>

## 구성

- `index.html`: 영문/한글 토글을 포함한 메인 홈페이지
- `assets/css/styles.css`: 홈페이지 전용 스타일
- `assets/js/site.js`: 언어 전환, 결과 탭, HDF-EC 샘플·비교 위치 관리
- `assets/js/pointcloud-viewer.js`: 회전 전용 VGGT point cloud 뷰어
- `assets/data/vggt/`: 453,253점 binary PLY와 해시·초기 카메라 정보
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

## 데이터 변환

변환은 Python 가상환경과 NumPy만 필요합니다. 홈페이지 실행에는 Python이나 NumPy가 필요하지 않습니다.

```sh
python3 -m venv /tmp/homepage-viewer-venv
/tmp/homepage-viewer-venv/bin/pip install numpy==2.5.3
/tmp/homepage-viewer-venv/bin/python scripts/export_pointcloud.py \
  --source-run /home/dwchoo/omniverse/isaac_sim/sim_data/local_data/vggt_web/jobs/766e4f73b8cf47f98d3f5c62d128b42d/runs/76792ce3d6414c049bedae5152fe084e \
  --output assets/data/vggt/pointcloud.ply
```

`--source-run`은 `pointcloud.npz`, `run_summary.json`, `transforms.json`을 포함한 완료 run 디렉터리입니다. 스크립트는 기록된 점 수, float32 XYZ, uint8 RGB, 배열 크기·유효성, 첫 카메라의 회전 행렬과 `world_from_vggt=identity`를 검사합니다. 필터링·점 감소·메시 생성 없이 순서 그대로 little-endian PLY로 내보내며, 모든 좌표·색상의 왕복 일치와 원본 해시를 확인합니다. 출력 `.json`에는 점 수·파일 크기·SHA-256·초기 카메라 방향을 기록합니다.

현재 PLY는 6,798,975바이트입니다. 입력은 이미 confidence percentile 90 조건으로 정리된 데이터이며, 홈페이지 변환에서 조건을 다시 적용하지 않습니다. 원본과 출력 해시, 좌표·색상 처리 및 vendor 출처는 [데이터 기록](docs/pointcloud-provenance.md)에 있습니다.

## 검증

```sh
/tmp/homepage-viewer-venv/bin/python scripts/test_export_pointcloud.py
/tmp/homepage-viewer-venv/bin/pip install playwright
/tmp/homepage-viewer-venv/bin/playwright install chromium
/tmp/homepage-viewer-venv/bin/python scripts/verify_homepage.py
```

브라우저 검증 스크립트는 임시 로컬 HTTP server를 시작하고 종료합니다. 루트 및 `/preview/` 하위 경로, 데스크톱·모바일 터치, 상태 보존, 오류 안내와 자원 정리를 검사하며 `docs/verification/`에 결과와 스크린샷을 저장합니다. Playwright는 검증용 가상환경에만 설치합니다.

[검증 기록과 스크린샷](docs/verification/README.md)을 참고하세요. 모바일은 Chromium 터치 에뮬레이션으로 확인했으며, 실제 휴대폰·Safari에서의 결과와 인터넷 다운로드 시간은 별도 확인 대상입니다.

## 배포

기존 `master` 기반 GitHub Pages 흐름을 사용합니다. `master`에 커밋을 push하면 GitHub Pages에서 게시합니다. `_config.yml`과 `docker-tutorial/`은 유지합니다.

배포 시 HTML/CSS/JS와 `assets/data/vggt/`, `assets/vendor/three/`를 함께 포함합니다. 모든 뷰어 모듈·데이터 경로는 상대 경로 또는 `import.meta.url` 기준이므로 저장소 하위 경로에서도 동작합니다. 커밋 전 `git status --short`로 대상 파일을 확인하고 `.serena/` 등 작업 도구 생성물은 제외합니다.
