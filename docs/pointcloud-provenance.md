# VGGT Kitchen 게시 데이터 기록

## 선택한 최종 결과

- Job: `479b8f0c6112472ebd8eb75062d83e2b`
- Run: `4d342425366e4788ae571c034487f0c2`
- 입력: `/home/dwchoo/omniverse/isaac_sim/sim_data/local_data/vggt_web/jobs/479b8f0c6112472ebd8eb75062d83e2b/runs/4d342425366e4788ae571c034487f0c2/pointcloud.npz`
- 완료 상태: `status=complete`, 기록된 exported 점 수 `500000`
- 웹앱에서 적용한 조건: confidence percentile 50, threshold `12.92031192779541`, point cap `500000`
- 좌표: `world_from_vggt=identity`, scale은 상대값
- NPZ SHA-256: `a0b6747acdfdf9400ca9ecdcf083856f4ba131ef5c941ee159b97e5acb61f790`

사용자가 선택한 최종 NPZ를 그대로 변환했습니다. 추가 필터링, 점 감소, 점 복제, 재추론, 메시 생성은 수행하지 않았습니다. 원본 run은 수정하지 않았습니다.

## 출처

[facebookresearch/vggt의 공식 Kitchen 예제](https://github.com/facebookresearch/vggt/tree/main/examples/kitchen)를 사용한 검증 결과입니다. 공식 `examples/kitchen/images` 디렉터리에 이미지 25장이 있는 것을 확인했습니다. 입력 manifest의 50개 항목은 원본 사진 SHA-256 기준으로 25종이며, 각각 정확히 두 번씩 나타납니다.

따라서 원본 사진 25장을 복제해 입력 50장으로 실행한 결과입니다. 원본 장면의 독립적인 촬영이나 서로 다른 50개 시점의 수집을 수행했다는 의미가 아닙니다. 홈페이지 영문·한글의 결과 캡션과 프로젝트 설명에도 이 출처를 명시했습니다.

## 변환 및 게시 파일

- 데이터: [`reconstruction.ply`](../assets/data/vggt/reconstruction.ply)
- 형식: binary little-endian, float32 XYZ + uint8 RGB, 점당 15바이트
- 점 수: **500,000**
- 파일 크기: **7,500,180바이트** (헤더 180 + 점 데이터 7,500,000)
- PLY SHA-256: `101d4de72c5bec2247e6628c1bf6acc7574d6069af99b09d818ce4b357ff540a`
- 뷰어 설정: [`reconstruction-data.js`](../assets/js/reconstruction-data.js)에 파일 크기·해시·점 수·첫 카메라 방향 기록
- 환경: Python 3.12 가상환경, NumPy 2.5.3

```sh
/tmp/homepage-viewer-venv/bin/python scripts/export_pointcloud.py \
  --source-run /home/dwchoo/omniverse/isaac_sim/sim_data/local_data/vggt_web/jobs/479b8f0c6112472ebd8eb75062d83e2b/runs/4d342425366e4788ae571c034487f0c2 \
  --output assets/data/vggt/reconstruction.ply \
  --metadata-output assets/js/reconstruction-data.js
```

`assets/data/vggt/`에는 `reconstruction.ply`만 있습니다. 원본 사진, `pointcloud.npz`, 약 244 MB의 `predictions.npz`, USD 파일은 홈페이지 저장소에 복사하지 않았습니다. 변환에는 최종 NPZ와 run 상태·좌표 정보만 사용했습니다.

변환기의 왕복 검사와 별도 `numpy.frombuffer` 검사에서 500,000행 전체 XYZ·RGB의 바이트와 순서가 원본과 일치했습니다. 원본 NPZ 해시도 변환 전후 동일했습니다. 입력 오류와 JS 설정 출력 보호를 포함해 13개 변환 테스트를 통과했습니다.

## 카메라·색상·로딩

첫 입력의 `camera_to_world_cv[0]`에서 `up=-R[:,1]`, `forward=R[:,2]`를 사용합니다. Forward는 대략 `[-0.0000237725, 0.00000324199, 1]`, up은 `[0.0000357564, -1, 0.00000324284]`입니다. 원본 좌표를 회전시키지 않고 카메라 방향만 맞췄습니다.

바운딩 박스 중심을 회전 중심으로 두고 바운딩 구와 시야각으로 전체 결과를 담는 거리를 계산합니다. FOV 45°, 배경 `#101315`, 점 크기 2 CSS px, `sizeAttenuation=false`, pixel ratio 최대 2입니다. 크기 변경 시 현재 회전 방향을 유지합니다.

[PLYLoader r185](https://github.com/mrdoob/three.js/blob/r185/examples/jsm/loaders/PLYLoader.js)가 sRGB 색상을 linear로 한 번 변환하고 renderer가 sRGB로 출력합니다. Loader의 normalized uint8 색상 attribute에 따른 양자화는 있지만 PLY의 RGB 바이트는 원본 그대로입니다.

로딩 UI는 실제 다운로드 바이트로 진행률을 표시하고, 다운로드 후 3D 준비 단계를 별도로 안내합니다. gzip 응답에서는 압축된 Content-Length 대신 원래 PLY 크기를 기준으로 계산합니다. 파일은 한 번만 요청하며, 파싱 결과를 탭·언어 전환에 재사용합니다.

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
