// BidWise 목업 공용 그림 도구. 화면 파일은 BidWiseMock.render(기본 상태)만 부른다.
// 숫자와 공고는 Figma 목업에 있던 지어낸 예시 값이다. 실제 데이터가 아니다.
// 주소 파라미터: ?state=dashboard|region|empty|glossary, 팝오버 용어는 ?term=개찰 (용어 8종)

(function () {
  // Figma 원본의 지역 묶음 그대로다. 구현 기준은 16개 지역이다 (DESIGN 3장).
  const REGIONS = [
    { name: "경기", rate: "86.9", fill: "--blue-300", pts: "95,30 170,15 200,75 150,125 85,110" },
    { name: "강원", rate: "88.4", fill: "--blue-700", pts: "200,30 330,12 360,70 310,125 225,130 200,75" },
    { name: "충남", rate: "87.1", fill: "--blue-300", pts: "80,125 165,135 180,190 120,225 70,190" },
    { name: "충북", rate: "87.6", fill: "--blue-500", pts: "170,130 225,130 240,160 215,205 185,190" },
    { name: "경북", rate: "88.9", fill: "--blue-900", pts: "310,125 355,175 345,270 295,285 270,235 245,165" },
    { name: "전북", rate: "88.2", fill: "--blue-700", pts: "155,235 185,195 215,210 265,240 240,288 170,275" },
    { name: "전남", rate: "88.6", fill: "--blue-700", pts: "85,275 150,240 170,280 205,300 185,370 115,400 60,350" },
    { name: "경남", rate: "87.3", fill: "--blue-500", pts: "215,295 275,290 335,320 320,375 245,395 205,350" },
    { name: "제주", rate: "89.4", fill: "--blue-900", pts: "60,445 105,430 130,450 105,470 60,465" },
  ];

  const RANKS = [
    ["제주", "312건", "89.4", 100], ["경북·대구", "1,486건", "88.9", 88], ["전남·광주", "1,102건", "88.6", 75],
    ["강원", "874건", "88.4", 66], ["전북", "693건", "88.2", 60], ["경남·부산", "1,340건", "87.3", 34],
    ["충남·대전", "958건", "87.1", 24], ["경기·서울·인천", "2,317건", "86.9", 18],
  ];

  const CATEGORIES = [
    ["건축", "412건", "86.1", 30, ""], ["토목", "388건", "87.4", 62, ""], ["전기·통신설비", "254건", "88.0", 80, ""],
    ["소방설비", "187건", "88.0", 80, "추정"], ["조경", "144건", "87.2", 58, ""], ["기계설비", "121건", "86.8", 48, ""],
    ["상하수도", "98건", "89.1", 92, "추정"], ["미분류", "93건", "89.3", 96, "분류없음"],
  ];

  const BIDS = [
    { done: true, kind: "제한경쟁", title: "2026년 서울둘레길(누리길-수락산) 조성사업", where: "서울특별시 노원구 · 예산 4.38억", side: "27개사", rate: "90.2%" },
    { done: false, kind: "수의계약", title: "강서소방서 노후 배관 교체 공사", where: "서울특별시 강서구 · 예산 0.62억", side: "2026-09-18 개찰" },
    { done: true, kind: "일반경쟁", title: "수원 영통구 도로 재포장 공사(3공구)", where: "경기도 수원시 · 예산 12.4억", side: "41개사", rate: "87.6%" },
    { done: true, kind: "제한경쟁", title: "인천 미추홀구 어린이공원 리모델링", where: "인천광역시 미추홀구 · 예산 2.85억", side: "19개사", rate: "88.1%" },
    { done: false, kind: "일반경쟁", title: "고양시 덕양구 노후 상수관 정비", where: "경기도 고양시 · 예산 5.10억", side: "2026-09-22 개찰" },
  ];

  // 정의와 비유의 원본은 DESIGN 6장 용어 사전이다.
  const TERMS = {
    "낙찰률": { def: "공사를 따낸 금액이, 정부가 미리 잡아둔 기준 금액의 몇 %인지를 나타내는 값입니다.", formula: "낙찰금액 ÷ 예정가격 × 100", easy: "정부가 \"이 공사는 10억쯤 들겠다\"고 잡아둔 금액이 예정가격입니다. 실제로 9억에 공사를 따냈다면 낙찰률은 90%가 됩니다. 낙찰률이 낮을수록 그만큼 경쟁이 치열했다는 뜻입니다.", source: "sucsfbidRate" },
    "예정가격": { def: "발주처가 \"이 정도면 적정하다\"고 미리 정해 둔 상한 기준 금액. 낙찰률 계산의 분모.", easy: "물건 살 때 마음속으로 정해 둔 최대 지출 한도 같은 것.", source: "API 직접 미제공" },
    "추정가격": { def: "부가세와 관급자재를 빼고 순수하게 공사에만 드는 것으로 추정한 금액.", easy: "예정가격보다 앞 단계의, 더 날것에 가까운 견적.", source: "presmptPrce" },
    "공종(주공종)": { def: "그 공사가 어떤 종류의 일인지 나타내는 분류. 건축·토목·조경·소방설비 등.", easy: "같은 \"공사\"라도 건물 짓는 일과 도로 까는 일은 완전히 다른 종목.", source: "mainCnsttyNm" },
    "수의계약": { def: "경쟁 입찰 없이 발주처가 특정 업체를 골라 계약하는 방식. 주로 소규모 공사.", easy: "동네 가게에 바로 전화해서 맡기는 것에 가까움. 이 경우 주공종명이 비어 있습니다.", source: "cntrctCnclsMthdNm" },
    "제한·일반경쟁": { def: "자격을 갖춘 업체들이 가격을 써내 경쟁하는 방식. 제한경쟁은 참가 자격을 좁힌 것.", easy: "여러 곳에서 견적을 받아 가장 유리한 곳을 고르는 것.", source: "cntrctCnclsMthdNm" },
    "개찰": { def: "제출된 입찰서를 열어 낙찰자를 정하는 절차. 이 시점이 지나야 낙찰 결과가 생깁니다.", easy: "봉투를 여는 날. 그 전까지는 결과가 존재하지 않습니다.", source: "opengDt" },
    "유찰": { def: "참가 업체가 없거나 자격 미달로 낙찰자가 정해지지 않은 상태. 보통 재공고로 이어집니다.", easy: "응모가 없어 당첨자를 못 뽑은 상황.", source: "—" },
  };

  function header() {
    return `<div class="header">
      <div class="brand"><div class="logo"><i></i><i></i><i></i></div><div><h1>BidWise</h1><p>공공 공사 입찰 낙찰 분석</p></div></div>
      <div class="freshness"><span class="dot"></span>데이터 기준 2026-09-11 04:30</div>
    </div>`;
  }

  function filters(state) {
    const active = (on) => (on ? " active" : "");
    const period = state === "empty" ? 0 : 1;
    const seg = ["1개월", "3개월", "6개월", "1년"].map((p, i) => `<span class="${i === period ? "on" : ""}">${p}</span>`).join("");
    const region = state === "empty" ? "제주" : state === "region" ? "경기·서울·인천" : "전체 지역";
    const cat = state === "empty" ? "철도·궤도" : "전체 공종";
    const mthd = state === "empty" ? "일반경쟁" : "전체";
    const count = state === "empty" ? "0" : "12,847";
    return `<div class="filters">
      <div class="segment">${seg}</div>
      <div class="select${active(state === "empty" || state === "region")}">지역 <b>${region}</b></div>
      <div class="select${active(state === "empty")}">공종 <b>${cat}</b></div>
      <div class="select${active(state === "empty")}">계약방법<span class="q">?</span> <b>${mthd}</b></div>
      <div class="spacer"></div>
      <div class="count"><b>${count}</b> 건의 공고</div>
      <button class="btn">조건 초기화</button>
    </div>`;
  }

  function cards(state) {
    const blank = state === "empty";
    const v = (text, unit) => (blank ? "—" : `${text}<small>${unit}</small>`);
    const sub = (text) => (blank ? "조건에 맞는 데이터가 없습니다" : text);
    const open = state === "glossary" ? " open" : "";
    return `<div class="cards">
      <div class="card"><div class="label">전체 공고</div><div class="value">${v("12,847", "건")}</div><div class="sub">${sub("개찰완료 9,302 · 진행중 3,545")}</div></div>
      <div class="card" id="rate-card"><div class="label">평균 낙찰률<span class="q${open}">?</span></div><div class="value hot">${v("87.42", "%")}</div><div class="sub">${sub("개찰완료 9,302건 기준")}</div></div>
      <div class="card"><div class="label">총 예산 규모</div><div class="value">${v("4조 2,839", "억원")}</div><div class="sub">${sub("공고당 평균 3.3억원")}</div></div>
      <div class="card"><div class="label">평균 참가업체<span class="q">?</span></div><div class="value">${v("24.6", "개사")}</div><div class="sub">${sub("경쟁이 치열할수록 낙찰률 하락")}</div></div>
    </div>`;
  }

  function map(state) {
    const shapes = REGIONS.map((r) => {
      const sel = state === "region" && r.name === "경기" ? "sel" : "";
      const nums = r.pts.split(/[ ,]/).map(Number);
      const xs = nums.filter((_, i) => i % 2 === 0);
      const ys = nums.filter((_, i) => i % 2 === 1);
      const cx = xs.reduce((a, b) => a + b, 0) / xs.length;
      const cy = ys.reduce((a, b) => a + b, 0) / ys.length;
      const label = state === "empty" ? "" : `<text class="name ${sel}" x="${cx}" y="${cy - 4}">${r.name}</text><text class="rate ${sel}" x="${cx}" y="${cy + 12}">${r.rate}%</text>`;
      return `<polygon class="${sel}" points="${r.pts}" style="fill:var(${r.fill})"></polygon>${label}`;
    }).join("");
    const cls = state === "region" ? "map dim" : state === "empty" ? "map empty" : "map";
    return `<div class="${cls}"><svg viewBox="40 0 340 480" role="img" aria-label="지역별 낙찰률 지도 (그림)">${shapes}</svg></div>`;
  }

  function rank(state) {
    if (state === "empty") {
      return `<div class="rank"><h3>낙찰률 상위 지역</h3><p class="hint">개찰 완료 건 기준</p><p class="hint" style="text-align:center;padding:24px 0">표시할 순위가 없습니다</p></div>`;
    }
    const rows = RANKS.map(([n, c, r, w]) => `<div class="rank-row"><div class="top"><span>${n}<small>${c}</small></span><b>${r}%</b></div><div class="track"><i style="width:${w}%"></i></div></div>`).join("");
    return `<div class="rank"><h3>낙찰률 상위 지역</h3><p class="hint">개찰 완료 건 기준</p>${rows}</div>`;
  }

  function mapPanel(state) {
    const legend = ["--blue-100", "--blue-300", "--blue-500", "--blue-700", "--blue-900"].map((c) => `<i style="background:var(${c})"></i>`).join("");
    const right = state === "empty" ? `<button class="btn">데이터 없음</button>` : `<div class="legend"><span>낮음</span>${legend}<span>높음</span></div>`;
    return `<section class="panel">
      <div class="panel-head"><div><h2>지역별 평균 낙찰률</h2><p class="hint">지역을 선택하면 해당 지역의 공고 목록을 볼 수 있습니다</p></div>${right}</div>
      <div class="map-area">${map(state)}${rank(state)}</div>
    </section>`;
  }

  function categoryPanel(state) {
    const head = `<div class="panel-head"><div><h2>공종별 평균 낙찰률<span class="q">?</span></h2><p class="hint">주공종명이 없는 공고는 공고명에서 추정 분류</p></div></div>`;
    if (state === "empty") {
      return `<section class="panel">${head}<div class="empty-box">
        <div class="empty-icon"><i style="height:8px"></i><i style="height:14px"></i><i style="height:11px"></i></div>
        <h3>조건에 맞는 공고가 없습니다</h3>
        <p>제주 지역의 철도·궤도 일반경쟁 공고는 최근 1개월간 등록되지 않았습니다. 기간을 넓히거나 공종 조건을 완화해 보세요.</p>
        <div class="actions"><button class="btn primary">기간 1년으로 넓히기</button><button class="btn">조건 초기화</button></div>
      </div></section>`;
    }
    const rows = CATEGORIES.map(([n, c, r, w, t]) => {
      const tag = t ? `<span class="tag${t === "분류없음" ? " none" : ""}">${t}</span>` : "";
      return `<div class="bar-row"><div class="top"><span>${n}${tag}<small>${c}</small></span><b>${r}%</b></div><div class="track"><i style="width:${w}%"></i></div></div>`;
    }).join("");
    return `<section class="panel">${head}${rows}</section>`;
  }

  function bidCard(b, selected) {
    const badge = b.done ? `<span class="badge done">낙찰완료</span>` : `<span class="badge pending">개찰 전</span>`;
    const side = b.done ? `<span>${b.side}<span class="rate">${b.rate}</span></span>` : `<span>${b.side}</span>`;
    return `<div class="bid${selected ? " selected" : ""}"><div class="badges">${badge}<span class="badge">${b.kind}</span></div><h4>${b.title}</h4><div class="meta"><span>${b.where}</span>${side}</div></div>`;
  }

  function listPanel() {
    return `<section class="panel">
      <div class="panel-head"><div><h2>경기·서울·인천 <small style="font-size:11px;color:var(--text-muted);font-weight:400">2,317건</small></h2><p class="hint">평균 낙찰률 86.9% · 개찰완료 1,740건</p></div><button class="btn">닫기</button></div>
      <div class="sort"><span class="on">최신순</span><span>낙찰률순</span><span>금액순</span></div>
      ${BIDS.map((b) => bidCard(b)).join("")}
    </section>`;
  }

  function popover(termName) {
    const name = TERMS[termName] ? termName : "낙찰률";
    const t = TERMS[name];
    const formula = t.formula ? `<div class="formula">${t.formula}</div>` : "";
    return `<div class="popover" style="left:372px;top:262px">
      <header><b>${name}</b><span>닫기</span></header>
      <p>${t.def}</p>${formula}
      <div class="easy"><b>쉽게 말하면</b><p>${t.easy}</p></div>
      <div class="source">출처: 나라장터 API — ${t.source}</div>
    </div>`;
  }

  function dashboard(state, term) {
    const right = state === "region" ? listPanel() : categoryPanel(state);
    return `<div class="frame">${header()}${filters(state)}<main class="main">${cards(state)}<div class="panels">${mapPanel(state)}${right}</div></main>${state === "glossary" ? popover(term) : ""}</div>`;
  }

  function tokens() {
    const swatch = (name, value) => `<div class="swatch"><i style="background:${value}"></i><b>${name}</b><span>${value}</span></div>`;
    const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
    const set = (rows) => `<div class="swatches">${rows.map(([n, v]) => swatch(n, css(v))).join("")}</div>`;
    const sample = BIDS[0];
    const terms = Object.entries(TERMS).map(([n, t]) => `<div class="term"><header><b>${n}</b><code>${t.source}</code></header><p>${t.def}</p><div class="easy"><p>${t.easy}</p></div></div>`).join("");
    const types = [["Display / 큰 숫자", "30 / Light / -2%", "87.42", "font-size:30px;font-weight:300;letter-spacing:-.02em"], ["H1 / 화면 제목", "19 / SemiBold", "BidWise", "font-size:19px;font-weight:600"], ["H2 / 카드 제목", "16 / SemiBold", "지역별 평균 낙찰률", "font-size:16px;font-weight:600"], ["Body / 본문", "13 / Medium", sample.title, "font-size:13px;font-weight:500"], ["Caption / 보조", "11 / Regular", "개찰완료 9,302건 기준", "font-size:11px"]]
      .map(([a, b, c, s]) => `<div class="type-row"><div>${a}<small>${b}</small></div><div style="${s}">${c}</div></div>`).join("");
    const maps = [["상단 기간 선택", "Tabs 또는 ToggleGroup"], ["지역·공종·계약방법 필터", "Select"], ["요약 통계 4종", "Card + CardHeader/CardContent"], ["공고 카드", "Card + Badge"], ["낙찰완료 / 개찰 전 표시", "Badge (variant: outline)"], ["지역 랭킹 막대", "Progress"], ["닫기 · 조건 초기화", "Button (variant: outline / ghost)"], ["용어 툴팁", "Popover (클릭 유지형) — Tooltip 아님"]]
      .map(([a, b]) => `<div class="type-row"><div>${a}</div><div style="color:var(--text-muted)">${b}</div></div>`).join("");
    return `<div class="sheet">
      <h1>BidWise Design Tokens</h1>
      <h2>색상 토큰</h2><p class="hint">배경 · 데이터 · 강조 · 상태</p>
      ${set([["bg/base", "--bg-base"], ["bg/surface", "--bg-surface"], ["bg/elevated", "--bg-elevated"], ["border/subtle", "--border-subtle"], ["border/strong", "--border-strong"]])}
      ${set([["blue-100", "--blue-100"], ["blue-300", "--blue-300"], ["blue-500", "--blue-500"], ["blue-700", "--blue-700"], ["blue-900", "--blue-900"]])}
      ${set([["accent/safety", "--accent-safety"], ["status/done", "--status-done"], ["status/pending", "--status-pending"], ["text/primary", "--text-primary"], ["text/secondary", "--text-secondary"]])}
      <h2>타이포그래피</h2><p class="hint">IBM Plex Sans KR 단일 서체</p>${types}
      <h2>공고 카드 상태</h2><p class="hint">ERD의 1:0..1 관계가 화면에서 드러나는 지점 — 낙찰결과 레코드가 없으면 "개찰 전"</p>
      <div class="states">
        <div><div class="cap">낙찰완료 — result 있음</div>${bidCard(BIDS[0])}</div>
        <div><div class="cap">개찰 전 — result: null</div>${bidCard(BIDS[1])}</div>
        <div><div class="cap">선택됨 — 지도에서 클릭</div>${bidCard(BIDS[0], true)}</div>
      </div>
      <h2>shadcn/ui 컴포넌트 매핑</h2>${maps}
      <h2>용어 툴팁 사전</h2><p class="hint">이 분야를 모르는 사람도 화면을 이탈하지 않고 이해할 수 있도록, 용어 옆 ? 아이콘에 붙습니다</p>${terms}
    </div>`;
  }

  window.BidWiseMock = {
    render(defaultState) {
      const params = new URLSearchParams(location.search);
      const state = params.get("state") || defaultState;
      document.body.innerHTML = state === "tokens" ? tokens() : dashboard(state, params.get("term"));
    },
  };
})();
