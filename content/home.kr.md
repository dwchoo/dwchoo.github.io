# 추동원

Computer Vision Researcher & AI Engineer

영상 복원과 self-supervised foundation model을 연구하며, 3D reconstruction과 NVIDIA Isaac Sim을 활용한 시뮬레이션에 관심을 두고 있습니다.

Image Restoration · Self-Supervised Learning · 3D Reconstruction · Digital Twin (Isaac Sim)

- GitHub: <https://github.com/dwchoo>
- LinkedIn: <https://www.linkedin.com/in/dwchoo1991/>

## 연구 관심 분야

### Image Restoration

학습하지 않은 환경에서도 강건하게 동작하는 영상 복원 모델을 연구합니다. 합성 데이터와 self-supervised learning을 활용해 저조도·과노출·역광을 복원하고, 일반화 성능과 추론 효율을 함께 개선합니다.

관련 연구: HDF-EC, HVR-SSLE

### 3D Reconstruction

다중 시점 영상 기반 3D 재구성과 **NVIDIA Isaac Sim을 활용한 시뮬레이션**에 관심을 두고 있습니다.

관련 프로젝트: VGGT-ISAAC-SIM

## 프로젝트

### 3D Reconstruction — VGGT-ISAAC-SIM

<!-- 배치: 3D 데모와 출처 캡션 아래에 프로젝트 설명을 표시함. -->

데모 출처: [공식 VGGT Kitchen 예제](https://github.com/facebookresearch/vggt/tree/main/examples/kitchen). 원본 사진 25장을 각각 두 번 사용한 입력 50장으로 검증 수행. 뷰어에는 최종 500,000점 결과를 표시함.

- **VGGT 기반 3D Reconstruction:** 다중 시점 사진을 업로드하면 사전 학습된 VGGT-1B로 장면의 3D 구조와 카메라를 추정하는 웹앱을 개발함. 재구성 결과를 컬러 포인트클라우드와 OpenUSD 장면으로 변환함.
- **NVIDIA Triton Inference Server:** 웹 애플리케이션과 GPU 추론을 분리하고, VGGT-1B를 GPU 메모리에 상주시켜 사진 묶음 단위로 실행하는 추론 서비스를 구성함.
- **NVIDIA Isaac Sim 연동:** OpenUSD 장면을 Isaac Sim에서 렌더링하고, WebRTC를 통해 브라우저에서 회전·이동·확대할 수 있도록 구현함. GPU 재추론 없이 confidence 필터를 조절하고 결과를 저장할 수 있도록 연결함.

[GitHub에서 보기](https://github.com/dwchoo/vggt-isaac-sim)

### Image Restoration — HDF-EC

<!-- 배치: 비교 데모와 샘플 조작 요소 아래에 연구 설명을 표시함. -->

- **통합 노출 복원:** 저조도·과노출·역광을 하나의 모델로 복원하는 HDF-EC를 제안함. 합성 데이터와 self-supervised learning으로 여러 노출 문제에 공통으로 활용할 수 있는 **Foundation Model**을 구축함.
- **Hierarchical Dual-Flow:** 열화된 입력의 잠재 표현을 정상 노출 상태로 옮기는 **latent transport**로 복원을 정식화함. CNN의 국소 보정과 Transformer의 전체 복원 목표 추정을 결합하고, 동일한 모듈을 반복 사용하도록 설계함.
- **일반화 성능과 추론 효율:** 사전학습 모델을 대상 데이터에 fine-tuning한 뒤, 학습에 사용하지 않은 데이터에서 일반화 성능을 검증함. 잠재 공간 연산과 가중치 공유로 모델 크기를 줄이고 추론 자원 사용량을 절감함.

파라미터 **5.065M** · 연산량 **81.3 GFLOPs** · 추론 메모리 **0.420 GiB** — 512 × 512 입력 기준

### HVR-SSLE

[HVR-SSLE](https://github.com/dwchoo/HVR-SSLE): 합성 데이터만으로 학습한 저조도 영상 개선 모델의 일반화 가능성을 검증한 제1저자 연구로, *IEEE Access*에 게재함. 평가 대상의 학습 데이터나 별도의 fine-tuning 없이 새로운 환경에서 평가했으며, 모델을 0.354M 파라미터로 구현하고 PyTorch 코드를 공개함.

### GoCV Contribution

OpenCV CUDA 기능을 Go에서 사용하는 과정에서 누락된 Go wrapper 함수와 테스트·타입 오류를 보완함. 제안한 PR 2건이 공식 저장소에 병합됨

## 주요 논문

- **D. Choo**, Q. Deng, T. Park, and D. Lee, "HVR-SSLE: Hierarchical Visual Reasoning for Self-Supervised Low-Light Image Enhancement," *IEEE Access*, vol. 14, pp. 34705-34725, 2026.
- Q. Deng, **D. Choo**, H. Ji, and D. Lee, "A 5K Efficient Low-Light Enhancement Model by Estimating Increment between Dark Image and Transmission Map Based on Local Maximum Color Value Prior," *Electronics*, vol. 13, p. 1814, 2024.
- M.-j. Kim, Q. Deng, **D. Choo**, H. C. Ji, and D. Lee, "AGCSNet: High-contrast image-exposure correction with automatic illumination-map attention-based gamma and saturation correction," *ETRI Journal*, 2025.

## 학력 및 경력

### 학력

- 부산대학교 전자공학과 학사, 2010.03 - 2017.02
- 부산대학교 정보융합공학과 AI 전공 박사, 2018.09 - 2026.08

### 인빅 주식회사 (스타트업)

책임연구원 (실무상 개발1팀을 이끎)

2023.01 - 2025.06

#### Vision AI 개발

- 실시간 CCTV 저조도 영상 개선·다채널 객체 탐지 시스템 개발 및 TensorRT 기반 추론 최적화 수행
- Go 기반 RTSP 서버와 공유 메모리로 Python의 영상 수신·AI 처리·송신을 연결하는 실시간 영상 backend 설계·구현
- Jetson AGX Orin에 저조도 개선·객체 탐지 기능 이식·검증 및 저조도 개선 SW의 GS 인증 1등급 취득에 기여함
- FastAPI 기반 이미지·동영상 처리 플랫폼의 구조 설계 및 B2B 영상 AI용 Python gRPC 서버 설계·개발

#### 3D Reconstruction & Digital Twin — 방위사업청 R&D 과제

- 3D reconstruction과 NVIDIA Omniverse·Isaac Sim 기반 Digital Twin을 포함한 방위사업청 과제에서 기술 기획 및 협력기관 조율 수행
- 영상 개선·객체 탐지 pipeline 개발, Omniverse 화면의 WebRTC 기반 웹 연동 및 OpenUSD 샘플을 활용한 초기 통합 시연 구현

## 기술 역량

- Research: Computer Vision, Low-Light Image Enhancement, Image Exposure Correction, Self-Supervised Learning, 3D Reconstruction
- Programming: Python, Go
- Deep Learning: PyTorch, TensorRT, RT-DETR, model training, inference pipelines, experiment analysis
- Vision Systems: OpenCV, GoCV, Jetson, RTSP streaming, shared memory
- AI Platforms: FastAPI, gRPC
- 3D Tools: NVIDIA Isaac Sim, NVIDIA Omniverse, OpenUSD

<!-- 3D 뷰어 UI 원고 (구현 참고)
3D 재구성을 불러오는 중…
3D 데이터를 다운로드하는 중…
3D 화면을 준비하는 중…
다운로드 완료
다운로드 진행률: {percent}% · {received} / {total} MB
{count}점 · 드래그하여 회전
-->
