(function () {
  const canvas = document.getElementById('noiseChart');
  const ctx = canvas.getContext('2d');

  // 내부 패딩(라벨/눈금 공간)
  const PADDING = { top: 28, right: 28, bottom: 36, left: 64 };

  // X축 라벨 (피그마 시안과 유사)
  const xTicks = ['5:18','5:20','5:22','5:24','5:26','5:28','5:30','5:32','5:34','5:36','5:38','5:40'];

  // 0~100 dB 범위의 샘플 값 (시안 곡선 형태 근사)
  let data = [72, 22, 38, 32, 48, 16, 76, 44, 50, 88, 40];

  // 고해상도 렌더링
  function fitCanvas() {
    const ratio = Math.max(window.devicePixelRatio || 1, 1);
    const cssW = canvas.clientWidth;
    const cssH = canvas.clientHeight;
    canvas.width = Math.floor(cssW * ratio);
    canvas.height = Math.floor(cssH * ratio);
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0); // 좌표계를 CSS 픽셀 기준으로
  }

  function yScale(value, h) {
    // dB: 0(바닥) ~ 100(천장)
    const plotH = h - PADDING.top - PADDING.bottom;
    return PADDING.top + (1 - (value / 100)) * plotH;
  }
  function xScale(index, w) {
    const plotW = w - PADDING.left - PADDING.right;
    const step = plotW / (xTicks.length - 1);
    return PADDING.left + index * step;
  }

  function drawGrid(w, h) {
    ctx.save();
    ctx.strokeStyle = 'rgba(138,146,168,0.35)';
    ctx.lineWidth = 1;

    // 수평 6줄 (0,20,40,60,80,100)
    const ySteps = [100,80,60,40,20,0];
    ySteps.forEach(v => {
      const y = yScale(v, h);
      ctx.beginPath(); ctx.moveTo(PADDING.left, y); ctx.lineTo(w - PADDING.right, y); ctx.stroke();
    });

    // 수직 반복선 (tick 간격 가까이)
    const count = xTicks.length;
    for (let i = 0; i < count; i++) {
      const x = xScale(i, w);
      ctx.beginPath(); ctx.moveTo(x, PADDING.top); ctx.lineTo(x, h - PADDING.bottom); ctx.stroke();
    }

    // Y 라벨
    ctx.fillStyle = '#8A92A8';
    ctx.font = '12px Inter, system-ui';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ySteps.forEach(v => {
      const y = yScale(v, h);
      ctx.fillText(String(v), PADDING.left - 10, y);
    });

    // X 라벨
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    xTicks.forEach((t, i) => {
      const x = xScale(i, w);
      ctx.fillText(t, x, h - PADDING.bottom + 8);
    });

    ctx.restore();
  }

  function drawThreshold(w, h) {
    // 기준선(빨간) – 50dB 근처
    const y = yScale(50, h);
    ctx.save();
    ctx.strokeStyle = '#ff3a3a';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(PADDING.left, y);
    ctx.lineTo(w - PADDING.right, y);
    ctx.stroke();
    ctx.restore();
  }

  function drawAreaAndLine(w, h) {
    const plotLeft = PADDING.left;
    const plotRight = w - PADDING.right;
    const plotBottom = h - PADDING.bottom;

    // 좌표 준비
    const pts = data.map((v, i) => [xScale(i, w), yScale(v, h)]);

    // 영역 그라디언트
    const grad = ctx.createLinearGradient(0, PADDING.top, 0, plotBottom);
    grad.addColorStop(0, 'rgba(194,244,103,0.50)');
    grad.addColorStop(1, 'rgba(194,244,103,0.05)');

    // 영역
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);

    // 부드럽게: quadratic curve
    for (let i = 1; i < pts.length; i++) {
      const [x, y] = pts[i];
      const [px, py] = pts[i - 1];
      const cx = (px + x) / 2; // 중간점
      ctx.quadraticCurveTo(px, py, cx, (py + y) / 2);
      ctx.quadraticCurveTo(cx, (py + y) / 2, x, y);
    }

    // 바닥으로 닫기
    ctx.lineTo(plotRight, plotBottom);
    ctx.lineTo(plotLeft, plotBottom);
    ctx.closePath();

    ctx.fillStyle = grad;
    ctx.fill();

    // 윤곽선(연두)
    ctx.strokeStyle = '#C2F467';
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.restore();

    // 포인트
    ctx.save();
    for (const [x, y] of pts) {
      ctx.globalAlpha = 0.25;
      ctx.fillStyle = '#C2F467';
      ctx.beginPath(); ctx.arc(x, y, 8, 0, Math.PI * 2); ctx.fill();

      ctx.globalAlpha = 1;
      ctx.beginPath(); ctx.arc(x, y, 4, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 1;
      ctx.stroke();
    }
    ctx.restore();
  }

  function draw() {
    fitCanvas();
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;

    // 배경
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = '#2d3037';
    ctx.fillRect(0, 0, w, h);

    drawGrid(w, h);
    drawThreshold(w, h);
    drawAreaAndLine(w, h);
  }

  // 반응형 리사이즈
  window.addEventListener('resize', draw);
  draw();

  // (선택) 데모 애니메이션: 약간의 변동을 주어 실시간 느낌
  let t = 0;
  function animate() {
    t += 0.02;
    data = data.map((v, i) => {
      const jitter = Math.sin(t + i * 0.6) * 1.5;
      return Math.max(0, Math.min(100, v + jitter));
    });
    draw();
    requestAnimationFrame(animate);
  }
  animate();
})();


const canvas = document.getElementById('noiseChart');
if (!canvas) return;  // 캔버스 없으면 그냥 종료
const ctx = canvas.getContext('2d');