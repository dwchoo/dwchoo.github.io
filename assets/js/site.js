(function () {
  const storageKey = "dwchoo-home-lang";
  const body = document.body;
  const buttons = Array.from(document.querySelectorAll("[data-lang-button]"));
  const translatedNodes = Array.from(document.querySelectorAll("[data-i18n-en][data-i18n-kr]"));
  const HDF_EC_RESULTS = [
    {
      dataset: "LSRW-Huawei-low",
      width: 960,
      height: 720,
      inputSrc: "assets/img/research/hdf-ec/lsrw-huawei-2049-input.jpg",
      resultSrc: "assets/img/research/hdf-ec/lsrw-huawei-2049-result.jpg",
    },
    {
      dataset: "LSRW-Nikon-low",
      width: 960,
      height: 640,
      inputSrc: "assets/img/research/hdf-ec/lsrw-nikon-3001-input.jpg",
      resultSrc: "assets/img/research/hdf-ec/lsrw-nikon-3001-result.jpg",
    },
    {
      dataset: "LSD-NEI",
      width: 1600,
      height: 1200,
      inputSrc: "assets/img/research/hdf-ec/lsd-nei-46-low-input.jpg",
      resultSrc: "assets/img/research/hdf-ec/lsd-nei-46-low-result.jpg",
    },
    {
      dataset: "LSD-U-android",
      width: 1600,
      height: 900,
      inputSrc: "assets/img/research/hdf-ec/lsd-u-android-1079-input.jpg",
      resultSrc: "assets/img/research/hdf-ec/lsd-u-android-1079-result.jpg",
    },
    {
      dataset: "LSD-DLI",
      width: 1600,
      height: 1200,
      inputSrc: "assets/img/research/hdf-ec/lsd-dli-40-low-input.jpg",
      resultSrc: "assets/img/research/hdf-ec/lsd-dli-40-low-result.jpg",
    },
    {
      dataset: "DICM",
      width: 480,
      height: 720,
      inputSrc: "assets/img/research/hdf-ec/dicm-59-input.jpg",
      resultSrc: "assets/img/research/hdf-ec/dicm-59-result.jpg",
    },
    {
      dataset: "NPE",
      width: 750,
      height: 725,
      inputSrc: "assets/img/research/hdf-ec/npe-birds-input.jpg",
      resultSrc: "assets/img/research/hdf-ec/npe-birds-result.jpg",
    },
    {
      dataset: "MSEC-P1.5",
      width: 1277,
      height: 850,
      inputSrc: "assets/img/research/hdf-ec/msec-p15-a0046-dgw-101-input.jpg",
      resultSrc: "assets/img/research/hdf-ec/msec-p15-a0046-dgw-101-result.jpg",
    },
  ];

  let currentResultIndex = 0;
  let comparePosition = 50;

  function getInitialLanguage() {
    const stored = window.localStorage.getItem(storageKey);
    if (stored === "en" || stored === "kr") {
      return stored;
    }

    return "en";
  }

  function setLanguage(language) {
    body.dataset.lang = language;
    document.documentElement.lang = language === "kr" ? "ko" : "en";
    window.localStorage.setItem(storageKey, language);

    buttons.forEach((button) => {
      const isActive = button.dataset.langButton === language;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });

    translatedNodes.forEach((node) => {
      node.textContent = language === "kr" ? node.dataset.i18nKr : node.dataset.i18nEn;
    });
  }

  function setComparePosition(value) {
    comparePosition = Number(value);
    const viewer = document.querySelector(".comparison-viewer");

    if (viewer) {
      viewer.style.setProperty("--compare-position", `${comparePosition}%`);
    }
  }

  function renderResult(index) {
    const result = HDF_EC_RESULTS[index];
    const viewer = document.querySelector(".comparison-viewer");
    const inputImage = document.querySelector("[data-input-image]");
    const resultImage = document.querySelector("[data-result-image]");
    const selectorButtons = Array.from(document.querySelectorAll("[data-sample-index]"));

    if (!result || !viewer || !inputImage || !resultImage) {
      return;
    }

    currentResultIndex = index;

    inputImage.src = result.inputSrc;
    inputImage.alt = `Input for ${result.dataset}`;
    inputImage.width = result.width;
    inputImage.height = result.height;

    resultImage.src = result.resultSrc;
    resultImage.alt = `HDF-EC result for ${result.dataset}`;
    resultImage.width = result.width;
    resultImage.height = result.height;

    selectorButtons.forEach((button) => {
      const isActive = Number(button.dataset.sampleIndex) === index;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });
  }

  function setupResultComparison() {
    const selector = document.querySelector("[data-sample-selector]");
    const range = document.querySelector("[data-comparison-range]");
    const previousButton = document.querySelector("[data-result-prev]");
    const nextButton = document.querySelector("[data-result-next]");

    if (!selector || !range || !previousButton || !nextButton) {
      return;
    }

    HDF_EC_RESULTS.forEach((result, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.sampleIndex = String(index);
      button.textContent = result.dataset;
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => renderResult(index));
      selector.appendChild(button);
    });

    range.addEventListener("input", (event) => setComparePosition(event.target.value));
    previousButton.addEventListener("click", () => {
      const nextIndex = (currentResultIndex - 1 + HDF_EC_RESULTS.length) % HDF_EC_RESULTS.length;
      renderResult(nextIndex);
    });
    nextButton.addEventListener("click", () => {
      const nextIndex = (currentResultIndex + 1) % HDF_EC_RESULTS.length;
      renderResult(nextIndex);
    });

    setComparePosition(comparePosition);
    renderResult(currentResultIndex);
  }

  buttons.forEach((button) => {
    button.addEventListener("click", () => setLanguage(button.dataset.langButton));
  });

  setupResultComparison();
  setLanguage(getInitialLanguage());
})();
