# 추동원

Computer Vision Researcher & AI Engineer

Computer vision을 중심으로 AI model과 self-supervised learning을 연구하며, 실제 환경에 적용 가능한 AI system 개발에 관심이 있습니다.

- GitHub: <https://github.com/dwchoo>
- LinkedIn: <https://www.linkedin.com/in/dwchoo1991/>

## 소개

저는 image exposure restoration, low-light enhancement, self-supervised learning을 연구하는 computer vision 연구자이자 AI engineer입니다. 부산대학교 정보융합공학과 AI 전공 박사과정에서 연구를 수행했으며, 2026년 8월 박사 학위 취득 예정입니다.

제 연구는 실제 환경에서 발생하는 다양한 조명 열화 문제를 복원하면서도, 실제 배포 가능한 수준의 계산 효율성을 갖춘 vision model을 만드는 데 초점을 둡니다. Python 기반 딥러닝 연구 구현과 Go 기반 소프트웨어 개발 경험을 함께 갖고 있으며, OpenCV 기반 Go computer vision library인 GoCV에도 기여했습니다.

3D vision과 NVIDIA Isaac Sim을 활용한 시뮬레이션에도 관심이 있습니다.

## 학위논문 연구

제 박사학위논문은 low-light, over-exposed, backlit scene처럼 실제 환경에서 자주 발생하는 까다로운 조명 조건을 대상으로 하는 **unified image exposure restoration**에 초점을 둡니다. 기존처럼 under-exposure와 over-exposure를 별개의 문제로 다루기보다, 밝기, 색상, 대비, 구조적 디테일을 자연스럽게 복원하는 하나의 exposure restoration 문제로 재정의했습니다.

이 연구의 핵심 기여는 효율적이고 일관된 exposure correction을 위한 **HDF-EC**, 즉 Hierarchical Dual-Flow architecture입니다. HDF-EC는 local texture와 brightness refinement를 담당하는 CNN 기반 low-level module과 global exposure 및 structural consistency를 담당하는 Transformer 기반 high-level module을 결합합니다. 이를 통해 다양한 exposure benchmark에서 안정적인 복원 품질을 목표로 하면서도 실제 적용에 필요한 계산 효율성을 유지합니다.

## 학력

- 부산대학교 전자공학과 학사, 2010.03 - 2017.02
- 부산대학교 정보융합공학과 AI 전공 박사, 2018.09 - 2026.08 예정

## 경력

### 인빅 주식회사 (스타트업)

AI 개발 팀장 / 책임 연구원  
2023.01 - 2025.06

- 실시간 Vision AI 모델 개발 및 운용 시스템 개발
- PyTorch, TensorFlow, TensorRT, NVIDIA Triton, DeepStream 기반 Vision AI 모델 개발 및 초경량화 수행
- Go, OpenCV, GoCV를 활용해 H.264/H.265 RTSP 스트리밍 영상의 고속 처리, 실시간 AI 변환 및 중계 시스템을 개발
- Jetson, DeepStream 기반 edge-device Vision AI 솔루션을 개발

## 주요 논문

- **D. Choo**, Q. Deng, T. Park, and D. Lee, "HVR-SSLE: Hierarchical Visual Reasoning for Self-Supervised Low-Light Image Enhancement," *IEEE Access*, vol. 14, pp. 34705-34725, 2026.
- Q. Deng, **D. Choo**, H. Ji, and D. Lee, "A 5K Efficient Low-Light Enhancement Model by Estimating Increment between Dark Image and Transmission Map Based on Local Maximum Color Value Prior," *Electronics*, vol. 13, p. 1814, 2024.
- M.-j. Kim, Q. Deng, **D. Choo**, H. C. Ji, and D. Lee, "AGCSNet: High-contrast image-exposure correction with automatic illumination-map attention-based gamma and saturation correction," *ETRI Journal*, 2025.

## 프로젝트

### VGGT-ISAAC-SIM

[VGGT-ISAAC-SIM](https://github.com/dwchoo/vggt-isaac-sim): VGGT 기반 다중 시점 3D 재구성, OpenUSD 내보내기 및 Isaac Sim 시각화 파이프라인 개발

### HVR-SSLE

[HVR-SSLE](https://github.com/dwchoo/HVR-SSLE): compact self-supervised low-light image enhancement 모델을 제안한 HVR-SSLE 논문의 official PyTorch implementation을 공개함. Training/inference pipeline, dataset configuration, checkpoint handling, analysis resource를 포함해 연구 재현성을 고려함

### GoCV Contribution

OpenCV 기반 Go computer vision library인 GoCV에 기여함. Computer vision 연구를 실제 소프트웨어 구현과 연결하는 open-source contribution 수행

## 기술 역량

- Research: Computer Vision, Low-Light Image Enhancement, Image Exposure Correction, Self-Supervised Learning
- Programming: Python, Go
- Deep Learning: PyTorch, TensorFlow, TensorRT, model training, inference pipelines, experiment analysis
- Vision Systems: OpenCV, GoCV, NVIDIA Triton, Jetson, DeepStream, RTSP streaming, image restoration workflows
