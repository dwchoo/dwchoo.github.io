# Dongwon Choo

Computer Vision Researcher & AI Engineer

I work on image exposure restoration, low-light enhancement, and self-supervised learning, with a focus on building efficient vision models that can move from research prototypes to practical deployment.

- GitHub: <https://github.com/dwchoo>
- LinkedIn: <https://www.linkedin.com/in/dwchoo1991/>

## About

I am a computer vision researcher and AI engineer specializing in image exposure restoration, low-light enhancement, and self-supervised learning. I am expected to receive my Ph.D. from the AI major in the Department of Information Convergence Engineering at Pusan National University in August 2026.

My work focuses on restoring degraded images under challenging illumination conditions while maintaining practical computational efficiency. I have experience developing deep learning models in Python and production-oriented software in Go, and I have contributed to GoCV, an OpenCV-based computer vision library for Go.

I am also interested in 3D vision and simulation with NVIDIA Isaac Sim.

## Dissertation Research

My doctoral research focuses on **unified image exposure restoration** for challenging real-world illumination conditions, including low-light, over-exposed, and backlit scenes. Instead of treating under-exposure and over-exposure as separate problems, this work reformulates them as a single exposure restoration task that aims to recover visually natural brightness, color, contrast, and structural details.

The core contribution of this research is **HDF-EC**, a Hierarchical Dual-Flow architecture designed for efficient and consistent exposure correction. The model combines a CNN-based low-level module for local texture and brightness refinement with a Transformer-based high-level module for global exposure and structural consistency. This design targets robust restoration quality across multiple exposure benchmarks while maintaining practical deployment efficiency.

## Education

- Pusan National University, B.S. in Electronics Engineering, 2010.03 - 2017.02
- Pusan National University, Ph.D. in Information Convergence Engineering, AI Major, 2018.09 - 2026.08 expected

## Experience

### InBic Inc. (startup)

AI Development Team Lead / Senior Researcher  
2023.01 - 2025.06

- Developed real-time vision AI models and operation systems.
- Developed and optimized lightweight vision AI models using PyTorch, TensorFlow, TensorRT, NVIDIA Triton, and DeepStream.
- Built high-speed video processing and real-time AI relay systems for H.264/H.265 RTSP streams using Go, OpenCV, and GoCV.
- Developed edge-device vision AI solutions using Jetson and DeepStream.

## Selected Publications

- **D. Choo**, Q. Deng, T. Park, and D. Lee, "HVR-SSLE: Hierarchical Visual Reasoning for Self-Supervised Low-Light Image Enhancement," *IEEE Access*, vol. 14, pp. 34705-34725, 2026.
- Q. Deng, **D. Choo**, H. Ji, and D. Lee, "A 5K Efficient Low-Light Enhancement Model by Estimating Increment between Dark Image and Transmission Map Based on Local Maximum Color Value Prior," *Electronics*, vol. 13, p. 1814, 2024.
- M.-j. Kim, Q. Deng, **D. Choo**, H. C. Ji, and D. Lee, "AGCSNet: High-contrast image-exposure correction with automatic illumination-map attention-based gamma and saturation correction," *ETRI Journal*, 2025.

## Projects

### VGGT-ISAAC-SIM

[VGGT-ISAAC-SIM](https://github.com/dwchoo/vggt-isaac-sim): Developed a pipeline for VGGT-based multi-view 3D reconstruction, OpenUSD export, and visualization in Isaac Sim.

Demo source: the [official VGGT Kitchen example](https://github.com/facebookresearch/vggt/tree/main/examples/kitchen). The 25 source images were duplicated to form a 50-image validation run; the viewer shows the final 500,000-point result.

### HVR-SSLE

[HVR-SSLE](https://github.com/dwchoo/HVR-SSLE) is the official PyTorch implementation of the HVR-SSLE paper, which proposes a compact self-supervised low-light image enhancement model. The repository includes training and inference pipelines, dataset configuration, checkpoint handling, and analysis resources for reproducible research.

### GoCV Contribution

Contributed to GoCV, a Go package for computer vision using OpenCV. This reflects my interest in connecting computer vision research with practical software engineering.

## Skills

- Research: Computer Vision, Low-Light Image Enhancement, Image Exposure Correction, Self-Supervised Learning
- Programming: Python, Go
- Deep Learning: PyTorch, TensorFlow, TensorRT, model training, inference pipelines, experiment analysis
- Vision Systems: OpenCV, GoCV, NVIDIA Triton, Jetson, DeepStream, RTSP streaming, image restoration workflows

<!-- 3D viewer UI copy (implementation reference)
Loading 3D reconstruction…
Downloading 3D data…
Preparing the 3D view…
Download complete
Download progress: {percent}% · {received} / {total} MB
{count} points · Drag to rotate
-->
