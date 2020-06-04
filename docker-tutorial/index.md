# Docker tutorial
---
## Docker install
* ### Install Docker on Windows 10
  ['도커 처음 사용자를 위한 윈도우 도커 설치 및 실행하기'](https://steemit.com/kr/@mystarlight/docker)

* ### Install Docker on MAC
  공식 홈페이지에서 **Docker Desktop for mac** 다운 및 설치  
  [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
  
* ### Install Docker on Ubuntu
  ```bash
  $ sudo apt-get update
  $ sudo apt-get install docker-ce docker-ce-cli containerd.io
  ```
---
## Docker, Container, Image
![Docker](./image/what-is-container.png)
* ### Docker
도커는 **컨테이너 기반의 가상호 플랫폼**이다. 이는 Virtual machine으로 OS를 구동하는 것과는 차이가 있다.  
![Docker vs VM](./image/containerized-and-vm-transparent-bg.png)
도커는 Host OS kernel을 이용하여 여러개의 Application을 구동하는 반면에 VM은 Hypervisor를 활용하여 Guest OS를 올리고 그 위에 Application을 구동한다.
