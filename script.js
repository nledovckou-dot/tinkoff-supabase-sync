(() => {
  'use strict';

  const boardEl = document.getElementById('board');
  const sizeEl = document.getElementById('size');
  const minesEl = document.getElementById('mines');
  const resetBtn = document.getElementById('reset');
  const mineCountEl = document.getElementById('mine-count');
  const timerEl = document.getElementById('timer');
  const cellTemplate = document.getElementById('cell-template');

  /** Game state */
  let gridSize = Number(sizeEl.value);
  let mineCount = Number(minesEl.value);
  let cells = [];
  let mines = new Set();
  let revealedCount = 0;
  let flags = new Set();
  let firstClickDone = false;
  let gameOver = false;
  let timerInterval = null;
  let startTime = null;

  function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${String(s).padStart(2, '0')}`;
  }

  function startTimer() {
    startTime = Date.now();
    stopTimer();
    timerInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      timerEl.textContent = formatTime(elapsed);
    }, 250);
  }

  function stopTimer() {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
  }

  function idx(row, col) {
    return row * gridSize + col;
  }

  function inBounds(row, col) {
    return row >= 0 && col >= 0 && row < gridSize && col < gridSize;
  }

  function neighbors(row, col) {
    const result = [];
    for (let dr = -1; dr <= 1; dr++) {
      for (let dc = -1; dc <= 1; dc++) {
        if (dr === 0 && dc === 0) continue;
        const r = row + dr;
        const c = col + dc;
        if (inBounds(r, c)) result.push([r, c]);
      }
    }
    return result;
  }

  function placeMines(safeRow, safeCol) {
    mines.clear();
    const total = gridSize * gridSize;
    const safeIndex = idx(safeRow, safeCol);
    while (mines.size < mineCount) {
      const m = Math.floor(Math.random() * total);
      if (m === safeIndex) continue;
      // Avoid placing mines in immediate neighbors of first click, for a nicer start
      const r = Math.floor(m / gridSize);
      const c = m % gridSize;
      const isNear = Math.abs(r - safeRow) <= 1 && Math.abs(c - safeCol) <= 1;
      if (isNear) continue;
      mines.add(m);
    }
  }

  function countAdjacentMines(row, col) {
    let count = 0;
    for (const [r, c] of neighbors(row, col)) {
      if (mines.has(idx(r, c))) count++;
    }
    return count;
  }

  function createBoard() {
    boardEl.style.setProperty('grid-template-columns', `repeat(${gridSize}, 36px)`);
    boardEl.innerHTML = '';
    cells = new Array(gridSize * gridSize);
    flags.clear();
    revealedCount = 0;
    firstClickDone = false;
    gameOver = false;
    timerEl.textContent = '0:00';
    stopTimer();
    mineCountEl.textContent = `Мины: ${mineCount}`;

    for (let r = 0; r < gridSize; r++) {
      for (let c = 0; c < gridSize; c++) {
        const btn = cellTemplate.content.firstElementChild.cloneNode(true);
        btn.dataset.row = String(r);
        btn.dataset.col = String(c);
        btn.addEventListener('click', onLeftClick);
        btn.addEventListener('contextmenu', onRightClick);
        boardEl.appendChild(btn);
        cells[idx(r, c)] = btn;
      }
    }
  }

  function onLeftClick(e) {
    e.preventDefault();
    if (gameOver) return;
    const btn = e.currentTarget;
    const row = Number(btn.dataset.row);
    const col = Number(btn.dataset.col);
    const key = idx(row, col);
    if (flags.has(key)) return; // don't open flagged

    if (!firstClickDone) {
      placeMines(row, col);
      firstClickDone = true;
      startTimer();
    }

    openCell(row, col);
  }

  function onRightClick(e) {
    e.preventDefault();
    if (gameOver) return;
    const btn = e.currentTarget;
    const row = Number(btn.dataset.row);
    const col = Number(btn.dataset.col);
    toggleFlag(row, col);
  }

  function toggleFlag(row, col) {
    const key = idx(row, col);
    const btn = cells[key];
    if (btn.classList.contains('open')) return;
    if (flags.has(key)) {
      flags.delete(key);
      btn.classList.remove('flag');
      btn.textContent = '';
      btn.setAttribute('aria-label', 'не открыта');
    } else {
      flags.add(key);
      btn.classList.add('flag');
      btn.textContent = '⚑';
      btn.setAttribute('aria-label', 'помечена флагом');
    }
    mineCountEl.textContent = `Мины: ${mineCount - flags.size}`;
  }

  function openCell(row, col) {
    if (!inBounds(row, col)) return;
    const key = idx(row, col);
    const btn = cells[key];
    if (btn.classList.contains('open')) return;
    if (flags.has(key)) return;

    if (mines.has(key)) {
      // Boom
      revealMines(key);
      btn.classList.add('exploded');
      gameOver = true;
      stopTimer();
      return;
    }

    floodReveal(row, col);
    checkWin();
  }

  function revealMines(explodedKey) {
    cells.forEach((btn, i) => {
      if (mines.has(i)) {
        btn.classList.add('mine', 'open');
        if (i === explodedKey) btn.textContent = '💥'; else btn.textContent = '💣';
      }
      btn.disabled = true;
    });
  }

  function floodReveal(startRow, startCol) {
    const queue = [[startRow, startCol]];
    while (queue.length) {
      const [row, col] = queue.shift();
      const key = idx(row, col);
      const btn = cells[key];
      if (btn.classList.contains('open')) continue;
      if (flags.has(key)) continue;

      btn.classList.add('open');
      btn.disabled = true;
      btn.setAttribute('aria-label', 'открыта');
      revealedCount++;

      const count = countAdjacentMines(row, col);
      if (count > 0) {
        btn.textContent = String(count);
        btn.classList.add(`n${count}`);
      } else {
        btn.textContent = '';
        // add neighbors to queue
        for (const [r, c] of neighbors(row, col)) {
          const nKey = idx(r, c);
          const nBtn = cells[nKey];
          if (!nBtn.classList.contains('open') && !flags.has(nKey) && !mines.has(nKey)) {
            queue.push([r, c]);
          }
        }
      }
    }
  }

  function checkWin() {
    const totalSafe = gridSize * gridSize - mineCount;
    if (revealedCount >= totalSafe) {
      gameOver = true;
      stopTimer();
      // Auto reveal flags correctly
      cells.forEach((btn, i) => {
        if (!btn.classList.contains('open')) btn.disabled = true;
      });
    }
  }

  function reset() {
    gridSize = Number(sizeEl.value);
    mineCount = Math.min(Number(minesEl.value), gridSize * gridSize - 9);
    mineCountEl.textContent = `Мины: ${mineCount}`;
    createBoard();
  }

  // Events
  resetBtn.addEventListener('click', reset);
  sizeEl.addEventListener('change', reset);
  minesEl.addEventListener('change', reset);

  // Init
  reset();
})();



