import * as THREE from "../vendor/three/three.module.min.js";
import { PLYLoader } from "../vendor/three/PLYLoader.js";
import { OrbitControls } from "../vendor/three/OrbitControls.js";

const assetURL = new URL("../data/vggt/pointcloud.ply", import.meta.url);
const manifestURL = new URL("../data/vggt/pointcloud.json", import.meta.url);
const messages = {
  en: {
    loading: "Loading 3D reconstruction…",
    ready: "{count} points · Drag to rotate",
    file: "The 3D data could not be loaded. Please reload the page.",
    webgl: "3D graphics are unavailable. Please use a browser with WebGL enabled and reload.",
    canvas: "VGGT 3D reconstruction. Drag with the left mouse button or one finger to rotate.",
  },
  kr: {
    loading: "3D 재구성을 불러오는 중…",
    ready: "{count}점 · 드래그하여 회전",
    file: "3D 데이터를 불러올 수 없습니다. 페이지를 새로고침해 주세요.",
    webgl: "3D 그래픽을 사용할 수 없습니다. WebGL이 활성화된 브라우저에서 새로고침해 주세요.",
    canvas: "VGGT 3D 재구성. 왼쪽 마우스 버튼 또는 한 손가락으로 드래그하여 회전합니다.",
  },
};

export function createPointcloudViewer(host, { language = "en", active = true } = {}) {
  const status = host.querySelector("[data-viewer-status]");
  const request = new AbortController();
  let state = "loading";
  let disposed = false;
  let inView = false;
  let frame = 0;
  let renderer, controls, geometry, material, camera, scene;
  let radius = 0;
  let width = 0;
  let height = 0;
  let pixelRatio = 0;
  let pointCount = 0;

  function setLanguage(value) {
    language = value === "kr" ? "kr" : "en";
    status.textContent = messages[language][state].replace("{count}", pointCount.toLocaleString("en-US"));
    host.dataset.viewerState = state;
    host.setAttribute("aria-busy", String(state === "loading"));
    renderer?.domElement.setAttribute("aria-label", messages[language].canvas);
  }

  function canRender() {
    return !disposed && active && inView && !document.hidden && state === "ready";
  }

  function invalidate() {
    if (!canRender() || frame) return;
    frame = requestAnimationFrame(() => {
      frame = 0;
      if (canRender()) renderer.render(scene, camera);
    });
  }

  function fit() {
    if (!geometry || !host.clientWidth || !host.clientHeight || !active) return;
    const nextWidth = host.clientWidth;
    const nextHeight = host.clientHeight;
    const nextRatio = Math.min(window.devicePixelRatio || 1, 2);
    if (nextWidth === width && nextHeight === height && nextRatio === pixelRatio) return;
    width = nextWidth;
    height = nextHeight;
    pixelRatio = nextRatio;
    renderer.setPixelRatio(pixelRatio);
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    const halfVertical = THREE.MathUtils.degToRad(camera.fov / 2);
    const halfHorizontal = Math.atan(Math.tan(halfVertical) * camera.aspect);
    const distance = radius * 1.08 / Math.sin(Math.min(halfVertical, halfHorizontal));
    const direction = camera.position.clone().sub(controls.target).normalize();
    camera.position.copy(controls.target).addScaledVector(direction, distance);
    camera.near = Math.max(radius * 0.001, distance - radius * 1.2);
    camera.far = distance + radius * 1.2;
    camera.updateProjectionMatrix();
    controls.update();
    invalidate();
  }

  function syncActivity() {
    if (disposed) return;
    if (controls) controls.enabled = canRender();
    if (!canRender()) {
      cancelAnimationFrame(frame);
      frame = 0;
    } else {
      fit();
      invalidate();
    }
  }

  function setActive(value) {
    active = Boolean(value);
    syncActivity();
  }

  function releaseGraphics() {
    controls?.dispose();
    geometry?.dispose();
    material?.dispose();
    if (renderer) {
      renderer.domElement.removeEventListener("webglcontextlost", onContextLost);
      renderer.dispose();
      renderer.forceContextLoss();
      renderer.domElement.remove();
    }
    renderer = controls = geometry = material = camera = scene = null;
  }

  function fail(reason) {
    if (disposed) return;
    state = reason;
    request.abort();
    syncActivity();
    releaseGraphics();
    setLanguage(language);
  }

  function onContextLost(event) {
    event.preventDefault();
    fail("webgl");
  }

  const resizeObserver = new ResizeObserver(() => {
    if (canRender()) fit();
  });
  resizeObserver.observe(host);
  const intersectionObserver = new IntersectionObserver(([entry]) => {
    inView = entry.isIntersecting;
    syncActivity();
  });
  intersectionObserver.observe(host);
  const removalObserver = new MutationObserver(() => {
    if (!host.isConnected) dispose();
  });
  removalObserver.observe(document.body, { childList: true, subtree: true });
  document.addEventListener("visibilitychange", syncActivity);
  window.addEventListener("resize", syncActivity);

  function dispose() {
    if (disposed) return;
    disposed = true;
    request.abort();
    cancelAnimationFrame(frame);
    resizeObserver.disconnect();
    intersectionObserver.disconnect();
    removalObserver.disconnect();
    document.removeEventListener("visibilitychange", syncActivity);
    window.removeEventListener("resize", syncActivity);
    releaseGraphics();
  }

  async function load() {
    try {
      renderer = new THREE.WebGLRenderer({ antialias: false, alpha: false });
      renderer.setClearColor("#101315");
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      renderer.domElement.setAttribute("role", "img");
      renderer.domElement.addEventListener("webglcontextlost", onContextLost);
      host.prepend(renderer.domElement);
    } catch {
      fail("webgl");
      return;
    }
    setLanguage(language);
    try {
      const [dataResponse, manifestResponse] = await Promise.all([
        fetch(assetURL, { signal: request.signal }),
        fetch(manifestURL, { signal: request.signal }),
      ]);
      if (!dataResponse.ok || !manifestResponse.ok) throw new Error("Asset request failed");
      const [buffer, manifest] = await Promise.all([dataResponse.arrayBuffer(), manifestResponse.json()]);
      if (disposed || state !== "loading") return;
      if (buffer.byteLength !== manifest.byte_length || !Number.isSafeInteger(manifest.point_count) || manifest.point_count <= 0) {
        throw new Error("Unexpected point cloud size");
      }
      if (globalThis.crypto?.subtle) {
        const digest = await crypto.subtle.digest("SHA-256", buffer);
        const hash = Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
        if (hash !== manifest.ply_sha256) throw new Error("Point cloud checksum mismatch");
      }
      if (disposed || state !== "loading") return;
      geometry = new PLYLoader().parse(buffer);
      const positions = geometry.getAttribute("position");
      const colors = geometry.getAttribute("color");
      if (positions?.count !== manifest.point_count || colors?.count !== positions.count ||
          !positions.array.every(Number.isFinite) || !colors.array.every(Number.isFinite)) {
        throw new Error("Invalid point cloud");
      }
      pointCount = positions.count;
      geometry.computeBoundingBox();
      geometry.computeBoundingSphere();
      radius = geometry.boundingSphere.radius;
      if (!Number.isFinite(radius) || radius <= 0) throw new Error("Invalid bounds");
      scene = new THREE.Scene();
      // PLYLoader converts sRGB vertex colors to linear once; the renderer outputs sRGB.
      material = new THREE.PointsMaterial({ size: 2, sizeAttenuation: false, vertexColors: true });
      scene.add(new THREE.Points(geometry, material));
      camera = new THREE.PerspectiveCamera(45, 1, 0.01, 1000);
      camera.up.fromArray(manifest.initial_camera.up).normalize();
      const center = geometry.boundingBox.getCenter(new THREE.Vector3());
      camera.position.copy(center).sub(new THREE.Vector3().fromArray(manifest.initial_camera.forward).normalize());
      camera.lookAt(center);
      controls = new OrbitControls(camera, renderer.domElement);
      controls.target.copy(center);
      controls.enableZoom = false;
      controls.enablePan = false;
      controls.enableDamping = false;
      controls.autoRotate = false;
      controls.mouseButtons = { LEFT: THREE.MOUSE.ROTATE, MIDDLE: null, RIGHT: null };
      controls.touches = { ONE: THREE.TOUCH.ROTATE, TWO: null };
      controls.addEventListener("change", invalidate);
      state = "ready";
      setLanguage(language);
      syncActivity();
    } catch {
      if (!disposed && state === "loading") fail("file");
    }
  }

  setLanguage(language);
  void load();
  return { setActive, setLanguage, dispose };
}
