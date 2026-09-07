# 홈페이지 결과 탭 검증 기록

2026-09-07 사용자가 선택한 Kitchen 500,000점 최종본과 다운로드 진행 바를 검증한 기록입니다.

## 환경 및 최초 표시 시간

- 브라우저: Chromium 151.0.7922.34 (Playwright, Linux ARM64, headless)
- 렌더링: SwiftShader WebGL, 실제 휴대폰 대신 Chromium 터치 에뮬레이션
- 데스크톱: 1440×1100 CSS px, DPR 1, 뷰어 1080×680 CSS px
- 모바일: 390×844 CSS px, 기기 DPR 3을 renderer DPR 2로 제한, 뷰어 358×320 CSS px
- 크기 변경: 데스크톱 1000×900, 모바일 가로 844×390, 숨긴 상태 600×800
- PLY 크기: 7,500,180바이트 (약 7.5 MB), 500,000점
- localhost 페이지 탐색 시작부터 첫 실제 render 호출까지: 데스크톱 **641.9 ms**, 모바일 **813.9 ms**

최초 표시 시간은 각각 새 browser context에서 한 번 측정한 로컬 결과입니다. 인터넷 전송, GitHub Pages 캐시, 실제 모바일 GPU 성능을 대표하지 않습니다. 데이터 로딩·파싱·검증과 화면으로 스크롤하는 시간이 포함됩니다.

## 검증 결과

| 항목 | 결과 |
| --- | --- |
| 원본과 PLY의 전체 XYZ·RGB·순서 | 500,000행 전체 바이트 일치, 원본 SHA-256 유지 |
| 변환기 유효성 검사 | 정상 왕복·잘못된 dtype/크기/점 수/좌표/카메라/완료 상태 등 13개 테스트 통과 |
| 초기 방향·색상 | 첫 입력 카메라 방향 수치 일치, 원본 사진과 정방향·색상 육안 비교, sRGB → linear 변환 수치 확인 |
| 기본 탭 | VGGT-ISAAC-SIM 선택, 하나의 canvas·Points·geometry |
| 마우스·터치 회전 | 좌측 드래그·한 손가락 터치로 카메라 회전, 거리·회전 중심 유지 |
| 제한된 조작 | 휠·우측/중앙 드래그·두 손가락 조작 후 카메라 위치·거리 불변 |
| 상태 보존 | 반복 탭 전환·EN/KR 전환 후 회전, 샘플, 비교 위치 유지 |
| 접근성 | tablist/tab/tabpanel 연결, 선택 상태, roving tabindex, 방향키·Home·End 전환 |
| HDF-EC | 8개 샘플 모두 로딩, 이전·다음, 샘플 선택, 비교 슬라이더 동작 |
| 크기 변경 | 회전 방향·중심 유지, 프레임 재맞춤, 유효한 clipping 범위 |
| 불필요한 렌더링 | idle·비활성 탭·화면 밖·숨겨진 페이지에서 render 호출 증가 없음 |
| 중복 로딩 | 반복 탭/언어 전환 후 PLY 요청 1회, canvas 1개 |
| 로딩 중 전환·제거 | 다른 탭에서 로딩 완료 시 render 0회, 복귀 시 표시, 제거 시 요청·canvas 정리 |
| 오류 처리 | PLY 404·동일 크기 데이터 손상·불완전 다운로드·vendor module 404·WebGL 생성 실패·context loss에 한/영 안내 |
| 오류 시 기존 기능 | 모든 오류 상황에서 HDF-EC 샘플 이동 유지 |
| 경로 | `/`와 `/preview/` 하위 경로에서 모듈·PLY·이미지 로딩 |
| JavaScript | 처리되지 않은 오류 0건, 정상 시나리오에서 console error·HTTP 4xx/5xx 0건 |

페이지 숨김은 `document.hidden`과 `visibilitychange`를 주입하여 해당 로직을 확인했습니다. 탭 전환과 화면 밖 검사는 실제 DOM 표시·스크롤로 수행했습니다. 렌더링 횟수와 카메라 상태 관찰용 코드는 테스트 HTTP 응답에만 주입하며 게시 JavaScript에는 포함되지 않습니다.

진행 바 전용 검증은 게시 JavaScript를 변경하지 않고 실제 HTTP 스트림을 사용해 수행했습니다. 이 로컬 검증에는 Safari·Firefox·실제 휴대폰 및 배포 URL 검증이 포함되지 않습니다.

## 다운로드 진행 바

별도 `verify_loading_progress.py`에서 HTTP 전송을 중간에 멈춰 진행률과 수신 MB를 확인했습니다. 일반 응답은 정확히 절반을 받은 상태에서 50%를 표시했고, gzip 응답은 압축 해제된 바이트를 기준으로 0–100%를 계산했습니다. Content-Length가 없는 응답에서도 진행률이 표시됐습니다.

로딩 중 EN/KR·결과 탭 전환 후 진행 상태가 유지됐고, 완료 후 `preparing` 단계에 100% 다운로드 완료를 표시한 다음 뷰어를 준비했습니다. 불완전 파일에서는 오류 안내와 함께 진행 바를 숨겼으며, 로딩 중 DOM 제거 시 요청·canvas가 정리됐습니다. 처리되지 않은 JavaScript 오류는 0건입니다.

[진행 바 검증 원시 결과](loading-results.json)를 참고하세요. 입력 데이터 파일은 `reconstruction.ply`만 요청하며 사진·NPZ·USD를 다운로드하지 않습니다.

## 데이터 출처 확인

입력 manifest에서 사진 25종의 SHA-256이 각각 두 번 나타나는 것을 확인했습니다. 원본 사진 25장을 복제한 입력 50장으로 검증한 결과라는 출처를 EN/KR 캡션·Projects에 표기했습니다. 500,000점에 추가 필터링·점 감소를 적용하지 않았습니다.

## 스크린샷

- [데스크톱 VGGT 기본 구도](desktop-vggt.png)
- [모바일 VGGT 기본 구도](mobile-vggt.png)
- [데스크톱 HDF-EC 한글](desktop-hdf-kr.png)
- [모바일 HDF-EC 한글](mobile-hdf-kr.png)
- [다운로드 진행 바 — 데스크톱](loading-plain.png)
- [다운로드 진행 바 — 모바일 gzip](loading-gzip.png)

스크린샷은 페이지 스크롤 상태의 viewport 캡처입니다. [자동 검증 원시 결과](browser-results.json)와 [재실행 방법](../../README.md)을 함께 참고하세요.
