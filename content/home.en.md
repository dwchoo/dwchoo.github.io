# Dongwon Choo

Computer Vision Researcher & AI Engineer

I work on image restoration and self-supervised foundation models, with interests in 3D reconstruction and simulation using NVIDIA Isaac Sim.

Image Restoration · Self-Supervised Learning · 3D Reconstruction · Digital Twin (Isaac Sim)

- GitHub: <https://github.com/dwchoo>
- LinkedIn: <https://www.linkedin.com/in/dwchoo1991/>

## Research Interests

### Image Restoration

I study image restoration that generalizes to unseen environments. My work uses synthetic data and self-supervised learning to restore low-light, over-exposed, and backlit images while improving inference efficiency.

Related work: HDF-EC, HVR-SSLE

### 3D Reconstruction

I am interested in multi-view 3D reconstruction and simulation using **NVIDIA Isaac Sim**.

Related project: VGGT-ISAAC-SIM

## Projects

### 3D Reconstruction — VGGT-ISAAC-SIM

<!-- Layout: show the 3D demo, six input-photo thumbnails, and the source caption before the project description. -->

Input photos · 6 of 25 views

VGGT estimates a scene's 3D structure from photos taken from multiple viewpoints.

<!-- Thumbnails: official Kitchen images 00.png, 04.png, 09.png, 14.png, 19.png, and 24.png. -->

Demo source: the [official VGGT Kitchen example](https://github.com/facebookresearch/vggt/tree/main/examples/kitchen). The 25 source images were duplicated to form a 50-image validation run; the viewer shows the final 500,000-point result.

- **VGGT-based 3D Reconstruction:** I built a web application that estimates scene geometry and cameras from uploaded multi-view images using pretrained VGGT-1B. Reconstructions are exported as colored point clouds and OpenUSD scenes.
- **NVIDIA Triton Inference Server:** I separated GPU inference from the web application and deployed VGGT-1B as a serving endpoint, keeping the model resident in GPU memory to process each scene’s image set.
- **NVIDIA Isaac Sim Integration:** I integrated Isaac Sim rendering with WebRTC so users can rotate, pan, and zoom through reconstructed scenes in their browser. Users can also adjust confidence filtering without rerunning GPU inference and save the updated results.

[View on GitHub](https://github.com/dwchoo/vggt-isaac-sim)

### Image Restoration — HDF-EC

<!-- Layout: show the comparison demo and sample controls before the research description. -->

- **Unified Exposure Restoration:** I proposed HDF-EC to restore low-light, over-exposed, and backlit images within a single model. Using synthetic data and self-supervised learning, I built a shared **Foundation Model** for exposure restoration.
- **Hierarchical Dual-Flow:** I formulated restoration as **latent transport** from degraded to normal exposure. The architecture combines local latent corrections by a CNN with global restoration targets estimated by a Transformer, reusing the same modules across successive restoration steps.
- **Generalization and Inference Efficiency:** I evaluated generalization on unseen datasets after fine-tuning the pretrained model on target data. Latent-space processing and weight sharing reduced model size and inference resource requirements.

**5.065M** parameters · **81.3 GFLOPs** · **0.420 GiB** inference memory — 512 × 512 input

### HVR-SSLE

[HVR-SSLE](https://github.com/dwchoo/HVR-SSLE): First-author research published in *IEEE Access* on low-light enhancement learned from synthetic data. I evaluated generalization without using the target benchmarks' training data or additional fine-tuning, and released the PyTorch implementation of the 0.354M-parameter model.

### GoCV Contribution

Contributed missing Go wrapper functions and fixes for tests and type errors while using OpenCV CUDA functionality from Go. Both pull requests were merged into GoCV.

## Selected Publications

- **D. Choo**, Q. Deng, T. Park, and D. Lee, "HVR-SSLE: Hierarchical Visual Reasoning for Self-Supervised Low-Light Image Enhancement," *IEEE Access*, vol. 14, pp. 34705-34725, 2026.
- Q. Deng, **D. Choo**, H. Ji, and D. Lee, "A 5K Efficient Low-Light Enhancement Model by Estimating Increment between Dark Image and Transmission Map Based on Local Maximum Color Value Prior," *Electronics*, vol. 13, p. 1814, 2024.
- M.-j. Kim, Q. Deng, **D. Choo**, H. C. Ji, and D. Lee, "AGCSNet: High-contrast image-exposure correction with automatic illumination-map attention-based gamma and saturation correction," *ETRI Journal*, 2025.

## Background

### Education

- Pusan National University, B.S. in Electronics Engineering, 2010.03 - 2017.02
- Pusan National University, Ph.D. in Information Convergence Engineering, AI Major, 2018.09 - 2026.08

### InBic Inc. (startup)

Senior Researcher (led Development Team 1)

2023.01 - 2025.06

#### Vision AI Development

- Developed real-time CCTV low-light enhancement and multi-channel object detection systems, with TensorRT inference optimization.
- Designed and implemented a Go RTSP backend, using shared memory to connect video reception, AI processing, and transmission in Python.
- Ported and verified low-light enhancement and object detection on Jetson AGX Orin, and contributed to Grade 1 GS certification of the low-light enhancement software.
- Designed a FastAPI image/video processing platform and designed and developed a Python gRPC server for B2B vision AI.

#### 3D Reconstruction & Digital Twin — DAPA R&D Project

- Coordinated technical planning and partner collaboration for a DAPA R&D project involving 3D reconstruction and digital twins using NVIDIA Omniverse and Isaac Sim.
- Developed image enhancement and object detection pipelines, and implemented an initial web integration demo of Omniverse visualization using WebRTC and provided OpenUSD samples.

## Technical Skills

- Research: Computer Vision, Low-Light Image Enhancement, Image Exposure Correction, Self-Supervised Learning, 3D Reconstruction
- Programming: Python, Go
- Deep Learning: PyTorch, TensorRT, RT-DETR, model training, inference pipelines, experiment analysis
- Vision Systems: OpenCV, GoCV, Jetson, RTSP streaming, shared memory
- AI Platforms: FastAPI, gRPC
- 3D Tools: NVIDIA Isaac Sim, NVIDIA Omniverse, OpenUSD

<!-- 3D viewer UI copy (implementation reference)
Loading 3D reconstruction…
Downloading 3D data…
Preparing the 3D view…
Download complete
Download progress: {percent}% · {received} / {total} MB
{count} points · Drag to rotate
-->
