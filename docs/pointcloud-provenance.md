# VGGT point cloud 게시 데이터 기록

## 선택한 입력

- Run: `76792ce3d6414c049bedae5152fe084e`
- 입력: `/home/dwchoo/omniverse/isaac_sim/sim_data/local_data/vggt_web/jobs/766e4f73b8cf47f98d3f5c62d128b42d/runs/76792ce3d6414c049bedae5152fe084e/pointcloud.npz`
- `run_summary.json`: `status=complete`, `point_counts.exported=453253`
- 기존 정리 조건: confidence percentile 90, 기록된 threshold `17.639276885986327`
- `transforms.json`: `world_from_vggt=identity`
- 입력 SHA-256: `92034ad03849352780485f2710a0dc810bf87131b277d170f26cc34d841c8c9b`

이 정리본은 원본 카메라와 기존 점의 검증 기준으로 사용합니다. 현재 게시 데이터는 같은 run의 저장된 depth와 RGB 이미지에서 confidence percentile 50 조건으로 다시 추출했습니다. 기존 VGGT/Isaac Sim 프로젝트와 원본 run 파일은 수정하지 않았습니다.

## 변환 결과

- 출력: [`assets/data/vggt/pointcloud.ply`](../assets/data/vggt/pointcloud.ply)
- 형식: binary little-endian PLY, 점당 15바이트(float32 XYZ + uint8 RGB)
- 점 수: **2,266,250**
- 파일 크기: **33,993,931바이트** (헤더 181바이트 + 점 데이터 33,993,750바이트)
- 출력 SHA-256: `828926997ff67fa5256745160b76c2d070ed7a6c6e483ff0268c02d28b7670c9`
- 부가 정보: [`pointcloud.json`](../assets/data/vggt/pointcloud.json)
- 변환 환경: Python 3.12 가상환경, NumPy 2.5.3, Pillow 12.3.0

실행 명령:

```sh
/tmp/homepage-viewer-venv/bin/python scripts/export_pointcloud.py \
  --source-run /home/dwchoo/omniverse/isaac_sim/sim_data/local_data/vggt_web/jobs/766e4f73b8cf47f98d3f5c62d128b42d/runs/76792ce3d6414c049bedae5152fe084e \
  --confidence-percentile 50 \
  --output assets/data/vggt/pointcloud.ply
```

변환 스크립트의 왕복 검사에서 모든 출력 XYZ·RGB의 바이트와 점 순서가 재구성 결과와 일치했습니다. 재구성 시 기존 NPZ의 453,253개 source pixel index에 해당하는 XYZ·RGB가 원본과 바이트 단위로 일치하는지 확인했습니다. 이 기존 점들은 새 데이터에도 모두 포함됩니다. 입력 파일들의 SHA-256은 변환 전후 동일하며, 관련 해시는 `pointcloud.json`의 `reconstruction.source_files_sha256`에 기록했습니다. 유효하지 않은 입력·PNG 해시 변경·depth 불일치 등을 거부하는 테스트를 포함해 17개 변환 테스트를 통과했습니다.

## 점 수를 늘린 방법

- 원본 유효점: 4,532,500개. Padding, 비정상 depth/좌표/confidence는 제외합니다.
- 최초 게시: percentile 90, 453,253점. PLY SHA-256은 `a4c466a60928afd1df8d06219dd050561c70a204778b48071758b31850fe537a`였습니다.
- 현재: percentile 50, threshold `12.386348724365234`, 2,266,250점. 임의 샘플링과 point cap은 없습니다.
- 기존 점 453,253개를 모두 유지하고 1,812,997개를 추가했습니다. 재추론이나 인공적인 점 복제는 수행하지 않았습니다.
- 원본 `predictions.npz` SHA-256: `9451e2ce67ae19de10fa1d33109fe04ead7a9b49fafbda9d6a48278ea9c567d5`

[원 프로젝트의 depth 후처리](https://github.com/dwchoo/vggt-isaac-sim/blob/main/src/vggt_runner/postprocess.py)와 [카메라 좌표 계산](https://github.com/dwchoo/vggt-isaac-sim/blob/main/src/geometry/camera.py)을 확인해 같은 방식으로 depth를 역투영했습니다. Confidence는 보정된 확률이 아닌 모델 점수입니다. 기준을 완화하면 표면 범위와 밀도가 늘지만 주변 노이즈도 늘어납니다. 원본 이미지·depth에 없는 가려진 면을 새로 생성하지는 않습니다.

## 초기 카메라와 색상

`camera_to_world_cv[0]`의 첫 입력 카메라 방향을 사용합니다. CV 좌표의 +Y는 아래, +Z는 전방이므로 `up=-R[:,1]`, `forward=R[:,2]`로 설정했습니다. 초기 forward는 대략 `[-0.0000320475, 0.00000530818, 1]`, up은 `[-0.00000412105, -1, 0.00000530804]`입니다.

전체 결과를 담기 위해 바운딩 박스 중심을 회전 중심으로 사용하고 바운딩 구와 가로·세로 시야각으로 거리를 계산합니다. 첫 카메라의 **방향**을 유지하면서 중심과 거리를 맞추므로 원본 사진의 위치·화각과 완전히 같은 투영은 아닙니다. 좌표 자체는 보존하며 크기 변경 시 현재 회전 방향을 유지합니다.

배경 `#101315`, 점 크기 2 CSS px, `sizeAttenuation=false`, FOV 45°, pixel ratio 최대 2입니다. [Three.js r185 PLYLoader](https://github.com/mrdoob/three.js/blob/r185/examples/jsm/loaders/PLYLoader.js)가 sRGB RGB를 linear 색상으로 변환하며, renderer의 출력은 sRGB입니다. 별도의 중복 색상 변환은 없습니다. r185 loader의 normalized uint8 색상 attribute에 따른 양자화는 적용되지만, 게시 PLY의 RGB 원본 바이트는 그대로입니다.

## Three.js 배포 파일

[Three.js r185](https://github.com/mrdoob/three.js/tree/r185)의 0.185.0 파일을 저장소에 포함했습니다. `PLYLoader.js`와 `OrbitControls.js`에서 bare import `from 'three'`만 `from './three.module.min.js'`로 변경했습니다. 나머지는 upstream과 바이트 단위로 일치하는지 확인했습니다. 핵심 모듈은 번들러 없이 상대 경로로 읽습니다.

[MIT 라이선스](../assets/vendor/three/LICENSE)를 함께 배포합니다.

| 파일 | 바이트 | 게시 파일 SHA-256 |
| --- | ---: | --- |
| `three.module.min.js` | 365,552 | `86bcee248b64f44bcfc23c331ae74619061957d59cab040171dcb6fb5900beb6` |
| `three.core.min.js` | 385,386 | `05b2609338c76cd65daf74f3ac515bc9a5045e1b3b33edc07d8c9bd55250fa90` |
| `PLYLoader.js` | 21,885 | `c3159e34a526617c621f6ead9eb6e9c3d96682ac6fe8d18861d721361430329d` |
| `OrbitControls.js` | 40,520 | `845c827054bda45b84ae0e9e0db4e707f75d2182af9cd88787b2cac86aeef8ef` |
| `LICENSE` | 1,081 | `8b378ebe60e2fe500158cb0ac71cb5e8b7d92953c2abcc63a0eb90499653b5bc` |
