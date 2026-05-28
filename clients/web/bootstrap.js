(function () {
  const cacheBust = Date.now();

  function loadScript(src, { type = "text/javascript", optional = false } = {}) {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = src;
      script.type = type;
      script.onload = () => resolve();
      script.onerror = () => {
        if (optional) {
          resolve();
        } else {
          reject(new Error(`Failed to load script: ${src}`));
        }
      };
      document.body.appendChild(script);
    });
  }

  (async () => {
    await loadScript(`./version.js?${cacheBust}`, { optional: true });
    await loadScript(`./config.sample.js?${cacheBust}`, { optional: true });
    await loadScript(`./config.js?${cacheBust}`, { optional: true });
    await loadScript(`./libs/marked.min.js?${cacheBust}`, { optional: true });
    await loadScript(`./libs/purify.min.js?${cacheBust}`, { optional: true });

    const version = String(window.PLAYPALACE_WEB_VERSION || "2026.02.08.1").trim();
    await loadScript(`./app.js?v=${encodeURIComponent(version)}&${cacheBust}`, {
      type: "module",
    });
  })().catch((error) => {
    console.error(error);
  });
})();
