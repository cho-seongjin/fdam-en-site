// Imweb can stack another page's widget under this one (one-page menus). Keep only the first
// widget's header so navigation bars never pile up and the wrong menu never shows as active.
document.querySelectorAll('.fdam-root > .site-header').forEach((header, index) => { if (index > 0) header.remove(); });
document.querySelectorAll('.fdam-root > .scroll-progress').forEach((bar, index) => { if (index > 0) bar.remove(); });

const header = document.querySelector('.site-header');
const menuButton = document.querySelector('.menu-button');
const nav = document.querySelector('.nav-links');

const progressBar = document.querySelector('.scroll-progress i');
const parallaxItems = document.querySelectorAll('[data-parallax]');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const updateScrollEffects = () => {
  header?.classList.toggle('scrolled', window.scrollY > 24);
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollable > 0 ? Math.min(window.scrollY / scrollable, 1) : 0;
  if (progressBar) progressBar.style.transform = `scaleX(${progress})`;

  if (!reducedMotion) {
    parallaxItems.forEach((item) => {
      const speed = Number(item.dataset.parallax || 0.06);
      const rect = item.getBoundingClientRect();
      const offset = (window.innerHeight / 2 - (rect.top + rect.height / 2)) * speed;
      item.style.setProperty('--parallax-y', `${Math.max(-28, Math.min(28, offset))}px`);
    });
  }
};
const updateHeader = updateScrollEffects;
updateHeader();
window.addEventListener('scroll', updateScrollEffects, { passive: true });
window.addEventListener('resize', updateScrollEffects, { passive: true });

menuButton?.addEventListener('click', () => {
  const isOpen = nav.classList.toggle('open');
  menuButton.setAttribute('aria-expanded', String(isOpen));
  menuButton.setAttribute('aria-label', isOpen ? '메뉴 닫기' : '메뉴 열기');
});

document.querySelectorAll('.nav-links a').forEach((link) => link.addEventListener('click', () => {
  nav?.classList.remove('open');
  menuButton?.setAttribute('aria-expanded', 'false');
  menuButton?.setAttribute('aria-label', '메뉴 열기');
}));

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('is-visible');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });
document.querySelectorAll('.reveal, .reveal-scale, .reveal-stagger').forEach((el) => revealObserver.observe(el));

document.querySelectorAll('.platform-grid, .issue-list, .flow-line, .data-proof-list, .copilot-steps, .ob-steps').forEach((group) => {
  group.classList.add('reveal-stagger');
  Array.from(group.children).forEach((item, index) => item.style.setProperty('--stagger', index));
  revealObserver.observe(group);
});

const hero = document.querySelector('.hero');
hero?.addEventListener('pointermove', (event) => {
  const rect = hero.getBoundingClientRect();
  hero.style.setProperty('--mx', `${((event.clientX - rect.left) / rect.width) * 100}%`);
  hero.style.setProperty('--my', `${((event.clientY - rect.top) / rect.height) * 100}%`);
});

// Living gradient behind the main hero: one soft liquid body that wanders and reshapes itself like a cell.
// On hover it drifts toward the cursor and stretches a lobe out to meet it.
(() => {
  const canvas = document.querySelector('.hero-aurora');
  const host = canvas?.closest('.hero');
  if (!canvas || !host) return;
  const ctx = canvas.getContext('2d');
  const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  // lobes that orbit a shared centre; they stay close enough to always read as a single body
  // [angle, distance, radius, r, g, b] — distance and radius as fractions of the hero width
  const lobes = [
    [0.0, 0.0, 0.1, 139, 132, 236],
    [0.0, 0.095, 0.07, 139, 124, 240],
    [0.9, 0.105, 0.064, 132, 150, 203],
    [1.8, 0.1, 0.06, 126, 200, 246],
    [2.7, 0.11, 0.056, 196, 168, 246],
    [3.6, 0.095, 0.064, 150, 184, 250],
    [4.5, 0.105, 0.058, 118, 140, 230],
    [5.4, 0.09, 0.052, 214, 176, 244],
  ].map(([ang, dist, r, cr, cg, cb], i) => ({ ang, dist, r, c: [cr, cg, cb], seed: i * 1.93 + 0.4 }));
  const body = { x: 0.68, y: 0.48 };
  const focus = { x: 0.7, y: 0.45, on: 0 };
  const pointer = { x: 0.7, y: 0.45, inside: false };
  let w = 0, h = 0, img = null, raf = 0, visible = true, last = 0;
  const t0 = performance.now();

  const resize = () => {
    const rect = canvas.getBoundingClientRect();
    // coarse field grid; the CSS blur turns it into a smooth membrane
    w = canvas.width = Math.max(60, Math.round(rect.width / 6));
    h = canvas.height = Math.max(60, Math.round(rect.height / 6));
    img = ctx.createImageData(w, h);
  };

  const frame = (now) => {
    // ~30fps keeps the motion fluid while halving the per-pixel work
    if (!still && now - last < 30) { raf = requestAnimationFrame(frame); return; }
    last = now;
    const t = (now - t0) / 1000;
    focus.on += ((pointer.inside ? 1 : 0) - focus.on) * 0.035;
    focus.x += (pointer.x - focus.x) * 0.05;
    focus.y += (pointer.y - focus.y) * 0.05;
    const tall = h > w;
    const unit = tall ? w * 2.2 : w;
    // the body wanders around its home spot; on hover it moves most of the way to the cursor
    // roam the whole hero: incommensurate sines trace a path that never settles on one side
    const wx = 0.5 + Math.sin(t * 0.31) * 0.26 + Math.sin(t * 0.17 + 1.3) * 0.12 + Math.sin(t * 0.53 + 0.4) * 0.04;
    const wy = (tall ? 0.42 : 0.5) + Math.cos(t * 0.27) * 0.2 + Math.sin(t * 0.41 + 0.7) * 0.1 + Math.cos(t * 0.13 + 2.1) * 0.05;
    body.x += (wx + (focus.x - wx) * 0.6 * focus.on - body.x) * 0.08;
    body.y += (wy + (focus.y - wy) * 0.6 * focus.on - body.y) * 0.08;
    const cxp = body.x * w, cyp = body.y * h * (tall ? 1 : 1);
    const toCur = Math.atan2((focus.y - body.y) * h, (focus.x - body.x) * w);
    const live = lobes.map((l) => {
      const s = l.seed;
      // each lobe circles, swells and reaches out on its own rhythm, so the outline keeps reshaping
      const ang = l.ang + t * (0.35 + (s % 1) * 0.3) + Math.sin(t * 0.9 + s) * 0.6;
      const dist = l.dist * unit * (1 + Math.sin(t * 1.1 + s * 2) * 0.45);
      const r = l.r * unit * (1 + Math.sin(t * 1.3 + s * 3) * 0.2);
      return [cxp + Math.cos(ang) * dist, cyp + Math.sin(ang) * dist * (tall ? 1 : 1.15), r * r, l.c];
    });
    if (focus.on > 0.01) {
      // a pseudopod stretches toward the cursor
      const reach = 0.11 * unit * focus.on * (1 + Math.sin(t * 2) * 0.12);
      const r = 0.06 * unit * focus.on;
      live.push([cxp + Math.cos(toCur) * reach, cyp + Math.sin(toCur) * reach, r * r, [112, 122, 238]]);
    }
    const d = img.data;
    const n = live.length;
    let i = 0;
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++, i += 4) {
        let f = 0, r = 0, g = 0, b = 0, wsum = 0;
        for (let k = 0; k < n; k++) {
          const c = live[k];
          const ddx = x - c[0], ddy = y - c[1];
          const v = c[2] / (ddx * ddx + ddy * ddy + 1);
          // cap the colour weight so lobe centres blend instead of showing as spots
          const cw = v < 1.5 ? v : 1.5;
          f += v; r += c[3][0] * cw; g += c[3][1] * cw; b += c[3][2] * cw; wsum += cw;
        }
        if (f < 0.25) { d[i + 3] = 0; continue; }
        r /= wsum; g /= wsum; b /= wsum;
        // soft body + a faint bright membrane where cells meet the background
        const body = Math.min(1, Math.max(0, (f - 0.35) / 1.3));
        const a = body * body * (3 - 2 * body);
        const rim = Math.exp(-((f - 0.9) * (f - 0.9)) / 0.08) * 0.35;
        d[i] = r + (255 - r) * rim; d[i + 1] = g + (255 - g) * rim; d[i + 2] = b + (255 - b) * rim;
        d[i + 3] = 255 * Math.min(0.62, a * 0.52 + rim * 0.36);
      }
    }
    ctx.putImageData(img, 0, 0);
    if (!still && visible) raf = requestAnimationFrame(frame);
  };

  const start = () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(frame); };
  host.addEventListener('pointermove', (event) => {
    if (event.pointerType === 'touch') return;
    const rect = canvas.getBoundingClientRect();
    pointer.x = (event.clientX - rect.left) / rect.width;
    pointer.y = (event.clientY - rect.top) / rect.height;
    pointer.inside = true;
  });
  host.addEventListener('pointerleave', () => { pointer.inside = false; });
  new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting && !document.hidden;
    if (visible && !still) start();
  }).observe(host);
  document.addEventListener('visibilitychange', () => {
    visible = !document.hidden;
    if (visible && !still) start();
  });
  // the hero grows when the copilot answer appears, so track the canvas box itself rather than the window
  const onResize = () => { resize(); if (still) frame(performance.now()); };
  if ('ResizeObserver' in window) new ResizeObserver(onResize).observe(canvas); else window.addEventListener('resize', onResize);
  resize();
  frame(performance.now());
  canvas.classList.add('is-ready');
})();

const solutionTabs = Array.from(document.querySelectorAll('[data-solution-tab]'));
const solutionPanels = Array.from(document.querySelectorAll('[data-solution-panel]'));

const activateSolution = (key, moveFocus = false) => {
  solutionTabs.forEach((tab) => {
    const active = tab.dataset.solutionTab === key;
    tab.classList.toggle('is-active', active);
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
    if (active && moveFocus) tab.focus();
  });
  solutionPanels.forEach((panel) => {
    const active = panel.dataset.solutionPanel === key;
    panel.hidden = !active;
    panel.classList.toggle('is-active', active);
  });
};

solutionTabs.forEach((tab, index) => {
  tab.addEventListener('click', () => activateSolution(tab.dataset.solutionTab));
  tab.addEventListener('keydown', (event) => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    let next = index;
    if (event.key === 'ArrowRight') next = (index + 1) % solutionTabs.length;
    if (event.key === 'ArrowLeft') next = (index - 1 + solutionTabs.length) % solutionTabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = solutionTabs.length - 1;
    activateSolution(solutionTabs[next].dataset.solutionTab, true);
  });
});

const roleTabs = Array.from(document.querySelectorAll('[data-role-tab]'));
const rolePanels = Array.from(document.querySelectorAll('[data-role-panel]'));

const activateRole = (key, moveFocus = false) => {
  roleTabs.forEach((tab) => {
    const active = tab.dataset.roleTab === key;
    tab.classList.toggle('is-active', active);
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
    if (active && moveFocus) tab.focus();
  });
  rolePanels.forEach((panel) => {
    const active = panel.dataset.rolePanel === key;
    panel.hidden = !active;
    panel.classList.toggle('is-active', active);
  });
};

roleTabs.forEach((tab, index) => {
  tab.addEventListener('click', () => activateRole(tab.dataset.roleTab));
  tab.addEventListener('keydown', (event) => {
    if (!['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    let next = index;
    if (['ArrowDown', 'ArrowRight'].includes(event.key)) next = (index + 1) % roleTabs.length;
    if (['ArrowUp', 'ArrowLeft'].includes(event.key)) next = (index - 1 + roleTabs.length) % roleTabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = roleTabs.length - 1;
    activateRole(roleTabs[next].dataset.roleTab, true);
  });
});

const salesTabs = Array.from(document.querySelectorAll('[data-sales-tab]'));
const salesPanels = Array.from(document.querySelectorAll('[data-sales-panel]'));

const activateSalesView = (key, moveFocus = false) => {
  salesTabs.forEach((tab) => {
    const active = tab.dataset.salesTab === key;
    tab.classList.toggle('active', active);
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
    if (active && moveFocus) tab.focus();
  });
  salesPanels.forEach((panel) => {
    const active = panel.dataset.salesPanel === key;
    panel.hidden = !active;
    panel.classList.toggle('is-active', active);
  });
};

salesTabs.forEach((tab, index) => {
  tab.addEventListener('click', () => activateSalesView(tab.dataset.salesTab));
  tab.addEventListener('keydown', (event) => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    let next = index;
    if (event.key === 'ArrowRight') next = (index + 1) % salesTabs.length;
    if (event.key === 'ArrowLeft') next = (index - 1 + salesTabs.length) % salesTabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = salesTabs.length - 1;
    activateSalesView(salesTabs[next].dataset.salesTab, true);
  });
});

const aiSuiteTrack = document.querySelector('.ai-suite-track');
if (aiSuiteTrack) {
  let dragging = false;
  let moved = false;
  let startX = 0;
  let startScroll = 0;

  aiSuiteTrack.addEventListener('pointerdown', (event) => {
    if (event.pointerType !== 'mouse' || event.button !== 0) return;
    dragging = true;
    moved = false;
    startX = event.clientX;
    startScroll = aiSuiteTrack.scrollLeft;
  });

  // capture the pointer only once the user actually drags, so a plain click still reaches the card links
  aiSuiteTrack.addEventListener('pointermove', (event) => {
    if (!dragging) return;
    const distance = event.clientX - startX;
    if (!moved && Math.abs(distance) > 5) {
      moved = true;
      aiSuiteTrack.classList.add('is-dragging');
      aiSuiteTrack.setPointerCapture(event.pointerId);
    }
    if (moved) aiSuiteTrack.scrollLeft = startScroll - distance;
  });

  const stopDragging = (event) => {
    if (!dragging) return;
    dragging = false;
    aiSuiteTrack.classList.remove('is-dragging');
    if (aiSuiteTrack.hasPointerCapture(event.pointerId)) aiSuiteTrack.releasePointerCapture(event.pointerId);
    if (moved) {
      aiSuiteTrack.dataset.preventClick = 'true';
      window.setTimeout(() => delete aiSuiteTrack.dataset.preventClick, 0);
    }
  };

  aiSuiteTrack.addEventListener('pointerup', stopDragging);
  aiSuiteTrack.addEventListener('pointercancel', stopDragging);
  aiSuiteTrack.addEventListener('dragstart', (event) => event.preventDefault());
  aiSuiteTrack.addEventListener('click', (event) => {
    if (aiSuiteTrack.dataset.preventClick === 'true') event.preventDefault();
  }, true);
}

const constellationRoot = document.querySelector('[data-constellation]');
if (constellationRoot) {
  const stage = constellationRoot.querySelector('[data-constellation-stage]');
  const threads = constellationRoot.querySelector('[data-constellation-lines]');
  const card = constellationRoot.querySelector('[data-constellation-card]');
  const cardTitle = constellationRoot.querySelector('[data-constellation-card-title]');
  const cardCopy = constellationRoot.querySelector('[data-constellation-card-copy]');
  const cardLink = constellationRoot.querySelector('[data-constellation-card-link]');
  const destinationByNode = {
    sales: 'sales-analytics.html#channels',
    hq: 'hq-operations.html#workflow',
    store: 'sodam.html#features',
    customer: 'ai-platform.html#customer-experience',
    ai: 'ai-platform.html#capabilities',
    pos: 'sales-analytics.html#pos-sales',
    delivery: 'sales-analytics.html#delivery-sales',
    special: 'sales-analytics.html#special-sales',
    lead: 'hq-operations.html#sales-management',
    opening: 'hq-operations.html#opening',
    qscv: 'hq-operations.html#operation',
    order: 'sodam.html#ordering',
    inventory: 'sodam.html#inventory',
    staff: 'sodam.html#staff-management',
    communication: 'sodam.html#hq-communication',
    review: 'ai-platform.html#review-insight',
    voc: 'ai-platform.html#customer-voc',
    reply: 'ai-platform.html#ai-review-reply',
    'order-ai': 'ai-platform.html#ai-order',
    'sales-drop': 'ai-platform.html#ai-sales-drop',
    closure: 'ai-platform.html#ai-closure-risk',
    report: 'ai-platform.html#ai-report'
  };
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const nodeElements = Array.from(constellationRoot.querySelectorAll('[data-constellation-node]'));
  const mobilePositions = {
    fdam: [180, 372],
    sales: [92, 180], pos: [48, 92], delivery: [134, 70], special: [44, 262],
    hq: [268, 180], lead: [226, 74], opening: [314, 96], qscv: [322, 262],
    store: [292, 410], order: [326, 334], inventory: [330, 486], staff: [262, 494], communication: [214, 452],
    customer: [236, 590], reply: [300, 548], review: [316, 664], voc: [204, 676],
    ai: [86, 540], 'order-ai': [62, 440], 'sales-drop': [70, 628], closure: [112, 690], report: [146, 470]
  };
  const states = nodeElements.map((element, index) => ({
    element,
    id: element.dataset.constellationNode,
    parent: element.dataset.parent || '',
    group: element.dataset.group || '',
    desktopX: Number(element.dataset.x),
    desktopY: Number(element.dataset.y),
    mobileX: mobilePositions[element.dataset.constellationNode]?.[0],
    mobileY: mobilePositions[element.dataset.constellationNode]?.[1],
    x: Number(element.dataset.x),
    y: Number(element.dataset.y),
    currentX: Number(element.dataset.x),
    currentY: Number(element.dataset.y),
    phase: index * 1.73,
    dragging: false,
    moved: false
  }));
  const stateById = Object.fromEntries(states.map((state) => [state.id, state]));
  const links = [];
  let compact = false;
  let viewWidth = 1000;
  let viewHeight = 620;
  let hideCardTimer = 0;
  let frame = 0;

  const configureViewport = () => {
    compact = constellationRoot.clientWidth <= 760;
    viewWidth = compact ? 360 : 1000;
    viewHeight = compact ? 740 : 620;
    threads?.setAttribute('viewBox', `0 0 ${viewWidth} ${viewHeight}`);
    links.forEach((link) => {
      link.line.style.display = '';
    });
  };

  states.forEach((child, index) => {
    if (!child.parent || !threads) return;
    const parent = stateById[child.parent];
    if (!parent) return;
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('pathLength', '1');
    line.classList.add(child.parent === 'fdam' ? 'is-primary' : 'is-secondary');
    line.style.setProperty('--i', index);
    line.dataset.group = child.group;
    threads.appendChild(line);
    links.push({ line, parent, child, group: child.group });
  });

  const positionFor = (state) => {
    if (compact && Number.isFinite(state.mobileX) && Number.isFinite(state.mobileY)) {
      return [state.mobileX, state.mobileY];
    }
    return [state.desktopX, state.desktopY];
  };

  const trimmedLine = (from, to, fromPadding, toPadding) => {
    const dx = to.currentX - from.currentX;
    const dy = to.currentY - from.currentY;
    const length = Math.hypot(dx, dy) || 1;
    return {
      x1: from.currentX + (dx / length) * fromPadding,
      y1: from.currentY + (dy / length) * fromPadding,
      x2: to.currentX - (dx / length) * toPadding,
      y2: to.currentY - (dy / length) * toPadding
    };
  };

  const renderConstellation = (time = 0) => {
    const seconds = time / 1000;
    states.forEach((state) => {
      const [baseX, baseY] = positionFor(state);
      if (!state.dragging) {
        state.x = baseX;
        state.y = baseY;
      }
      const secondary = state.element.classList.contains('constellation-node--secondary');
      const amplitude = state.id === 'fdam' ? 2.6 : secondary ? 7.2 : 4.8;
      const driftX = reduceMotion.matches || state.dragging || compact ? 0 : Math.sin(seconds * .38 + state.phase) * amplitude;
      const driftY = reduceMotion.matches || state.dragging || compact ? 0 : Math.cos(seconds * .31 + state.phase * .8) * amplitude * .68;
      state.currentX = state.x + driftX;
      state.currentY = state.y + driftY;
      state.element.style.left = `${(state.currentX / viewWidth) * 100}%`;
      state.element.style.top = `${(state.currentY / viewHeight) * 100}%`;
    });

    links.forEach((link) => {
      if (link.line.style.display === 'none') return;
      const primary = link.child.parent === 'fdam';
      const points = compact
        ? trimmedLine(link.parent, link.child, primary ? 58 : 30, primary ? 34 : 16)
        : trimmedLine(link.parent, link.child, primary ? 62 : 48, primary ? 54 : 25);
      Object.entries(points).forEach(([name, value]) => link.line.setAttribute(name, String(value)));
    });
  };

  const startAnimation = () => {
    if (frame || reduceMotion.matches) {
      renderConstellation();
      return;
    }
    const tick = (time) => {
      renderConstellation(time);
      frame = window.requestAnimationFrame(tick);
    };
    frame = window.requestAnimationFrame(tick);
  };

  const stopAnimation = () => {
    if (!frame) return;
    window.cancelAnimationFrame(frame);
    frame = 0;
  };

  const focusGroup = (group) => {
    if (!group) return;
    stage.classList.add('has-focus');
    states.forEach((state) => state.element.classList.toggle('is-related', state.id === 'fdam' || state.group === group));
    links.forEach((link) => link.line.classList.toggle('is-related', link.group === group));
  };

  const clearGroup = () => {
    stage.classList.remove('has-focus');
    states.forEach((state) => state.element.classList.remove('is-related'));
    links.forEach((link) => link.line.classList.remove('is-related'));
  };

  const placeCard = (state) => {
    if (compact || !card) return;
    const stageRect = stage.getBoundingClientRect();
    const x = (state.currentX / viewWidth) * stageRect.width;
    const y = (state.currentY / viewHeight) * stageRect.height;
    const cardWidth = card.offsetWidth || 270;
    const cardHeight = card.offsetHeight || 130;
    const left = x > stageRect.width * .62 ? x - cardWidth - 24 : x + 24;
    const top = y > stageRect.height * .58 ? y - cardHeight - 20 : y + 20;
    card.style.left = `${Math.max(16, Math.min(left, stageRect.width - cardWidth - 16))}px`;
    card.style.top = `${Math.max(16, Math.min(top, stageRect.height - cardHeight - 16))}px`;
  };

  const showCard = (state) => {
    if (!card || !cardTitle || !cardCopy || !cardLink || !state.element.dataset.title) return;
    window.clearTimeout(hideCardTimer);
    states.forEach((item) => {
      if (item.element.matches('button')) item.element.setAttribute('aria-expanded', String(item === state));
    });
    cardTitle.textContent = state.element.dataset.title;
    cardCopy.textContent = state.element.dataset.copy || '';
    cardLink.href = destinationByNode[state.id] || 'contact.html';
    card.hidden = false;
    placeCard(state);
    window.requestAnimationFrame(() => card.classList.add('is-open'));
  };

  const hideCard = (immediate = false) => {
    if (!card) return;
    window.clearTimeout(hideCardTimer);
    const close = () => {
      card.classList.remove('is-open');
      states.forEach((state) => {
        if (state.element.matches('button')) state.element.setAttribute('aria-expanded', 'false');
      });
      window.setTimeout(() => {
        if (!card.classList.contains('is-open')) card.hidden = true;
      }, 220);
    };
    if (immediate) close();
    else hideCardTimer = window.setTimeout(close, 180);
  };

  states.forEach((state) => {
    const element = state.element;
    if (element.matches('button')) element.setAttribute('aria-expanded', 'false');

    element.addEventListener('pointerenter', (event) => {
      if (event.pointerType === 'touch') return;
      focusGroup(state.group);
      if (element.matches('button')) showCard(state);
    });
    element.addEventListener('pointerleave', (event) => {
      if (event.pointerType === 'touch' || state.dragging) return;
      clearGroup();
      hideCard();
    });
    element.addEventListener('focus', () => {
      focusGroup(state.group);
      showCard(state);
    });
    element.addEventListener('blur', () => {
      clearGroup();
      hideCard();
    });
    element.addEventListener('click', (event) => {
      if (state.moved) {
        event.preventDefault();
        state.moved = false;
        return;
      }
      if (window.matchMedia('(hover: hover)').matches) return;
      focusGroup(state.group);
      showCard(state);
    });
    element.addEventListener('pointerdown', (event) => {
      if (event.pointerType === 'touch' || event.button !== 0) return;
      const rect = stage.getBoundingClientRect();
      state.dragging = true;
      state.moved = false;
      state.grabX = (event.clientX - rect.left) / rect.width * viewWidth - state.x;
      state.grabY = (event.clientY - rect.top) / rect.height * viewHeight - state.y;
      element.classList.add('is-dragging');
      element.setPointerCapture(event.pointerId);
    });
    element.addEventListener('pointermove', (event) => {
      if (!state.dragging) return;
      const rect = stage.getBoundingClientRect();
      const nextX = (event.clientX - rect.left) / rect.width * viewWidth - state.grabX;
      const nextY = (event.clientY - rect.top) / rect.height * viewHeight - state.grabY;
      if (Math.hypot(nextX - state.x, nextY - state.y) > 2) state.moved = true;
      state.x = Math.max(28, Math.min(viewWidth - 28, nextX));
      state.y = Math.max(24, Math.min(viewHeight - 24, nextY));
      if (compact) {
        state.mobileX = state.x;
        state.mobileY = state.y;
      } else {
        state.desktopX = state.x;
        state.desktopY = state.y;
      }
      renderConstellation();
    });
    const release = (event) => {
      if (!state.dragging) return;
      state.dragging = false;
      element.classList.remove('is-dragging');
      if (element.hasPointerCapture(event.pointerId)) element.releasePointerCapture(event.pointerId);
    };
    element.addEventListener('pointerup', release);
    element.addEventListener('pointercancel', release);
  });

  card?.addEventListener('pointerenter', () => window.clearTimeout(hideCardTimer));
  card?.addEventListener('pointerleave', () => hideCard());
  document.addEventListener('pointerdown', (event) => {
    if (event.pointerType !== 'touch' || !card || card.hidden) return;
    if (!card.contains(event.target) && !event.target.closest('[data-constellation-node]')) {
      hideCard(true);
      clearGroup();
    }
  });

  configureViewport();
  renderConstellation();
  stage.classList.add('is-ready');
  const constellationResize = new ResizeObserver(() => {
    configureViewport();
    renderConstellation();
  });
  constellationResize.observe(constellationRoot);
  const constellationVisibility = new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting) startAnimation();
    else stopAnimation();
  }, { threshold: .05 });
  constellationVisibility.observe(constellationRoot);
}

const copilotConsole = document.querySelector('.copilot-console');
const copilotQuestion = copilotConsole?.querySelector('[data-copilot-question]');
if (copilotConsole && copilotQuestion && !reducedMotion) {
  const fullQuestion = copilotQuestion.textContent.trim();
  const stages = ['stage-user', 'stage-typing', 'stage-answer', 'stage-reset'];
  let cycleTimers = [];
  let typingTimer = 0;
  let isRunning = false;

  const clearCopilotTimers = () => {
    cycleTimers.forEach((timer) => window.clearTimeout(timer));
    cycleTimers = [];
    window.clearInterval(typingTimer);
    typingTimer = 0;
  };
  const setCopilotStage = (stage = '') => {
    copilotConsole.classList.remove(...stages);
    if (stage) copilotConsole.classList.add(stage);
  };
  const scheduleCopilotStage = (callback, delay) => {
    cycleTimers.push(window.setTimeout(callback, delay));
  };
  const typeCopilotQuestion = () => {
    let index = 0;
    copilotQuestion.textContent = '';
    typingTimer = window.setInterval(() => {
      index += 1;
      copilotQuestion.textContent = fullQuestion.slice(0, index);
      if (index >= fullQuestion.length) {
        window.clearInterval(typingTimer);
        typingTimer = 0;
      }
    }, 38);
  };
  const runCopilotCycle = () => {
    if (!isRunning) return;
    clearCopilotTimers();
    copilotConsole.classList.add('is-looping');
    setCopilotStage();
    copilotQuestion.textContent = '';
    scheduleCopilotStage(() => {
      setCopilotStage('stage-user');
      typeCopilotQuestion();
    }, 450);
    scheduleCopilotStage(() => {
      window.clearInterval(typingTimer);
      typingTimer = 0;
      copilotQuestion.textContent = fullQuestion;
      setCopilotStage('stage-typing');
    }, 2500);
    // play once and stay on the answer; it replays when the console scrolls back into view
    scheduleCopilotStage(() => setCopilotStage('stage-answer'), 4550);
  };
  const stopCopilotCycle = () => {
    isRunning = false;
    clearCopilotTimers();
    copilotConsole.classList.remove('is-looping', ...stages);
    copilotQuestion.textContent = fullQuestion;
  };
  const copilotVisibility = new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting && !isRunning) {
      isRunning = true;
      runCopilotCycle();
    } else if (!entry.isIntersecting && isRunning) {
      stopCopilotCycle();
    }
  }, { threshold: .2 });
  copilotVisibility.observe(copilotConsole);
}

const attributionStorageKey = 'fdam_first_touch_attribution';
const attributionParams = new URLSearchParams(window.location.search);
const cleanAttributionUrl = (value) => {
  if (!value) return '';
  try {
    const url = new URL(value, window.location.origin);
    return `${url.origin}${url.pathname}`;
  } catch {
    return '';
  }
};
const campaignKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
const currentCampaign = Object.fromEntries(campaignKeys.map((key) => [key, attributionParams.get(key) || '']));
const currentClickId = ['gclid', 'fbclid', 'nclid', 'kclid'].map((key) => attributionParams.get(key)).find(Boolean) || '';
const initialAttribution = {
  first_landing_page: cleanAttributionUrl(window.location.href),
  first_referrer: cleanAttributionUrl(document.referrer),
  first_visit_at: new Date().toISOString(),
  click_id: currentClickId,
  ...currentCampaign,
};
let firstAttribution = initialAttribution;

try {
  const storedAttribution = window.localStorage.getItem(attributionStorageKey);
  if (storedAttribution) {
    firstAttribution = { ...initialAttribution, ...JSON.parse(storedAttribution) };
  } else {
    window.localStorage.setItem(attributionStorageKey, JSON.stringify(initialAttribution));
  }
} catch {
  firstAttribution = initialAttribution;
}

const inferLeadSource = () => {
  const campaignSource = currentCampaign.utm_source || firstAttribution.utm_source;
  if (campaignSource) return campaignSource;
  const referrer = firstAttribution.first_referrer;
  if (!referrer) return 'direct';
  try {
    const hostname = new URL(referrer).hostname.replace(/^www\./, '');
    if (/naver\.|google\.|daum\.|bing\./i.test(hostname)) return 'organic-search';
    if (/instagram\.|facebook\.|linkedin\.|youtube\./i.test(hostname)) return 'social';
    if (hostname === window.location.hostname.replace(/^www\./, '')) return 'internal';
    return hostname;
  } catch {
    return 'referral';
  }
};

const form = document.querySelector('[data-contact-form]');
if (form) {
  const attributionValues = {
    inferred_source: inferLeadSource(),
    first_landing_page: firstAttribution.first_landing_page,
    first_referrer: firstAttribution.first_referrer,
    first_visit_at: firstAttribution.first_visit_at,
    last_referrer: cleanAttributionUrl(document.referrer),
    contact_page_url: cleanAttributionUrl(window.location.href),
    click_id: currentClickId || firstAttribution.click_id,
    ...Object.fromEntries(campaignKeys.map((key) => [key, currentCampaign[key] || firstAttribution[key] || ''])),
  };
  form.querySelectorAll('[data-attribution-field]').forEach((field) => {
    field.value = attributionValues[field.dataset.attributionField] || '';
  });
}

form?.addEventListener('submit', (event) => {
  event.preventDefault();
  const success = form.querySelector('.form-success');
  success?.classList.add('show');
  success?.setAttribute('tabindex', '-1');
  success?.focus();
});

// AI platform: pointer spotlight on cards and active capability tab
if (document.body.classList.contains('ai-page')) {
  document.querySelectorAll('.aix-card, .ai-page .ai-detail').forEach((card) => {
    card.addEventListener('pointermove', (event) => {
      const rect = card.getBoundingClientRect();
      card.style.setProperty('--mx', `${event.clientX - rect.left}px`);
      card.style.setProperty('--my', `${event.clientY - rect.top}px`);
    });
  });

  const capNav = document.querySelector('.aix-cap-nav');
  const capLinks = [...document.querySelectorAll('.aix-cap-nav a')];
  const capObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      capLinks.forEach((link) => link.classList.toggle('is-active', link.getAttribute('href') === `#${entry.target.id}`));
      const active = capNav.querySelector('a.is-active');
      if (active && capNav.scrollWidth > capNav.clientWidth) {
        capNav.scrollTo({ left: active.offsetLeft - (capNav.clientWidth - active.offsetWidth) / 2, behavior: 'smooth' });
      }
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  capLinks.forEach((link) => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) capObserver.observe(target);
  });
}

// In-page anchors: handled here before host-page scripts (e.g. Imweb one-page scroll) so scroll-margin and the URL hash are kept
const ownsLink = (link) => link.closest('.fdam-root') || !document.querySelector('.fdam-root');
const scrollToAnchor = (target, smooth) => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  target.scrollIntoView({ behavior: smooth && !reduce ? 'smooth' : 'auto', block: 'start' });
};
window.addEventListener('click', (event) => {
  const link = event.target.closest?.('a[href^="#"]');
  if (!link || !ownsLink(link) || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  const id = decodeURIComponent(link.getAttribute('href').slice(1));
  const target = id && document.getElementById(id);
  if (!target) return;
  event.preventDefault();
  event.stopImmediatePropagation();
  scrollToAnchor(target, true);
  history.pushState(null, '', `#${id}`);
}, true);

const initialAnchor = window.location.hash && document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
if (initialAnchor && document.querySelector('.fdam-root')) {
  const settle = () => setTimeout(() => scrollToAnchor(initialAnchor, false), 80);
  if (document.readyState === 'complete') settle(); else window.addEventListener('load', settle, { once: true });
}

// Client logo rows are written once in HTML; clone each track so the -50% roll loops seamlessly.
document.querySelectorAll('.logo-marquee-track').forEach((track) => {
  if (track.dataset.cloned) return;
  track.dataset.cloned = '1';
  [...track.children].forEach((chip) => {
    const copy = chip.cloneNode(true);
    copy.setAttribute('aria-hidden', 'true');
    copy.removeAttribute('role');
    copy.querySelectorAll('img').forEach((img) => { img.alt = ''; });
    track.appendChild(copy);
  });
});
