<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Business Sale Tax Calculator</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #080C12;
      --surface: #0F1620;
      --card: #141E2E;
      --border: #1E2D45;
      --accent: #0DC3BE;
      --accent-dark: #09A09C;
      --accent-glow: rgba(13, 195, 190, 0.15);
      --text: #F0F4F8;
      --muted: #7A8FA8;
      --muted2: #4A5E78;
      --red: #F05252;
      --yellow: #F59E0B;
      --green: #10B981;
    }

    html, body {
      min-height: 100%;
      background: var(--bg);
      color: var(--text);
      font-family: 'Inter', system-ui, sans-serif;
      -webkit-font-smoothing: antialiased;
    }

    body {
      display: flex;
      align-items: flex-start;
      justify-content: center;
      min-height: 100vh;
      padding: 40px 16px;
    }

    .wrapper { width: 100%; max-width: 580px; }

    .screen { display: none; }
    .screen.active { display: block; animation: fadeUp 0.35s ease; }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(16px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    /* HEADER */
    .tool-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--accent-glow);
      border: 1px solid rgba(13,195,190,0.3);
      color: var(--accent);
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      padding: 6px 14px;
      border-radius: 100px;
      margin-bottom: 20px;
    }
    .tool-badge::before { content: ''; width: 7px; height: 7px; border-radius: 50%; background: var(--accent); }

    .tool-title {
      font-size: clamp(24px, 6vw, 34px);
      font-weight: 800;
      line-height: 1.2;
      letter-spacing: -0.03em;
      margin-bottom: 10px;
    }
    .tool-title span { color: var(--accent); }

    .tool-sub {
      font-size: 15px;
      color: var(--muted);
      line-height: 1.65;
      margin-bottom: 36px;
    }

    /* INPUTS */
    .section-label {
      font-size: 11px;
      font-weight: 700;
      color: var(--muted);
      letter-spacing: 0.1em;
      text-transform: uppercase;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .section-label::after {
      content: '';
      flex: 1;
      height: 1px;
      background: var(--border);
    }

    .input-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      margin-bottom: 14px;
    }

    .form-group { display: flex; flex-direction: column; gap: 7px; margin-bottom: 14px; }
    .form-group label { font-size: 12px; font-weight: 600; color: var(--muted); letter-spacing: 0.04em; text-transform: uppercase; }

    .input-wrap { position: relative; }
    .input-prefix {
      position: absolute;
      left: 14px; top: 50%;
      transform: translateY(-50%);
      color: var(--muted);
      font-size: 15px;
      font-weight: 600;
      pointer-events: none;
    }

    .form-input, .form-select {
      width: 100%;
      padding: 14px 15px;
      background: var(--card);
      border: 1.5px solid var(--border);
      border-radius: 10px;
      color: var(--text);
      font-family: inherit;
      font-size: 14px;
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
      -webkit-appearance: none;
    }
    .form-input.has-prefix { padding-left: 28px; }
    .form-select {
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%237A8FA8' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 14px center;
      padding-right: 36px;
      cursor: pointer;
    }
    .form-select option { background: #141E2E; }
    .form-input::placeholder { color: var(--muted2); }
    .form-input:focus, .form-select:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(13,195,190,0.12); }

    /* STRUCTURE SELECTOR */
    .structure-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      margin-bottom: 20px;
    }
    .struct-btn {
      padding: 14px 10px;
      background: var(--card);
      border: 1.5px solid var(--border);
      border-radius: 10px;
      color: var(--muted);
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s;
    }
    .struct-btn:hover { border-color: var(--muted2); color: var(--text); }
    .struct-btn.active { border-color: var(--accent); background: rgba(13,195,190,0.08); color: var(--accent); }
    .struct-name { font-size: 15px; margin-bottom: 3px; }
    .struct-note { font-size: 10px; font-weight: 400; color: var(--muted2); }
    .struct-btn.active .struct-note { color: rgba(13,195,190,0.7); }

    /* YEARS SLIDER */
    .slider-wrap { position: relative; margin-bottom: 6px; }
    .years-slider {
      width: 100%;
      -webkit-appearance: none;
      height: 6px;
      border-radius: 3px;
      background: var(--border);
      outline: none;
      cursor: pointer;
    }
    .years-slider::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 22px; height: 22px;
      border-radius: 50%;
      background: var(--accent);
      box-shadow: 0 0 0 4px rgba(13,195,190,0.2);
      cursor: pointer;
    }
    .years-slider::-moz-range-thumb {
      width: 22px; height: 22px;
      border: none;
      border-radius: 50%;
      background: var(--accent);
      cursor: pointer;
    }
    .slider-labels {
      display: flex;
      justify-content: space-between;
      font-size: 11px;
      color: var(--muted2);
      margin-top: 8px;
    }
    .slider-value {
      display: inline-block;
      padding: 3px 10px;
      background: var(--accent-glow);
      border: 1px solid rgba(13,195,190,0.3);
      color: var(--accent);
      font-size: 13px;
      font-weight: 700;
      border-radius: 6px;
      margin-bottom: 12px;
    }

    /* BTN */
    .btn-primary {
      display: block;
      width: 100%;
      padding: 17px 24px;
      background: var(--accent);
      color: #000;
      font-family: inherit;
      font-size: 15px;
      font-weight: 700;
      border: none;
      border-radius: 12px;
      cursor: pointer;
      text-align: center;
      letter-spacing: -0.01em;
      transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
      margin-top: 24px;
    }
    .btn-primary:hover { background: var(--accent-dark); transform: translateY(-1px); box-shadow: 0 8px 24px rgba(13,195,190,0.25); }
    .btn-primary:active { transform: translateY(0); }

    /* LEAD FORM */
    .form-title { font-size: clamp(20px, 5vw, 26px); font-weight: 800; line-height: 1.25; letter-spacing: -0.025em; margin-bottom: 8px; }
    .form-sub { font-size: 14px; color: var(--muted); line-height: 1.6; margin-bottom: 28px; }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .form-privacy { font-size: 11px; color: var(--muted2); line-height: 1.6; text-align: center; margin-top: 14px; }

    /* RESULTS */
    .results-hero {
      padding: 28px;
      background: linear-gradient(135deg, rgba(13,195,190,0.08) 0%, rgba(13,195,190,0.03) 100%);
      border: 1px solid rgba(13,195,190,0.25);
      border-radius: 16px;
      margin-bottom: 20px;
      text-align: center;
    }
    .results-hero-label { font-size: 12px; color: var(--accent); font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 8px; }
    .results-hero-amount { font-size: clamp(36px, 8vw, 52px); font-weight: 800; letter-spacing: -0.04em; color: var(--accent); }
    .results-hero-sub { font-size: 13px; color: var(--muted); margin-top: 6px; }

    .results-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 20px;
    }
    .result-stat {
      padding: 18px;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
    }
    .result-stat-label { font-size: 11px; color: var(--muted); font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 8px; }
    .result-stat-value { font-size: 20px; font-weight: 800; letter-spacing: -0.02em; }
    .result-stat-note { font-size: 11px; color: var(--muted2); margin-top: 4px; }

    /* BAR VISUAL */
    .bar-section {
      padding: 24px;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      margin-bottom: 20px;
    }
    .bar-section-title { font-size: 13px; font-weight: 600; color: var(--muted); margin-bottom: 20px; }

    .bar-track {
      height: 40px;
      background: rgba(240,82,82,0.15);
      border-radius: 8px;
      overflow: hidden;
      position: relative;
      margin-bottom: 16px;
    }
    .bar-fill {
      height: 100%;
      background: var(--accent);
      border-radius: 8px;
      transition: width 1s cubic-bezier(0.4,0,0.2,1);
      position: relative;
      display: flex;
      align-items: center;
      padding-left: 12px;
      min-width: 10px;
    }
    .bar-fill-label {
      font-size: 12px;
      font-weight: 700;
      color: #000;
      white-space: nowrap;
      overflow: hidden;
    }

    .bar-legend {
      display: flex;
      gap: 20px;
    }
    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: var(--muted);
    }
    .legend-dot { width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; }

    .disclaimer {
      font-size: 11px;
      color: var(--muted2);
      line-height: 1.7;
      padding: 16px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      margin-bottom: 20px;
    }

    .cta-note { font-size: 12px; color: var(--muted2); text-align: center; margin-top: 10px; line-height: 1.6; }

    @media (max-width: 420px) {
      .input-grid { grid-template-columns: 1fr; }
      .results-grid { grid-template-columns: 1fr; }
      .form-row { grid-template-columns: 1fr; }
      .structure-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
<div class="wrapper">

  <!-- SCREEN: CALCULATOR INPUTS -->
  <div class="screen active" id="screen-calc">
    <div class="tool-badge">Tax Calculator</div>
    <h1 class="tool-title">What will you <span>actually keep</span><br>after selling?</h1>
    <p class="tool-sub">Enter your sale details to see a breakdown of federal and state taxes — and your real net proceeds.</p>

    <div class="section-label">Sale Details</div>

    <div class="form-group">
      <label>Estimated Sale Price</label>
      <div class="input-wrap">
        <span class="input-prefix">$</span>
        <input class="form-input has-prefix" type="text" id="sale-price" placeholder="2,500,000" inputmode="numeric">
      </div>
    </div>

    <div class="form-group">
      <label>Business Structure</label>
      <div class="structure-grid">
        <button class="struct-btn active" data-struct="llc" onclick="selectStruct(this)">
          <div class="struct-name">LLC</div>
          <div class="struct-note">Pass-through</div>
        </button>
        <button class="struct-btn" data-struct="s-corp" onclick="selectStruct(this)">
          <div class="struct-name">S-Corp</div>
          <div class="struct-note">Pass-through</div>
        </button>
        <button class="struct-btn" data-struct="c-corp" onclick="selectStruct(this)">
          <div class="struct-name">C-Corp</div>
          <div class="struct-note">Double tax risk</div>
        </button>
      </div>
    </div>

    <div class="form-group">
      <label>Years Owned</label>
      <div class="slider-value" id="years-display">3 years</div>
      <div class="slider-wrap">
        <input type="range" class="years-slider" id="years-slider" min="0" max="30" value="3" oninput="updateYears(this.value)">
      </div>
      <div class="slider-labels"><span>Less than 1 yr</span><span>30 years</span></div>
    </div>

    <div class="form-group">
      <label>State of Residence</label>
      <select class="form-select" id="state-select">
        <option value="" disabled selected>Select your state</option>
        <option value="AL,0.05">Alabama (5.0%)</option>
        <option value="AK,0">Alaska (0%)</option>
        <option value="AZ,0.025">Arizona (2.5%)</option>
        <option value="AR,0.044">Arkansas (4.4%)</option>
        <option value="CA,0.133">California (13.3%)</option>
        <option value="CO,0.044">Colorado (4.4%)</option>
        <option value="CT,0.0699">Connecticut (6.99%)</option>
        <option value="DE,0.066">Delaware (6.6%)</option>
        <option value="FL,0">Florida (0%)</option>
        <option value="GA,0.0549">Georgia (5.49%)</option>
        <option value="HI,0.0725">Hawaii (7.25%)</option>
        <option value="ID,0.058">Idaho (5.8%)</option>
        <option value="IL,0.0495">Illinois (4.95%)</option>
        <option value="IN,0.0305">Indiana (3.05%)</option>
        <option value="IA,0.06">Iowa (6.0%)</option>
        <option value="KS,0.057">Kansas (5.7%)</option>
        <option value="KY,0.04">Kentucky (4.0%)</option>
        <option value="LA,0.03">Louisiana (3.0%)</option>
        <option value="ME,0.0715">Maine (7.15%)</option>
        <option value="MD,0.0575">Maryland (5.75%)</option>
        <option value="MA,0.05">Massachusetts (5.0%)</option>
        <option value="MI,0.0425">Michigan (4.25%)</option>
        <option value="MN,0.0985">Minnesota (9.85%)</option>
        <option value="MS,0.047">Mississippi (4.7%)</option>
        <option value="MO,0.0495">Missouri (4.95%)</option>
        <option value="MT,0.0675">Montana (6.75%)</option>
        <option value="NE,0.0584">Nebraska (5.84%)</option>
        <option value="NV,0">Nevada (0%)</option>
        <option value="NH,0">New Hampshire (0%)</option>
        <option value="NJ,0.1075">New Jersey (10.75%)</option>
        <option value="NM,0.059">New Mexico (5.9%)</option>
        <option value="NY,0.109">New York (10.9%)</option>
        <option value="NC,0.045">North Carolina (4.5%)</option>
        <option value="ND,0.025">North Dakota (2.5%)</option>
        <option value="OH,0.035">Ohio (3.5%)</option>
        <option value="OK,0.0475">Oklahoma (4.75%)</option>
        <option value="OR,0.099">Oregon (9.9%)</option>
        <option value="PA,0.0307">Pennsylvania (3.07%)</option>
        <option value="RI,0.0599">Rhode Island (5.99%)</option>
        <option value="SC,0.065">South Carolina (6.5%)</option>
        <option value="SD,0">South Dakota (0%)</option>
        <option value="TN,0">Tennessee (0%)</option>
        <option value="TX,0">Texas (0%)</option>
        <option value="UT,0.0455">Utah (4.55%)</option>
        <option value="VT,0.0875">Vermont (8.75%)</option>
        <option value="VA,0.0575">Virginia (5.75%)</option>
        <option value="WA,0.07">Washington (7.0%)</option>
        <option value="WV,0.065">West Virginia (6.5%)</option>
        <option value="WI,0.0765">Wisconsin (7.65%)</option>
        <option value="WY,0">Wyoming (0%)</option>
        <option value="DC,0.1075">Washington D.C. (10.75%)</option>
      </select>
    </div>

    <button class="btn-primary" onclick="calculateAndContinue()">Calculate My Net Proceeds →</button>
  </div>

  <!-- SCREEN: LEAD FORM -->
  <div class="screen" id="screen-form">
    <div class="form-title">See your full<br>tax breakdown.</div>
    <p class="form-sub">Enter your details and we'll show you exactly how much you'll walk away with — and how to keep more.</p>
    <form id="lead-form" onsubmit="submitLead(event)">
      <div class="form-row">
        <div class="form-group">
          <label>First Name</label>
          <input class="form-input" type="text" name="firstName" placeholder="Jake" required>
        </div>
        <div class="form-group">
          <label>Last Name</label>
          <input class="form-input" type="text" name="lastName" placeholder="Mattoon" required>
        </div>
      </div>
      <div class="form-group">
        <label>Email Address</label>
        <input class="form-input" type="email" name="email" placeholder="jake@yourcompany.com" required>
      </div>
      <div class="form-group">
        <label>Phone Number</label>
        <input class="form-input" type="tel" name="phone" placeholder="(555) 000-0000" required>
      </div>
      <div class="form-group">
        <label>Estimated Investable Assets</label>
        <select class="form-select" name="assets" required>
          <option value="" disabled selected>Select a range</option>
          <option value="under-100k">Under $100,000</option>
          <option value="100k-250k">$100,000 – $250,000</option>
          <option value="250k-500k">$250,000 – $500,000</option>
          <option value="500k-1m">$500,000 – $1,000,000</option>
          <option value="1m-2.5m">$1,000,000 – $2,500,000</option>
          <option value="2.5m-plus">$2,500,000+</option>
        </select>
      </div>
      <button class="btn-primary" type="submit">Show My Results →</button>
      <p class="form-privacy">🔒 Your information is never sold or shared.</p>
    </form>
  </div>

  <!-- SCREEN: RESULTS -->
  <div class="screen" id="screen-results">
    <div class="results-hero">
      <div class="results-hero-label">Estimated Net Proceeds</div>
      <div class="results-hero-amount" id="res-net"></div>
      <div class="results-hero-sub" id="res-net-sub"></div>
    </div>

    <div class="results-grid">
      <div class="result-stat">
        <div class="result-stat-label">Gross Sale Price</div>
        <div class="result-stat-value" id="res-gross"></div>
        <div class="result-stat-note">Before taxes</div>
      </div>
      <div class="result-stat">
        <div class="result-stat-label">Total Tax Burden</div>
        <div class="result-stat-value" style="color: var(--red)" id="res-total-tax"></div>
        <div class="result-stat-note" id="res-eff-rate"></div>
      </div>
      <div class="result-stat">
        <div class="result-stat-label">Federal Capital Gains</div>
        <div class="result-stat-value" id="res-fed"></div>
        <div class="result-stat-note" id="res-fed-rate"></div>
      </div>
      <div class="result-stat">
        <div class="result-stat-label">State Tax</div>
        <div class="result-stat-value" id="res-state"></div>
        <div class="result-stat-note" id="res-state-rate"></div>
      </div>
    </div>

    <div class="bar-section">
      <div class="bar-section-title">Gross Sale Price vs. What You Keep</div>
      <div class="bar-track">
        <div class="bar-fill" id="bar-fill">
          <span class="bar-fill-label" id="bar-fill-label"></span>
        </div>
      </div>
      <div class="bar-legend">
        <div class="legend-item">
          <div class="legend-dot" style="background: var(--accent)"></div>
          <span>Net proceeds</span>
        </div>
        <div class="legend-item">
          <div class="legend-dot" style="background: rgba(240,82,82,0.4)"></div>
          <span>Tax burden</span>
        </div>
      </div>
    </div>

    <div class="disclaimer">
      <strong>Disclaimer:</strong> This estimate assumes a long-term capital asset sale and applies top-bracket rates. Actual tax liability depends on your specific situation, deductions, basis, installment structure, and other factors. Consult a tax professional before making financial decisions.
    </div>

    <button class="btn-primary" onclick="window.location.href='#review'">Get a Free Exit Review →</button>
    <p class="cta-note">Strategic planning can often reduce your tax burden by 30–50%. A free consultation costs nothing.</p>
  </div>

</div>
<script>
  let selectedStruct = 'llc';
  let calcResults = null;

  function fmt(n) {
    return '$' + Math.round(n).toLocaleString('en-US');
  }
  function pct(n) {
    return (n * 100).toFixed(1) + '%';
  }

  function selectStruct(btn) {
    document.querySelectorAll('.struct-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedStruct = btn.dataset.struct;
  }

  function updateYears(val) {
    const label = val == 0 ? 'Less than 1 year' : val == 1 ? '1 year' : val + ' years';
    document.getElementById('years-display').textContent = label;
  }

  function parseAmount(str) {
    return parseFloat(str.replace(/[^0-9.]/g, ''));
  }

  function calculateTax(salePrice, structure, years, stateRate) {
    const longTerm = years >= 1;
    let federalRate;
    let federalNote;

    if (structure === 'c-corp') {
      // Asset sale double tax: 21% corp tax + ~20% LTCG on remaining distribution
      federalRate = 0.398;
      federalNote = 'C-Corp effective rate (double tax)';
    } else {
      if (longTerm) {
        // 20% LTCG + 3.8% NIIT for high earners
        federalRate = 0.238;
        federalNote = '20% LTCG + 3.8% NIIT';
      } else {
        // 37% ordinary + 3.8% NIIT
        federalRate = 0.408;
        federalNote = '37% short-term + 3.8% NIIT';
      }
    }

    const federalTax = salePrice * federalRate;
    const stateTax = salePrice * stateRate;
    const totalTax = federalTax + stateTax;
    const netProceeds = salePrice - totalTax;
    const effectiveRate = totalTax / salePrice;

    return { federalTax, stateTax, totalTax, netProceeds, federalRate, stateRate, effectiveRate, federalNote };
  }

  function calculateAndContinue() {
    const rawPrice = document.getElementById('sale-price').value;
    const salePrice = parseAmount(rawPrice);
    if (!salePrice || salePrice <= 0) {
      alert('Please enter a valid sale price.');
      return;
    }
    const stateVal = document.getElementById('state-select').value;
    if (!stateVal) {
      alert('Please select your state of residence.');
      return;
    }
    const stateRate = parseFloat(stateVal.split(',')[1]);
    const years = parseInt(document.getElementById('years-slider').value);

    calcResults = { salePrice, structure: selectedStruct, years, stateRate };
    calcResults.taxes = calculateTax(salePrice, selectedStruct, years, stateRate);

    show('screen-form');
  }

  function submitLead(e) {
    e.preventDefault();
    const fd = new FormData(e.target);
    const leadData = {
      firstName: fd.get('firstName'),
      lastName: fd.get('lastName'),
      email: fd.get('email'),
      phone: fd.get('phone'),
      assets: fd.get('assets'),
      calculatorInputs: {
        salePrice: calcResults.salePrice,
        structure: calcResults.structure,
        yearsOwned: calcResults.years,
        stateRate: calcResults.stateRate
      },
      calculatorResults: {
        federalTax: calcResults.taxes.federalTax,
        stateTax: calcResults.taxes.stateTax,
        totalTax: calcResults.taxes.totalTax,
        netProceeds: calcResults.taxes.netProceeds,
        effectiveRate: calcResults.taxes.effectiveRate
      },
      tool: 'sale-proceeds-calculator',
      timestamp: new Date().toISOString()
    };
    console.log('[Lead Capture — Sale Proceeds Calculator]', leadData);
    renderResults();
    show('screen-results');
  }

  function renderResults() {
    const t = calcResults.taxes;
    const netPct = (t.netProceeds / calcResults.salePrice) * 100;

    document.getElementById('res-net').textContent = fmt(t.netProceeds);
    document.getElementById('res-net-sub').textContent = `You keep ${netPct.toFixed(1)}% of your gross sale price`;
    document.getElementById('res-gross').textContent = fmt(calcResults.salePrice);
    document.getElementById('res-total-tax').textContent = fmt(t.totalTax);
    document.getElementById('res-eff-rate').textContent = `${pct(t.effectiveRate)} effective rate`;
    document.getElementById('res-fed').textContent = fmt(t.federalTax);
    document.getElementById('res-fed-rate').textContent = `${pct(t.federalRate)} federal rate`;
    document.getElementById('res-state').textContent = fmt(t.stateTax);
    document.getElementById('res-state-rate').textContent = t.stateRate === 0 ? 'No state income tax' : `${pct(t.stateRate)} state rate`;

    // Animate bar
    const fillPct = Math.max(5, netPct);
    const fill = document.getElementById('bar-fill');
    const fillLabel = document.getElementById('bar-fill-label');
    fill.style.width = '0%';
    setTimeout(() => {
      fill.style.width = fillPct + '%';
      if (fillPct > 20) fillLabel.textContent = `${netPct.toFixed(0)}% kept`;
    }, 100);
  }

  function show(id) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    window.scrollTo(0, 0);
  }

  // Format sale price input as user types
  document.getElementById('sale-price').addEventListener('input', function() {
    const raw = parseAmount(this.value);
    if (raw && !isNaN(raw)) {
      const cursor = this.selectionStart;
      this.value = raw.toLocaleString('en-US');
    }
  });
</script>
</body>
</html>
