function isAbsoluteUrl(path) {
  return /^https?:\/\//i.test(path);
}

function isCrossOriginUrl(url) {
  try {
    const target = new URL(url, window.location.href);
    return target.origin !== window.location.origin;
  } catch {
    return false;
  }
}

function createAudioElement(url) {
  const audio = new Audio();
  if (isCrossOriginUrl(url)) {
    // Required for Web Audio processing of cross-origin media.
    audio.crossOrigin = "anonymous";
  }
  audio.src = url;
  return audio;
}

function toSoundUrl(name, soundBaseUrl) {
  if (!name) {
    return "";
  }
  if (isAbsoluteUrl(name) || name.startsWith("/")) {
    return name;
  }
  const base = String(soundBaseUrl || "./sounds").replace(/\/+$/, "");
  return `${base}/${name}`;
}

export function createAudioEngine(options = {}) {
  const soundBaseUrl = options.soundBaseUrl || "./sounds";
  const AudioCtx = window.AudioContext || window.webkitAudioContext;
  const context = AudioCtx ? new AudioCtx() : null;
  const MAX_EFFECT_START_DELAY_MS = 1500;
  const MAX_EFFECT_CACHE_ENTRIES = 128;
  const MAX_PENDING_EFFECTS = 24;
  const PRELOAD_CONCURRENCY = 4;
  const DEFAULT_PRELOAD_EFFECTS = [
    "menuclick.ogg",
    "menuenter.ogg",
    "chat.ogg",
    "chatlocal.ogg",
    "typing1.ogg",
    "typing2.ogg",
    "typing3.ogg",
    "typing4.ogg",
    "mention.ogg",
    "game_cards/play1.ogg",
    "game_cards/play2.ogg",
    "game_cards/play3.ogg",
    "game_cards/play4.ogg",
    "game_cards/draw1.ogg",
    "game_cards/draw2.ogg",
    "game_cards/draw3.ogg",
    "game_cards/draw4.ogg",
    "game_cards/discard1.ogg",
    "game_cards/discard2.ogg",
    "game_cards/discard3.ogg",
    "game_cards/shuffle1.ogg",
    "game_cards/shuffle2.ogg",
    "game_cards/shuffle3.ogg",
    "game_milebymile/25miles1.ogg",
    "game_milebymile/25miles2.ogg",
    "game_milebymile/50miles1.ogg",
    "game_milebymile/50miles2.ogg",
    "game_milebymile/50miles3.ogg",
    "game_milebymile/75miles1.ogg",
    "game_milebymile/75miles2.ogg",
    "game_milebymile/75miles3.ogg",
    "game_milebymile/100miles1.ogg",
    "game_milebymile/100miles2.ogg",
    "game_milebymile/100miles3.ogg",
    "game_milebymile/200miles1.ogg",
    "game_milebymile/200miles2.ogg",
    "game_milebymile/200miles3.ogg",
    "game_milebymile/crash1.ogg",
    "game_milebymile/crash2.ogg",
    "game_milebymile/drivingace.ogg",
    "game_milebymile/extratank1.ogg",
    "game_milebymile/extratank2.ogg",
    "game_milebymile/flat.ogg",
    "game_milebymile/gas.ogg",
    "game_milebymile/greenlight1.ogg",
    "game_milebymile/greenlight2.ogg",
    "game_milebymile/greenlight3.ogg",
    "game_milebymile/outofgas.ogg",
    "game_milebymile/punctureproof.ogg",
    "game_milebymile/repair1.ogg",
    "game_milebymile/repair2.ogg",
    "game_milebymile/rightofway.ogg",
    "game_milebymile/sparetyre.ogg",
    "game_milebymile/speedlimit.ogg",
    "game_milebymile/speedlimitend.ogg",
    "game_milebymile/stop.ogg",
    "game_milebymile/winround.ogg",
  ];

  let effectsGain = null;
  let musicGain = null;
  let ambienceGain = null;
  let currentMusic = null;
  let currentMusicNodes = null;
  let currentMusicName = "";
  let currentMusicLooping = true;
  let pendingMusicPacket = null;
  let currentAmbience = null;
  let currentAmbienceNodes = null;
  let currentAmbienceLoop = null;
  let currentAmbienceLoopNodes = null;
  let currentAmbienceLoopName = "";
  let pendingAmbiencePacket = null;
  const pendingEffectPackets = [];
  const activeEffects = new Map();
  const activeBufferEffects = new Set();
  const effectBufferCache = new Map();
  const preloadQueue = [];
  const preloadQueued = new Set();
  let activePreloads = 0;
  let muted = false;

  if (context) {
    effectsGain = context.createGain();
    musicGain = context.createGain();
    ambienceGain = context.createGain();

    effectsGain.gain.value = 1.0;
    musicGain.gain.value = 0.2;
    ambienceGain.gain.value = 1.0;

    effectsGain.connect(context.destination);
    musicGain.connect(context.destination);
    ambienceGain.connect(context.destination);
  }

  async function unlock() {
    if (!context) {
      retryPendingPlayback();
      return false;
    }
    if (context.state !== "running") {
      await context.resume();
    }
    preloadEffects(DEFAULT_PRELOAD_EFFECTS);
    retryPendingPlayback();
    return context.state === "running";
  }

  function safePlay(audio, { onRejected } = {}) {
    audio.muted = muted;
    try {
      const maybePromise = audio.play();
      if (maybePromise && typeof maybePromise.catch === "function") {
        maybePromise.catch(() => {
          if (onRejected) {
            onRejected();
          }
        });
      }
    } catch {
      if (onRejected) {
        onRejected();
      }
    }
  }

  function connectElement(audio, gainNode, panValue = 0, url = "") {
    if (!context || !gainNode) {
      return null;
    }

    if (isCrossOriginUrl(url)) {
      // Cross-origin media can be silenced by Web Audio without CORS;
      // let the element play directly as a fallback.
      return null;
    }

    try {
      const source = context.createMediaElementSource(audio);
      if (typeof context.createStereoPanner === "function") {
        const panner = context.createStereoPanner();
        panner.pan.value = Math.max(-1, Math.min(1, panValue));
        source.connect(panner);
        panner.connect(gainNode);
        return { source, panner };
      }
      source.connect(gainNode);
      return { source, panner: null };
    } catch {
      // Fallback to direct element playback if node creation fails.
      return null;
    }
  }

  function disconnectNodes(nodes) {
    if (!nodes) return;
    try { nodes.source.disconnect(); } catch { /* already disconnected */ }
    if (nodes.panner) {
      try { nodes.panner.disconnect(); } catch { /* already disconnected */ }
    }
  }

  function canUseBufferedEffect(url) {
    return Boolean(
      context
      && effectsGain
      && typeof fetch === "function"
      && !isCrossOriginUrl(url)
    );
  }

  function rememberEffectCacheUse(url, entry) {
    effectBufferCache.delete(url);
    effectBufferCache.set(url, entry);
    while (effectBufferCache.size > MAX_EFFECT_CACHE_ENTRIES) {
      const oldestUrl = effectBufferCache.keys().next().value;
      effectBufferCache.delete(oldestUrl);
    }
  }

  function decodeAudioBuffer(arrayBuffer) {
    if (!context) {
      return Promise.reject(new Error("Audio context unavailable"));
    }
    return new Promise((resolve, reject) => {
      let settled = false;
      const finish = (callback, value) => {
        if (settled) {
          return;
        }
        settled = true;
        callback(value);
      };

      try {
        const maybePromise = context.decodeAudioData(
          arrayBuffer.slice(0),
          (buffer) => finish(resolve, buffer),
          (error) => finish(reject, error)
        );
        if (maybePromise && typeof maybePromise.then === "function") {
          maybePromise.then(
            (buffer) => finish(resolve, buffer),
            (error) => finish(reject, error)
          );
        }
      } catch (error) {
        finish(reject, error);
      }
    });
  }

  function loadEffectBuffer(url) {
    const cached = effectBufferCache.get(url);
    if (cached) {
      rememberEffectCacheUse(url, cached);
      return cached.promise;
    }

    const entry = {
      promise: fetch(url, { cache: "force-cache" })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`Sound fetch failed: ${response.status}`);
          }
          return response.arrayBuffer();
        })
        .then((arrayBuffer) => decodeAudioBuffer(arrayBuffer)),
    };
    rememberEffectCacheUse(url, entry);
    return entry.promise;
  }

  function queueEffectPreload(name) {
    const url = toSoundUrl(name, soundBaseUrl);
    if (!url || !canUseBufferedEffect(url) || preloadQueued.has(url) || effectBufferCache.has(url)) {
      return;
    }
    preloadQueued.add(url);
    preloadQueue.push(url);
    pumpEffectPreloads();
  }

  function pumpEffectPreloads() {
    while (activePreloads < PRELOAD_CONCURRENCY && preloadQueue.length > 0) {
      const url = preloadQueue.shift();
      activePreloads += 1;
      loadEffectBuffer(url)
        .catch(() => {
          effectBufferCache.delete(url);
          preloadQueued.delete(url);
        })
        .finally(() => {
          activePreloads -= 1;
          pumpEffectPreloads();
        });
    }
  }

  function preloadEffects(names = []) {
    for (const name of names) {
      queueEffectPreload(name);
    }
  }

  function stopBufferEffect(effect) {
    try { effect.source.stop(); } catch { /* already stopped */ }
    try { effect.source.disconnect(); } catch { /* already disconnected */ }
    try { effect.gain.disconnect(); } catch { /* already disconnected */ }
    if (effect.panner) {
      try { effect.panner.disconnect(); } catch { /* already disconnected */ }
    }
    activeBufferEffects.delete(effect);
  }

  function startBufferedEffect(buffer, packet, queuedAtMs) {
    if (!context || !effectsGain || muted) {
      return;
    }
    if (performance.now() - queuedAtMs > MAX_EFFECT_START_DELAY_MS) {
      return;
    }

    const source = context.createBufferSource();
    source.buffer = buffer;
    source.playbackRate.value = Math.max(0.5, Math.min(2, (packet.pitch ?? 100) / 100));

    const gain = context.createGain();
    const volume = Math.max(0, Math.min(1, (packet.volume ?? 100) / 100));
    gain.gain.value = muted ? 0 : volume;

    let panner = null;
    if (typeof context.createStereoPanner === "function") {
      panner = context.createStereoPanner();
      panner.pan.value = Math.max(-1, Math.min(1, (packet.pan ?? 0) / 100));
      source.connect(panner);
      panner.connect(gain);
    } else {
      source.connect(gain);
    }
    gain.connect(effectsGain);

    const effect = { source, gain, panner, volume };
    activeBufferEffects.add(effect);
    if (typeof source.addEventListener === "function") {
      source.addEventListener("ended", () => stopBufferEffect(effect), { once: true });
    } else {
      source.onended = () => stopBufferEffect(effect);
    }
    try {
      source.start(0);
    } catch {
      stopBufferEffect(effect);
    }
  }

  function queuePendingEffect(packet) {
    if (pendingEffectPackets.length >= MAX_PENDING_EFFECTS) {
      pendingEffectPackets.shift();
    }
    pendingEffectPackets.push({
      name: packet.name || packet.sound || "",
      volume: packet.volume ?? 100,
      pan: packet.pan ?? 0,
      pitch: packet.pitch ?? 100,
    });
  }

  function playSoundWithElement(packet, url, name) {
    const audio = createAudioElement(url);
    audio.muted = muted;
    audio.preload = "auto";
    audio.volume = Math.max(0, Math.min(1, (packet.volume ?? 100) / 100));
    audio.playbackRate = Math.max(0.5, Math.min(2, (packet.pitch ?? 100) / 100));

    try {
      const nodes = connectElement(audio, effectsGain, (packet.pan ?? 0) / 100, url);
      if (!nodes && effectsGain) {
        audio.volume *= effectsGain.gain.value;
      }
      activeEffects.set(audio, nodes);
      const cleanup = () => {
        activeEffects.delete(audio);
        disconnectNodes(nodes);
      };
      audio.addEventListener("ended", cleanup);
      audio.addEventListener("error", cleanup);
      safePlay(audio, {
        onRejected: () => {
          cleanup();
          queuePendingEffect({
            name,
            volume: packet.volume ?? 100,
            pan: packet.pan ?? 0,
            pitch: packet.pitch ?? 100,
          });
        },
      });
    } catch {
      // Ignore autoplay/stream failures before unlock.
    }
  }

  function playSound(packet) {
    const name = packet.name || packet.sound || "";
    const url = toSoundUrl(name, soundBaseUrl);
    if (!url) {
      return;
    }

    if (canUseBufferedEffect(url)) {
      if (context.state !== "running") {
        queuePendingEffect(packet);
        queueEffectPreload(name);
        return;
      }
      const queuedAtMs = performance.now();
      loadEffectBuffer(url)
        .then((buffer) => {
          startBufferedEffect(buffer, packet, queuedAtMs);
        })
        .catch(() => {
          effectBufferCache.delete(url);
          playSoundWithElement(packet, url, name);
        });
      return;
    }

    playSoundWithElement(packet, url, name);
  }

  if (context) {
    setTimeout(() => {
      preloadEffects([
        "menuclick.ogg",
        "menuenter.ogg",
        "chat.ogg",
        "chatlocal.ogg",
        "game_cards/play1.ogg",
        "game_cards/play2.ogg",
        "game_cards/play3.ogg",
        "game_cards/play4.ogg",
        "game_cards/draw1.ogg",
        "game_cards/draw2.ogg",
        "game_cards/draw3.ogg",
        "game_cards/draw4.ogg",
      ]);
    }, 0);
  }

  function playMusic(packet) {
    const name = packet.name || packet.music || "";
    const url = toSoundUrl(name, soundBaseUrl);
    if (!url) {
      return;
    }
    const looping = packet.looping ?? true;

    // Match desktop behavior: don't restart music if the same track is already active.
    if (currentMusic && currentMusicName === name && currentMusicLooping === looping) {
      if (currentMusic.paused) {
        safePlay(currentMusic, {
          onRejected: () => {
            pendingMusicPacket = { name, looping };
          },
        });
      }
      return;
    }

    stopMusic();

    const audio = createAudioElement(url);
    audio.muted = muted;
    audio.preload = "auto";
    audio.loop = looping;
    audio.volume = 1.0;

    try {
      const nodes = connectElement(audio, musicGain, 0, url);
      if (!nodes && musicGain) {
        audio.volume *= musicGain.gain.value;
      }
      currentMusic = audio;
      currentMusicNodes = nodes;
      currentMusicName = name;
      currentMusicLooping = looping;
      pendingMusicPacket = null;
      safePlay(audio, {
        onRejected: () => {
          pendingMusicPacket = { name, looping };
        },
      });
    } catch {
      currentMusic = audio;
      currentMusicNodes = null;
      currentMusicName = name;
      currentMusicLooping = looping;
      pendingMusicPacket = { name, looping };
    }
  }

  function stopMusic() {
    if (!currentMusic) {
      return;
    }
    try {
      currentMusic.pause();
      currentMusic.currentTime = 0;
    } catch {
      // Ignore stop failures.
    }
    disconnectNodes(currentMusicNodes);
    currentMusic = null;
    currentMusicNodes = null;
    currentMusicName = "";
    currentMusicLooping = true;
    pendingMusicPacket = null;
  }

  function stopAmbience() {
    if (currentAmbience) {
      try {
        currentAmbience.pause();
        currentAmbience.currentTime = 0;
      } catch {
        // Ignore stop failures.
      }
      disconnectNodes(currentAmbienceNodes);
      currentAmbience = null;
      currentAmbienceNodes = null;
    }
    if (currentAmbienceLoop) {
      try {
        currentAmbienceLoop.pause();
        currentAmbienceLoop.currentTime = 0;
      } catch {
        // Ignore stop failures.
      }
      disconnectNodes(currentAmbienceLoopNodes);
      currentAmbienceLoop = null;
      currentAmbienceLoopNodes = null;
    }
    currentAmbienceLoopName = "";
    pendingAmbiencePacket = null;
  }

  function playAmbience(packet) {
    const loopName = packet.loop || "";
    const introName = packet.intro || "";
    if (!loopName) {
      return;
    }
    if (currentAmbienceLoop && currentAmbienceLoopName === loopName) {
      if (currentAmbienceLoop.paused) {
        safePlay(currentAmbienceLoop, {
          onRejected: () => {
            pendingAmbiencePacket = {
              loop: loopName,
              intro: introName,
              outro: packet.outro || "",
            };
          },
        });
      }
      return;
    }

    stopAmbience();

    const loopAudio = createAudioElement(toSoundUrl(loopName, soundBaseUrl));
    loopAudio.muted = muted;
    loopAudio.preload = "auto";
    loopAudio.loop = true;
    loopAudio.volume = 1.0;
    const loopUrl = toSoundUrl(loopName, soundBaseUrl);
    const loopNodes = connectElement(loopAudio, ambienceGain, 0, loopUrl);
    if (!loopNodes && ambienceGain) {
      loopAudio.volume *= ambienceGain.gain.value;
    }

    const startLoop = () => {
      currentAmbienceLoop = loopAudio;
      currentAmbienceLoopNodes = loopNodes;
      currentAmbienceLoopName = loopName;
      pendingAmbiencePacket = null;
      safePlay(loopAudio, {
        onRejected: () => {
          pendingAmbiencePacket = {
            loop: loopName,
            intro: introName,
            outro: packet.outro || "",
          };
        },
      });
    };

    if (introName) {
      const introAudio = createAudioElement(toSoundUrl(introName, soundBaseUrl));
      introAudio.muted = muted;
      introAudio.preload = "auto";
      introAudio.loop = false;
      introAudio.volume = 1.0;
      const introUrl = toSoundUrl(introName, soundBaseUrl);
      const introNodes = connectElement(introAudio, ambienceGain, 0, introUrl);
      if (!introNodes && ambienceGain) {
        introAudio.volume *= ambienceGain.gain.value;
      }
      introAudio.addEventListener("ended", () => {
        disconnectNodes(introNodes);
        currentAmbienceNodes = null;
        startLoop();
      }, { once: true });
      currentAmbience = introAudio;
      currentAmbienceNodes = introNodes;
      safePlay(introAudio, {
        onRejected: () => {
          pendingAmbiencePacket = {
            loop: loopName,
            intro: introName,
            outro: packet.outro || "",
          };
          startLoop();
        },
      });
      return;
    }

    startLoop();
  }

  function retryPendingPlayback() {
    if (pendingMusicPacket) {
      const packet = pendingMusicPacket;
      pendingMusicPacket = null;
      playMusic(packet);
    }
    if (pendingAmbiencePacket) {
      const packet = pendingAmbiencePacket;
      pendingAmbiencePacket = null;
      playAmbience(packet);
    }
    if (pendingEffectPackets.length > 0) {
      const packets = pendingEffectPackets.splice(0, pendingEffectPackets.length);
      for (const packet of packets) {
        playSound(packet);
      }
    }
  }

  function setMusicVolumePercent(percent) {
    const bounded = Math.max(0, Math.min(100, Number(percent)));
    if (musicGain) {
      musicGain.gain.value = bounded / 100;
    } else if (currentMusic) {
      currentMusic.volume = bounded / 100;
    }
    return bounded;
  }

  function setAmbienceVolumePercent(percent) {
    const bounded = Math.max(0, Math.min(100, Number(percent)));
    if (ambienceGain) {
      ambienceGain.gain.value = bounded / 100;
    } else {
      if (currentAmbience) {
        currentAmbience.volume = bounded / 100;
      }
      if (currentAmbienceLoop) {
        currentAmbienceLoop.volume = bounded / 100;
      }
    }
    return bounded;
  }

  function setMuted(nextMuted) {
    muted = Boolean(nextMuted);
    if (currentMusic) {
      currentMusic.muted = muted;
    }
    if (currentAmbience) {
      currentAmbience.muted = muted;
    }
    if (currentAmbienceLoop) {
      currentAmbienceLoop.muted = muted;
    }
    for (const effect of activeEffects.keys()) {
      effect.muted = muted;
    }
    for (const effect of activeBufferEffects) {
      effect.gain.gain.value = muted ? 0 : effect.volume;
    }
  }

  function isMuted() {
    return muted;
  }

  function getMusicVolumePercent() {
    if (musicGain) {
      return Math.round(musicGain.gain.value * 100);
    }
    if (currentMusic) {
      return Math.round(currentMusic.volume * 100);
    }
    return 20;
  }

  function getAmbienceVolumePercent() {
    if (ambienceGain) {
      return Math.round(ambienceGain.gain.value * 100);
    }
    if (currentAmbienceLoop) {
      return Math.round(currentAmbienceLoop.volume * 100);
    }
    return 100;
  }

  function stopAll() {
    stopMusic();
    stopAmbience();
    for (const [audio, nodes] of activeEffects) {
      try {
        audio.pause();
        audio.currentTime = 0;
      } catch {
        // Ignore per-element stop failures.
      }
      disconnectNodes(nodes);
    }
    activeEffects.clear();
    for (const effect of Array.from(activeBufferEffects)) {
      stopBufferEffect(effect);
    }
  }

  return {
    unlock,
    playSound,
    playMusic,
    playAmbience,
    stopMusic,
    stopAmbience,
    stopAll,
    setMusicVolumePercent,
    setAmbienceVolumePercent,
    getMusicVolumePercent,
    getAmbienceVolumePercent,
    setMuted,
    isMuted,
    retryPendingPlayback,
    preloadEffects,
  };
}
