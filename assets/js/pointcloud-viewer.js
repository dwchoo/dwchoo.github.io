import * as THREE from "../vendor/three/three.module.min.js";
import { PLYLoader } from "../vendor/three/PLYLoader.js";
import { OrbitControls } from "../vendor/three/OrbitControls.js";
import { reconstruction as manifest } from "./reconstruction-data.js?v=kitchen-500k-1";

const assetURL = new URL("../data/vggt/reconstruction.ply", import.meta.url);
const messages = {
  en: {
    loading: "Loading 3D reconstruction…",
    downloading: "Downloading 3D data…",
    preparing: "Preparing the 3D view…",
    downloaded: "Download complete",
    ready: "{count} points · Drag to rotate",
    file: "The 3D data could not be loaded. Please reload the page.",
    webgl: "3D graphics are unavailable. Please use a browser with WebGL enabled and reload.",
    canvas: "VGGT 3D reconstruction. Drag with the left mouse button or one finger to rotate.",
  },
  kr: {
    loading: "3D 재구성을 불러오는 중…",
    downloading: "3D 데이터를 다운로드하는 중…",
    preparing: "3D 화면을 준비하는 중…",
    downloaded: "다운로드 완료",
    ready: "{count}점 · 드래그하여 회전",
    file: "3D 데이터를 불러올 수 없습니다. 페이지를 새로고침해 주세요.",
    webgl: "3D 그래픽을 사용할 수 없습니다. WebGL이 활성화된 브라우저에서 새로고침해 주세요.",
    canvas: "VGGT 3D 재구성. 왼쪽 마우스 버튼 또는 한 손가락으로 드래그하여 회전합니다.",
  },
};

export function createPointcloudViewer(host, { language = "en", active = true } = {}) {
  const status = host.querySelector("[data-viewer-status]");
  const progress = host.querySelector("[data-viewer-progress]");
  const progressBar = host.querySelector("[data-viewer-progress-bar]");
  const progressText = host.querySelector("[data-viewer-progress-text]");
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
  let receivedBytes = 0;
  let totalBytes = 0;
  let lastPercent = -1;

  function isLoading() {
    return ["loading", "downloading", "preparing"].includes(state);
  }

  function updateProgress() {
    if (disposed) return;
    progress.hidden = !isLoading();
    if (!totalBytes) {
      progressBar.removeAttribute("value");
      progressBar.removeAttribute("aria-valuetext");
      progressText.textContent = "";
      return;
    }
    const percent = Math.floor(receivedBytes / totalBytes * 100);
    const amount = `${(receivedBytes / 1e6).toFixed(1)} / ${(totalBytes / 1e6).toFixed(1)} MB`;
    progressBar.value = percent;
    progressText.textContent = state === "preparing"
      ? `${messages[language].downloaded} · ${amount}`
      : `${percent}% · ${amount}`;
    progressBar.setAttribute("aria-valuetext", progressText.textContent);
    lastPercent = percent;
  }

  function setLanguage(value) {
    language = value === "kr" ? "kr" : "en";
    status.textContent = messages[language][state].replace("{count}", pointCount.toLocaleString("en-US"));
    host.dataset.viewerState = state;
    host.setAttribute("aria-busy", String(isLoading()));
    renderer?.domElement.setAttribute("aria-label", messages[language].canvas);
    updateProgress();
  }

  async function download(response) {
    state = "downloading";
    setLanguage(language);
    if (!response.body) {
      const buffer = await response.arrayBuffer();
      receivedBytes = buffer.byteLength;
      return buffer;
    }
    const bytes = new Uint8Array(totalBytes);
    const reader = response.body.getReader();
    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        if (disposed || request.signal.aborted) return null;
        if (receivedBytes + value.byteLength > totalBytes) throw new Error("Unexpected data length");
        bytes.set(value, receivedBytes);
        receivedBytes += value.byteLength;
        if (Math.floor(receivedBytes / totalBytes * 100) !== lastPercent) updateProgress();
      }
      if (receivedBytes !== totalBytes) throw new Error("Incomplete point cloud download");
      return bytes.buffer;
    } finally {
      // Cancel an unfinished response on abort/error, then release its stream lock.
      try { await reader.cancel(); } catch { /* Fetch may already have been aborted. */ }
      reader.releaseLock();
    }
  }

  function showPreparation() {
    state = "preparing";
    setLanguage(language);
    // Allow the browser to paint this phase before synchronous PLY parsing.
    return new Promise((resolve) => {
      const finish = () => {
        clearTimeout(timer);
        request.signal.removeEventListener("abort", finish);
        resolve();
      };
      const timer = setTimeout(finish, 32);
      request.signal.addEventListener("abort", finish, { once: true });
      if (request.signal.aborted) finish();
    });
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
      if (disposed || !isLoading()) return;
      if (!Number.isSafeInteger(manifest.byte_length) || manifest.byte_length <= 0 ||
          !Number.isSafeInteger(manifest.point_count) || manifest.point_count <= 0) {
        throw new Error("Invalid point cloud manifest");
      }
      // Fetch streams decoded bytes; use the PLY size, not a compressed Content-Length.
      totalBytes = manifest.byte_length;
      const dataResponse = await fetch(assetURL, { signal: request.signal });
      if (!dataResponse.ok) throw new Error("Asset request failed");
      const buffer = await download(dataResponse);
      if (disposed || !isLoading()) return;
      if (buffer.byteLength !== totalBytes) throw new Error("Unexpected point cloud size");
      await showPreparation();
      if (disposed || !isLoading()) return;
      if (globalThis.crypto?.subtle) {
        const digest = await crypto.subtle.digest("SHA-256", buffer);
        const hash = Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
        if (hash !== manifest.ply_sha256) throw new Error("Point cloud checksum mismatch");
      }
      if (disposed || !isLoading()) return;
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
      if (!disposed && isLoading()) fail("file");
    }
  }

  setLanguage(language);
  void load();
  return { setActive, setLanguage, dispose };
}
