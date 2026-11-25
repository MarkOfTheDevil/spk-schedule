(function () {
  'use strict';

  // Preserve the white lettering and tint only the blue parts of the emblem.
  function tint(pixels, accent) {
    const [red, green, blue] = accent.map(channel => channel / 255);
    const max = Math.max(red, green, blue);
    const min = Math.min(red, green, blue);
    const spread = max - min;
    const tone = spread > .025 ? accent.map(channel => (channel / 255 - min) / spread) : [.5, .5, .5];
    const strength = spread > .025 ? Math.min(1, spread * 1.35 + .2) : 0;

    for (let i = 0; i < pixels.length; i += 4) {
      if (!pixels[i + 3]) continue;
      const r = pixels[i] / 255, g = pixels[i + 1] / 255, b = pixels[i + 2] / 255;
      const chroma = b - Math.min(r, g);
      if (b <= r || b < g || chroma < .035) continue;
      const neutral = Math.min(r, g);
      const value = Math.min(1, neutral + chroma * (.56 + max * .43));
      const luminance = neutral + (value - neutral) * (strength ? .29 : .48);
      const blueWeight = Math.min(1, chroma * 12);
      for (let c = 0; c < 3; c++) {
        const colored = luminance + (value - luminance) * strength * tone[c];
        pixels[i + c] = Math.round(pixels[i + c] * (1 - blueWeight) + colored * 255 * blueWeight);
      }
    }
    return pixels;
  }

  if (typeof module === 'object' && module.exports) {
    module.exports = tint;
    return;
  }

  const root = document.documentElement;
  const source = new Image();
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  if (!context) return;
  let sourcePixels, currentAccent = '', themedSource = '', frame = 0;

  function paletteColor() {
    const probe = document.createElement('span');
    probe.hidden = true;
    probe.style.color = 'var(--lime)';
    document.body.append(probe);
    const rgb = getComputedStyle(probe).color;
    probe.remove();
    const match = /^rgba?\(\s*(\d+)[, ]+\s*(\d+)[, ]+\s*(\d+)/.exec(rgb);
    return match ? match.slice(1, 4).map(Number) : [186, 242, 110];
  }

  function update() {
    frame = 0;
    const accent = paletteColor();
    const key = accent.join(',');
    if (currentAccent !== key) {
      currentAccent = key;
      const pixels = new ImageData(new Uint8ClampedArray(sourcePixels.data), canvas.width, canvas.height);
      tint(pixels.data, accent);
      context.putImageData(pixels, 0, 0);
      themedSource = canvas.toDataURL('image/png');
      const favicon = document.querySelector('link[rel="icon"]');
      if (favicon) favicon.href = themedSource;
    }
    for (const mark of document.querySelectorAll('img.pulse-mark')) {
      if (mark.getAttribute('src') !== themedSource) mark.src = themedSource;
    }
  }

  function scheduleUpdate() {
    if (!frame) frame = requestAnimationFrame(update);
  }

  source.addEventListener('load', () => {
    canvas.width = source.naturalWidth;
    canvas.height = source.naturalHeight;
    context.drawImage(source, 0, 0);
    sourcePixels = context.getImageData(0, 0, canvas.width, canvas.height);
    const observer = new MutationObserver(records => {
      if (records.some(record => record.type === 'attributes' || [...record.addedNodes].some(node =>
        node.nodeType === 1 && (node.matches('img.pulse-mark') || node.querySelector('img.pulse-mark'))))) scheduleUpdate();
    });
    observer.observe(root, {attributes: true, attributeFilter: ['data-theme', 'data-palette', 'data-custom-design', 'style']});
    observer.observe(document.body, {childList: true, subtree: true});
    scheduleUpdate();
  }, {once: true});
  source.src = 'pulse-mark.png';
})();
