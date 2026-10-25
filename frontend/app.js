/**
 * TrustLens AI — Frontend Application Logic
 * Vanilla JavaScript (ES6+) with zero external framework dependencies.
 * In-memory session state only (zero persistent client storage).
 */

(() => {
  'use strict';

  // API Base Resolution:
  // If served over HTTP/HTTPS (on port 8000, 8081, etc.), use same-origin relative path "".
  // If opened as a local file (file://), default to http://127.0.0.1:8000.
  const API_BASE = (window.location.protocol && window.location.protocol.startsWith('http'))
    ? ''
    : 'http://127.0.0.1:8000';

  const GAUGE_CIRCUMFERENCE = 2 * Math.PI * 68; // ~427.26
  const MAX_HISTORY_ITEMS = 5;

  // In-Memory Session Storage ONLY (resets on page reload / tab close)
  let recentAnalyses = [];
  let currentInputType = 'job_offer';
  let isAnalyzing = false;
  let lastAnalysisResult = null;

  // DOM Elements — Inputs & Controls
  const messageInput = document.getElementById('messageInput');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const analyzeBtnText = document.getElementById('analyzeBtnText');
  const analyzeSpinner = document.getElementById('analyzeSpinner');
  const analyzeIcon = document.getElementById('analyzeIcon');
  const clearBtn = document.getElementById('clearBtn');
  const charCount = document.getElementById('charCount');
  const wordCount = document.getElementById('wordCount');
  const inputAlert = document.getElementById('inputAlert');
  const inputAlertText = document.getElementById('inputAlertText');

  // DOM Elements — Recent Analyses
  const recentCountBadge = document.getElementById('recentCountBadge');
  const clearHistoryBtn = document.getElementById('clearHistoryBtn');
  const clearConfirmBox = document.getElementById('clearConfirmBox');
  const confirmClearBtn = document.getElementById('confirmClearBtn');
  const cancelClearBtn = document.getElementById('cancelClearBtn');
  const recentAnalysesList = document.getElementById('recentAnalysesList');

  // DOM Elements — Views & Route Links
  const homeView = document.getElementById('homeView');
  const analyzerView = document.getElementById('analyzerView');
  const brandHomeBtn = document.getElementById('brandHomeBtn');
  const navLinkHome = document.getElementById('navLinkHome');
  const navLinkAnalyzer = document.getElementById('navLinkAnalyzer');
  const navLinkHowItWorks = document.getElementById('navLinkHowItWorks');
  const headerCtaBtn = document.getElementById('headerCtaBtn');
  const heroAnalyzeCta = document.getElementById('heroAnalyzeCta');
  const heroHowItWorksCta = document.getElementById('heroHowItWorksCta');
  const bottomAnalyzeCta = document.getElementById('bottomAnalyzeCta');
  const bottomHowItWorksCta = document.getElementById('bottomHowItWorksCta');
  const sidebarNavHome = document.getElementById('sidebarNavHome');
  const footerLinkHome = document.getElementById('footerLinkHome');
  const footerLinkAnalyzer = document.getElementById('footerLinkAnalyzer');
  const footerLinkHowItWorks = document.getElementById('footerLinkHowItWorks');

  // DOM Elements — Navigation & Workspace
  const navAnalyzer = document.getElementById('navAnalyzer');
  const navRecent = document.getElementById('navRecent');
  const navHowItWorks = document.getElementById('navHowItWorks');
  const sidebarRecentCount = document.getElementById('sidebarRecentCount');
  const resultsEmptyState = document.getElementById('resultsEmptyState');

  // DOM Elements — Results
  const resultsSection = document.getElementById('resultsSection');
  const historicalBanner = document.getElementById('historicalBanner');
  const historicalTimestamp = document.getElementById('historicalTimestamp');
  const historicalDismissBtn = document.getElementById('historicalDismissBtn');
  const metaId = document.getElementById('metaId');
  const metaTypeBadge = document.getElementById('metaTypeBadge');
  const metaTimestamp = document.getElementById('metaTimestamp');
  const scoreNumber = document.getElementById('scoreNumber');
  const gaugeFill = document.getElementById('gaugeFill');
  const riskLevelBadge = document.getElementById('riskLevelBadge');
  const riskLevelText = document.getElementById('riskLevelText');
  const scoreSubtext = document.getElementById('scoreSubtext');
  const verdictHeadline = document.getElementById('verdictHeadline');
  const verdictSummary = document.getElementById('verdictSummary');
  const findingsCount = document.getElementById('findingsCount');
  const positiveCount = document.getElementById('positiveCount');
  const findingsBadge = document.getElementById('findingsBadge');
  const findingsList = document.getElementById('findingsList');
  const positiveSignalsContainer = document.getElementById('positiveSignalsContainer');
  const positiveSignalsList = document.getElementById('positiveSignalsList');
  const recommendationsList = document.getElementById('recommendationsList');
  const disclaimerText = document.getElementById('disclaimerText');
  const copyReportBtn = document.getElementById('copyReportBtn');
  const analyzeAnotherBtn = document.getElementById('analyzeAnotherBtn');

  // DOM Elements — Samples
  const sampleLegitBtn = document.getElementById('sampleLegitBtn');
  const sampleFeeBtn = document.getElementById('sampleFeeBtn');
  const sampleOtpBtn = document.getElementById('sampleOtpBtn');
  const sampleTelegramBtn = document.getElementById('sampleTelegramBtn');

  // DOM Elements — Modal & Toast
  const howItWorksBtn = document.getElementById('howItWorksBtn');
  const howItWorksModal = document.getElementById('howItWorksModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const closeModalFooterBtn = document.getElementById('closeModalFooterBtn');
  const toastNotification = document.getElementById('toastNotification');
  const toastMessage = document.getElementById('toastMessage');

  // Sample Payloads
  const SAMPLES = {
    legitimate: {
      type: 'job_offer',
      text: `Dear Alex,

Thank you for submitting your application for the Summer 2026 Software Engineering Internship at Acorn Systems. We have reviewed your resume and would like to invite you to complete a technical coding assessment through our portal at https://careers.acorn.edu/internships.

Our team will review applications over the next two weeks. We do not charge any fee for applications or onboarding.

Best regards,
University Talent Acquisition Team
Acorn Systems`
    },
    fee_scam: {
      type: 'job_offer',
      text: `Congratulations! You have been selected for the Data Analyst Internship at Tech Global. Your stipend will be $3,500/month working from home.

To confirm your laptop dispatch and secure your placement, you are required to pay a registration fee of $150 refundable deposit before Monday via Zelle or wire transfer.

Immediate response required within 24 hours or the offer will be revoked!`
    },
    otp_theft: {
      type: 'scholarship',
      text: `URGENT: National Merit Academic Scholarship Notification. Your grant of $4,500 has been approved for immediate disbursement to your student account.

Please provide the 6-digit verification code (OTP) received on your mobile phone to verify your identity and release the funds today.

Do not contact campus finance as this is processed directly by the central scholarship board.`
    },
    telegram_phish: {
      type: 'message',
      text: `Hello! Google HR is hiring remote students for simple product review tasks. Earn $500 daily for 1 hour of typing. No interview needed! 100% guaranteed selection.

Contact our recruiter immediately on Telegram @google_talent_recruiter or visit http://192.168.1.55/google-careers. Payment made via Bitcoin.`
    }
  };

  /**
   * Application Initialization
   */
  function init() {
    setupRouting();
    setupSidebarNav();
    setupTypeSelector();
    setupInputListeners();
    setupSampleButtons();
    setupHistoryControls();
    setupModal();
    setupActions();
    updateTextMetrics();
    renderHistory();
  }

  /**
   * Client-Side View Routing (Home vs. Analyzer)
   * Uses URL hash (#home, #analyzer) for direct deep-linking, refresh persistence,
   * and full browser Back / Forward compatibility without page reloads.
   */
  function setupRouting() {
    if (navLinkHome) {
      navLinkHome.addEventListener('click', () => switchView('home'));
    }
    if (navLinkAnalyzer) {
      navLinkAnalyzer.addEventListener('click', () => switchView('analyzer'));
    }
    if (navLinkHowItWorks) {
      navLinkHowItWorks.addEventListener('click', openModal);
    }
    if (brandHomeBtn) {
      brandHomeBtn.addEventListener('click', (e) => {
        e.preventDefault();
        switchView('home');
      });
    }
    if (headerCtaBtn) {
      headerCtaBtn.addEventListener('click', () => switchView('analyzer', true));
    }

    // Landing page CTA triggers
    if (heroAnalyzeCta) {
      heroAnalyzeCta.addEventListener('click', () => switchView('analyzer', true));
    }
    if (heroHowItWorksCta) {
      heroHowItWorksCta.addEventListener('click', openModal);
    }
    if (bottomAnalyzeCta) {
      bottomAnalyzeCta.addEventListener('click', () => switchView('analyzer', true));
    }
    if (bottomHowItWorksCta) {
      bottomHowItWorksCta.addEventListener('click', openModal);
    }

    // Sidebar navigation home button
    if (sidebarNavHome) {
      sidebarNavHome.addEventListener('click', () => switchView('home'));
    }

    // Footer navigation links
    if (footerLinkHome) {
      footerLinkHome.addEventListener('click', () => switchView('home'));
    }
    if (footerLinkAnalyzer) {
      footerLinkAnalyzer.addEventListener('click', () => switchView('analyzer'));
    }
    if (footerLinkHowItWorks) {
      footerLinkHowItWorks.addEventListener('click', openModal);
    }

    // Popstate & hashchange events for browser back/forward buttons
    window.addEventListener('hashchange', handleRouteFromHash);
    window.addEventListener('popstate', handleRouteFromHash);

    // Initial check on load
    handleRouteFromHash();
  }

  function handleRouteFromHash() {
    const hash = (window.location.hash || '').toLowerCase();
    if (hash === '#analyzer') {
      applyView('analyzer', false);
    } else {
      applyView('home', false);
    }
  }

  function switchView(viewName, focusInput = false) {
    if (viewName === 'analyzer') {
      if (window.location.hash.toLowerCase() !== '#analyzer') {
        window.history.pushState(null, '', '#analyzer');
      }
      applyView('analyzer', focusInput);
    } else {
      if (window.location.hash.toLowerCase() !== '#home' && window.location.hash !== '') {
        window.history.pushState(null, '', '#home');
      }
      applyView('home', false);
    }
  }

  function applyView(viewName, focusInput = false) {
    if (viewName === 'analyzer') {
      if (homeView) homeView.classList.add('hidden');
      if (analyzerView) analyzerView.classList.remove('hidden');
      if (navLinkHome) navLinkHome.classList.remove('active');
      if (navLinkAnalyzer) navLinkAnalyzer.classList.add('active');
      if (headerCtaBtn) headerCtaBtn.classList.add('hidden');
      setNavActive(navAnalyzer);

      if (focusInput) {
        setTimeout(() => {
          if (messageInput) {
            messageInput.focus();
            messageInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }, 60);
      } else {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    } else {
      if (analyzerView) analyzerView.classList.add('hidden');
      if (homeView) homeView.classList.remove('hidden');
      if (navLinkHome) navLinkHome.classList.add('active');
      if (navLinkAnalyzer) navLinkAnalyzer.classList.remove('active');
      if (headerCtaBtn) headerCtaBtn.classList.remove('hidden');
      setNavActive(sidebarNavHome);

      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  /**
   * Sidebar Navigation Controls (Within Analyzer View)
   */
  function setupSidebarNav() {
    if (sidebarNavHome) {
      sidebarNavHome.addEventListener('click', () => {
        switchView('home');
      });
    }

    if (navAnalyzer) {
      navAnalyzer.addEventListener('click', () => {
        setNavActive(navAnalyzer);
        const analyzerSec = document.getElementById('analyzerSection');
        if (analyzerSec) {
          analyzerSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        messageInput.focus();
      });
    }

    if (navRecent) {
      navRecent.addEventListener('click', () => {
        setNavActive(navRecent);
        const recentSec = document.getElementById('recentSection');
        if (recentSec) {
          recentSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    }

    if (navHowItWorks) {
      navHowItWorks.addEventListener('click', openModal);
    }
  }

  function setNavActive(activeBtn) {
    [sidebarNavHome, navAnalyzer, navRecent, navHowItWorks].forEach(btn => {
      if (btn) btn.classList.remove('active');
    });
    if (activeBtn) activeBtn.classList.add('active');
  }

  /**
   * Context Category Selector
   */
  function setupTypeSelector() {
    const pills = document.querySelectorAll('.type-pill');
    pills.forEach(pill => {
      pill.addEventListener('click', () => {
        pills.forEach(p => {
          p.classList.remove('active');
          p.setAttribute('aria-checked', 'false');
        });
        pill.classList.add('active');
        pill.setAttribute('aria-checked', 'true');
        currentInputType = pill.dataset.type;
      });
    });
  }

  function setTypeSelector(type) {
    currentInputType = type;
    const pills = document.querySelectorAll('.type-pill');
    pills.forEach(p => {
      const match = p.dataset.type === type;
      p.classList.toggle('active', match);
      p.setAttribute('aria-checked', match ? 'true' : 'false');
    });
  }

  /**
   * Input Metrics and Keyboard Shortcuts
   */
  function setupInputListeners() {
    messageInput.addEventListener('input', () => {
      updateTextMetrics();
      hideInputAlert();
    });

    clearBtn.addEventListener('click', () => {
      messageInput.value = '';
      updateTextMetrics();
      hideInputAlert();
      resultsSection.classList.add('hidden');
      if (resultsEmptyState) resultsEmptyState.classList.remove('hidden');
      lastAnalysisResult = null;
      messageInput.focus();
    });

    analyzeBtn.addEventListener('click', handleAnalyze);

    // Keyboard shortcut: Ctrl + Enter / Cmd + Enter
    messageInput.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        handleAnalyze();
      }
    });

    if (historicalDismissBtn) {
      historicalDismissBtn.addEventListener('click', () => {
        historicalBanner.classList.add('hidden');
      });
    }
  }

  function updateTextMetrics() {
    const text = messageInput.value;
    const len = text.length;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;

    charCount.textContent = len.toLocaleString();
    wordCount.textContent = `${words.toLocaleString()} words`;

    charCount.classList.remove('limit-near', 'limit-exceeded');
    if (len > 9500) {
      charCount.classList.add('limit-exceeded');
    } else if (len > 8000) {
      charCount.classList.add('limit-near');
    }
  }

  /**
   * Sample Loaders
   */
  function setupSampleButtons() {
    sampleLegitBtn.addEventListener('click', () => loadSample('legitimate'));
    sampleFeeBtn.addEventListener('click', () => loadSample('fee_scam'));
    sampleOtpBtn.addEventListener('click', () => loadSample('otp_theft'));
    sampleTelegramBtn.addEventListener('click', () => loadSample('telegram_phish'));
  }

  function loadSample(key) {
    const sample = SAMPLES[key];
    if (!sample) return;
    setTypeSelector(sample.type);
    messageInput.value = sample.text;
    updateTextMetrics();
    hideInputAlert();
    messageInput.focus();
  }

  function showInputAlert(message) {
    inputAlertText.textContent = message;
    inputAlert.classList.remove('hidden');
  }

  function hideInputAlert() {
    inputAlert.classList.add('hidden');
  }

  /**
   * Core Analysis Execution
   */
  async function handleAnalyze() {
    if (isAnalyzing) return;

    const rawText = messageInput.value;
    const trimmed = rawText.trim();

    if (!trimmed) {
      showInputAlert('Please enter or paste a message, offer, or URL to analyze.');
      messageInput.focus();
      return;
    }

    if (trimmed.length < 3) {
      showInputAlert('Please enter at least 3 characters for a meaningful assessment.');
      messageInput.focus();
      return;
    }

    if (rawText.length > 10000) {
      showInputAlert('Input exceeds the maximum allowed length of 10,000 characters.');
      return;
    }

    hideInputAlert();
    setAnalyzingState(true);

    try {
      const response = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          text: rawText,
          input_type: currentInputType,
          language_hint: 'en'
        })
      });

      if (!response.ok) {
        let errMessage = 'Unable to analyze message. Please try again.';
        try {
          const errData = await response.json();
          if (errData.detail) {
            errMessage = Array.isArray(errData.detail) ? errData.detail.join(', ') : errData.detail;
          }
        } catch (_) {}
        throw new Error(errMessage);
      }

      const data = await response.json();
      lastAnalysisResult = data;

      // Add to session history (in-memory only; DO NOT store raw user text!)
      saveToSessionHistory(data);

      // Render fresh assessment
      renderResults(data, false);

      // Smooth scroll to results
      resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (err) {
      console.error('Analysis error:', err);
      showInputAlert(err.message || 'Network error: could not connect to backend analyzer server at http://127.0.0.1:8000.');
    } finally {
      setAnalyzingState(false);
    }
  }

  function setAnalyzingState(loading) {
    isAnalyzing = loading;
    analyzeBtn.disabled = loading;
    if (loading) {
      analyzeSpinner.classList.remove('hidden');
      analyzeIcon.classList.add('hidden');
      analyzeBtnText.textContent = 'Analyzing...';
    } else {
      analyzeSpinner.classList.add('hidden');
      analyzeIcon.classList.remove('hidden');
      analyzeBtnText.textContent = 'Analyze Message';
    }
  }

  /**
   * In-Memory Session History Management
   * STRICT PRIVACY: NEVER stores raw submitted text or matched text snippets in memory!
   */
  function saveToSessionHistory(data) {
    if (!data || !data.analysis_id) return;

    // Remove existing entry if duplicated by ID
    recentAnalyses = recentAnalyses.filter(item => item.analysis_id !== data.analysis_id);

    // Save only minimal required metadata (no raw text)
    const historyEntry = {
      analysis_id: data.analysis_id,
      timestamp: data.timestamp,
      input_type: data.input_type,
      risk_score: data.risk_score,
      risk_level: data.risk_level,
      verdict_summary: data.verdict_summary,
      character_count: data.character_count || 0,
      word_count: data.word_count || 0,
      // Minimal findings copy without retaining raw text
      findings: (data.findings || []).map(f => ({
        rule_id: f.rule_id,
        title: f.title,
        category: f.category,
        severity: f.severity,
        explanation: f.explanation,
        recommended_action: f.recommended_action,
        matched_evidence: [] // Intentionally omit raw user text tokens from history
      })),
      positive_signals: [...(data.positive_signals || [])],
      recommended_actions: [...(data.recommended_actions || [])],
      analyzer_method: data.analyzer_method || 'heuristic_rule_engine',
      disclaimer: data.disclaimer || ''
    };

    recentAnalyses.unshift(historyEntry);

    // Keep bounded to MAX_HISTORY_ITEMS (5)
    if (recentAnalyses.length > MAX_HISTORY_ITEMS) {
      recentAnalyses.length = MAX_HISTORY_ITEMS;
    }

    renderHistory();
  }

  function setupHistoryControls() {
    clearHistoryBtn.addEventListener('click', () => {
      if (recentAnalyses.length === 0) return;
      clearConfirmBox.classList.remove('hidden');
      confirmClearBtn.focus();
    });

    cancelClearBtn.addEventListener('click', () => {
      clearConfirmBox.classList.add('hidden');
      clearHistoryBtn.focus();
    });

    confirmClearBtn.addEventListener('click', () => {
      recentAnalyses = [];
      clearConfirmBox.classList.add('hidden');
      renderHistory();
      showToast('In-memory session history cleared.');
      clearHistoryBtn.focus();
    });
  }

  /**
   * Render Recent Analyses (Safe DOM construction, zero XSS vulnerability)
   */
  function renderHistory() {
    recentAnalysesList.innerHTML = '';
    const count = recentAnalyses.length;
    recentCountBadge.textContent = `${count} / ${MAX_HISTORY_ITEMS}`;
    if (sidebarRecentCount) sidebarRecentCount.textContent = count;
    clearHistoryBtn.disabled = count === 0;

    if (count === 0) {
      const emptyDiv = document.createElement('div');
      emptyDiv.className = 'recent-empty-state';

      const iconDiv = document.createElement('div');
      iconDiv.className = 'recent-empty-icon';
      iconDiv.innerHTML = `
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      `;

      const titleDiv = document.createElement('div');
      titleDiv.className = 'recent-empty-title';
      titleDiv.textContent = 'No recent session analyses';

      const descDiv = document.createElement('div');
      descDiv.className = 'recent-empty-desc';
      descDiv.textContent = 'Analyses performed during this browser session will appear here temporarily. History is stored strictly in memory and clears when the page is closed or refreshed.';

      emptyDiv.appendChild(iconDiv);
      emptyDiv.appendChild(titleDiv);
      emptyDiv.appendChild(descDiv);
      recentAnalysesList.appendChild(emptyDiv);
      return;
    }

    recentAnalyses.forEach(entry => {
      const card = document.createElement('div');
      card.className = `recent-card level-${escapeAttr(entry.risk_level)}`;
      card.tabIndex = 0;
      card.setAttribute('role', 'button');
      card.setAttribute('aria-label', `Revisit ${entry.input_type} analysis with risk score ${entry.risk_score} out of 100`);

      // Left column: Score circle + meta + summary
      const leftCol = document.createElement('div');
      leftCol.className = 'recent-card-left';

      // Score badge
      const scoreBadge = document.createElement('div');
      scoreBadge.className = 'recent-score-badge';
      const levelColors = getLevelColorStyles(entry.risk_level);
      scoreBadge.style.backgroundColor = levelColors.bg;
      scoreBadge.style.borderColor = levelColors.border;
      scoreBadge.style.color = levelColors.text;

      const scoreVal = document.createElement('span');
      scoreVal.className = 'score-val';
      scoreVal.textContent = entry.risk_score;

      const scoreDenom = document.createElement('span');
      scoreDenom.className = 'score-denom';
      scoreDenom.textContent = '/100';

      scoreBadge.appendChild(scoreVal);
      scoreBadge.appendChild(scoreDenom);

      // Content Column
      const contentCol = document.createElement('div');
      contentCol.className = 'recent-card-content';

      const metaRow = document.createElement('div');
      metaRow.className = 'recent-meta-row';

      const typeChip = document.createElement('span');
      typeChip.className = 'recent-type-chip';
      typeChip.textContent = entry.input_type.replace('_', ' ');

      const levelChip = document.createElement('span');
      levelChip.className = 'recent-level-chip';
      levelChip.textContent = entry.risk_level;
      levelChip.style.backgroundColor = levelColors.bg;
      levelChip.style.color = levelColors.text;

      const timeSpan = document.createElement('span');
      timeSpan.className = 'recent-time';
      const timeDate = new Date(entry.timestamp);
      timeSpan.textContent = isNaN(timeDate.getTime()) ? entry.timestamp : timeDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

      metaRow.appendChild(typeChip);
      metaRow.appendChild(levelChip);
      metaRow.appendChild(timeSpan);

      const summarySnippet = document.createElement('p');
      summarySnippet.className = 'recent-summary-snippet';
      summarySnippet.textContent = entry.verdict_summary || 'Evaluation report available.';

      contentCol.appendChild(metaRow);
      contentCol.appendChild(summarySnippet);

      leftCol.appendChild(scoreBadge);
      leftCol.appendChild(contentCol);

      // Right column: View arrow
      const rightCol = document.createElement('div');
      rightCol.className = 'recent-card-right';
      rightCol.innerHTML = `
        <span>Revisit</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6" />
        </svg>
      `;

      card.appendChild(leftCol);
      card.appendChild(rightCol);

      // Event handlers to restore assessment
      const triggerRestore = () => {
        restoreHistoryAssessment(entry);
      };

      card.addEventListener('click', triggerRestore);
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          triggerRestore();
        }
      });

      recentAnalysesList.appendChild(card);
    });
  }

  function getLevelColorStyles(level) {
    switch (level) {
      case 'Critical':
        return { bg: 'var(--risk-critical-bg)', border: 'var(--risk-critical-border)', text: '#fca5a5', stroke: 'var(--risk-critical)' };
      case 'High':
        return { bg: 'var(--risk-high-bg)', border: 'var(--risk-high-border)', text: '#fed7aa', stroke: 'var(--risk-high)' };
      case 'Moderate':
        return { bg: 'var(--risk-moderate-bg)', border: 'var(--risk-moderate-border)', text: '#fde68a', stroke: 'var(--risk-moderate)' };
      case 'Low':
      default:
        return { bg: 'var(--risk-low-bg)', border: 'var(--risk-low-border)', text: '#a7f3d0', stroke: 'var(--risk-low)' };
    }
  }

  /**
   * Reopen a historical session record into the results area
   */
  function restoreHistoryAssessment(entry) {
    lastAnalysisResult = entry;
    renderResults(entry, true);
    setNavActive(navAnalyzer);
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    showToast('Loaded historical assessment from session memory.');
  }

  /**
   * Render Analysis Report
   * @param {Object} data - Structured assessment report
   * @param {boolean} isHistorical - True if restoring a historical session entry
   */
  function renderResults(data, isHistorical = false) {
    if (resultsEmptyState) resultsEmptyState.classList.add('hidden');
    resultsSection.classList.remove('hidden');

    // Historical banner state
    if (isHistorical) {
      const d = new Date(data.timestamp);
      const timeStr = isNaN(d.getTime()) ? data.timestamp : d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      historicalTimestamp.textContent = timeStr;
      historicalBanner.classList.remove('hidden');
    } else {
      historicalBanner.classList.add('hidden');
    }

    // Metadata
    metaId.querySelector('span').textContent = (data.analysis_id || '').slice(0, 13) + '...';
    metaTypeBadge.textContent = (data.input_type || 'MESSAGE').replace('_', ' ').toUpperCase();
    const date = new Date(data.timestamp);
    metaTimestamp.textContent = isNaN(date.getTime()) ? data.timestamp : date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    // Animated Risk Score & Gauge
    animateScore(data.risk_score, data.risk_level);

    // Verdict Summary Card
    verdictHeadline.textContent = getVerdictHeadline(data.risk_level);
    verdictSummary.textContent = data.verdict_summary;
    findingsCount.textContent = (data.findings || []).length;
    positiveCount.textContent = (data.positive_signals || []).length;

    // Evidence-based findings list (safe DOM construction)
    renderFindings(data.findings || [], isHistorical);

    // Positive signals list
    renderPositiveSignals(data.positive_signals || []);

    // Recommendations checklist
    renderRecommendations(data.recommended_actions || []);

    // Disclaimer
    disclaimerText.textContent = data.disclaimer || 'Heuristic assessment based on pattern detection — not a definitive determination of fraud or authenticity.';
  }

  function getVerdictHeadline(level) {
    switch (level) {
      case 'Critical': return 'Critical Scam Alert — High Probability of Fraud';
      case 'High': return 'Significant Red Flags Detected';
      case 'Moderate': return 'Elevated Risk — Caution Advised';
      case 'Low':
      default:
        return 'Low Heuristic Risk Detected';
    }
  }

  /**
   * Animate Circular Gauge and Numerical Counter
   */
  function animateScore(targetScore, level) {
    let current = 0;
    const duration = 750; // ms
    const stepTime = 16;
    const steps = duration / stepTime;
    const increment = targetScore / steps;

    gaugeFill.style.strokeDasharray = GAUGE_CIRCUMFERENCE;
    const targetOffset = GAUGE_CIRCUMFERENCE - (targetScore / 100) * GAUGE_CIRCUMFERENCE;

    const colors = getLevelColorStyles(level);
    gaugeFill.style.stroke = colors.stroke;
    gaugeFill.style.strokeDashoffset = targetOffset;

    riskLevelText.textContent = level;
    riskLevelBadge.style.backgroundColor = colors.bg;
    riskLevelBadge.style.borderColor = colors.border;
    riskLevelBadge.style.color = colors.text;
    riskLevelBadge.querySelector('.level-indicator').style.backgroundColor = colors.stroke;

    scoreSubtext.textContent = `${level} heuristic risk band (${getScoreBandLabel(level)})`;

    const timer = setInterval(() => {
      current += increment;
      if (current >= targetScore) {
        current = targetScore;
        clearInterval(timer);
      }
      scoreNumber.textContent = Math.round(current);
    }, stepTime);
  }

  function getScoreBandLabel(level) {
    switch (level) {
      case 'Critical': return 'Score 70–100';
      case 'High': return 'Score 45–69';
      case 'Moderate': return 'Score 20–44';
      default: return 'Score 0–19';
    }
  }

  /**
   * Render Findings (Safe DOM Construction — XSS Prevention)
   */
  function renderFindings(findings, isHistorical = false) {
    findingsList.innerHTML = '';
    findingsBadge.textContent = `${findings.length} Detected`;

    if (!findings || findings.length === 0) {
      const emptyBox = document.createElement('div');
      emptyBox.className = 'no-findings-box';
      emptyBox.innerHTML = `
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          <path d="m9 12 2 2 4-4" />
        </svg>
      `;
      const textWrap = document.createElement('div');
      const title = document.createElement('div');
      title.className = 'no-findings-title';
      title.textContent = 'No direct scam indicators detected';
      const desc = document.createElement('div');
      desc.className = 'no-findings-desc';
      desc.textContent = 'The deterministic rule engine found no upfront payment demands, OTP harvesting, artificial urgency, or suspicious link structures.';
      textWrap.appendChild(title);
      textWrap.appendChild(desc);
      emptyBox.appendChild(textWrap);
      findingsList.appendChild(emptyBox);
      return;
    }

    findings.forEach(f => {
      const card = document.createElement('div');
      card.className = `finding-card severity-${escapeAttr(f.severity)}`;

      // Card Header
      const header = document.createElement('div');
      header.className = 'finding-card-header';

      const meta = document.createElement('div');
      meta.className = 'finding-meta';

      const ruleBadge = document.createElement('span');
      ruleBadge.className = 'rule-id-badge';
      ruleBadge.textContent = f.rule_id;

      const catName = document.createElement('span');
      catName.className = 'category-name';
      catName.textContent = f.category;

      meta.appendChild(ruleBadge);
      meta.appendChild(catName);

      const sevPill = document.createElement('span');
      sevPill.className = `severity-pill ${escapeAttr(f.severity)}`;
      sevPill.textContent = (f.severity || '').toUpperCase();

      header.appendChild(meta);
      header.appendChild(sevPill);
      card.appendChild(header);

      // Title
      const title = document.createElement('h4');
      title.className = 'finding-title';
      title.textContent = f.title;
      card.appendChild(title);

      // Matched Evidence (chips)
      if (f.matched_evidence && f.matched_evidence.length > 0) {
        const evBox = document.createElement('div');
        evBox.className = 'finding-evidence-box';

        const evLabel = document.createElement('span');
        evLabel.className = 'evidence-label';
        evLabel.textContent = 'Matched Evidence:';
        evBox.appendChild(evLabel);

        const evChips = document.createElement('div');
        evChips.className = 'evidence-chips';

        f.matched_evidence.forEach(ev => {
          const chip = document.createElement('span');
          chip.className = 'evidence-chip';
          chip.textContent = `"${ev}"`;
          evChips.appendChild(chip);
        });

        evBox.appendChild(evChips);
        card.appendChild(evBox);
      } else if (isHistorical) {
        // In historical view, evidence chips are omitted for privacy preservation
        const notice = document.createElement('div');
        notice.className = 'finding-evidence-box';
        const evLabel = document.createElement('span');
        evLabel.className = 'evidence-label';
        evLabel.textContent = 'Matched Rule Reference: Verified Heuristic Flag';
        notice.appendChild(evLabel);
        card.appendChild(notice);
      }

      // Explanation
      const explanation = document.createElement('p');
      explanation.className = 'finding-explanation';
      explanation.textContent = f.explanation;
      card.appendChild(explanation);

      // Action Row
      const actionRow = document.createElement('div');
      actionRow.className = 'finding-action-row';
      actionRow.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6" />
        </svg>
      `;
      const actionText = document.createElement('span');
      const actionBold = document.createElement('strong');
      actionBold.textContent = 'Action: ';
      actionText.appendChild(actionBold);
      actionText.appendChild(document.createTextNode(f.recommended_action));
      actionRow.appendChild(actionText);

      card.appendChild(actionRow);
      findingsList.appendChild(card);
    });
  }

  /**
   * Render Positive Signals
   */
  function renderPositiveSignals(signals) {
    positiveSignalsList.innerHTML = '';
    if (!signals || signals.length === 0) {
      positiveSignalsContainer.classList.add('hidden');
      return;
    }

    positiveSignalsContainer.classList.remove('hidden');
    signals.forEach(sig => {
      const li = document.createElement('li');
      li.textContent = sig;
      positiveSignalsList.appendChild(li);
    });
  }

  /**
   * Render Recommendations Checklist
   */
  function renderRecommendations(actions) {
    recommendationsList.innerHTML = '';
    const items = (actions && actions.length > 0)
      ? actions
      : [
        'Verify the sender through your university career center or official company website.',
        'Never transfer funds or provide personal authentication codes.'
      ];

    items.forEach(act => {
      const li = document.createElement('li');
      li.textContent = act;
      recommendationsList.appendChild(li);
    });
  }

  /**
   * Copy Report & Analyze Another
   */
  function setupActions() {
    copyReportBtn.addEventListener('click', handleCopyReport);
    analyzeAnotherBtn.addEventListener('click', () => {
      messageInput.value = '';
      updateTextMetrics();
      resultsSection.classList.add('hidden');
      if (resultsEmptyState) resultsEmptyState.classList.remove('hidden');
      messageInput.focus();
      window.scrollTo({ top: messageInput.offsetTop - 100, behavior: 'smooth' });
    });
  }

  async function handleCopyReport() {
    if (!lastAnalysisResult) return;

    const r = lastAnalysisResult;
    const reportText = [
      `========================================`,
      ` TRUSTLENS AI — SCAM RISK ASSESSMENT REPORT`,
      `========================================`,
      `Analysis ID: ${r.analysis_id}`,
      `Date/Time:   ${r.timestamp}`,
      `Input Type:  ${(r.input_type || 'message').toUpperCase()}`,
      `Risk Score:  ${r.risk_score} / 100 (${(r.risk_level || 'LOW').toUpperCase()})`,
      `Engine:      ${r.analyzer_method || 'heuristic_rule_engine'}`,
      ``,
      `--- VERDICT SUMMARY ---`,
      r.verdict_summary || 'N/A',
      ``,
      `--- EVIDENCE-BASED WARNING SIGNS (${(r.findings || []).length}) ---`,
      ...(r.findings || []).map((f, i) =>
        `[${i + 1}] [${f.rule_id}] ${f.title} (${(f.severity || '').toUpperCase()})\n` +
        `    Explanation: ${f.explanation}\n` +
        `    Action:      ${f.recommended_action}`
      ),
      ``,
      `--- POSITIVE SIGNALS (${(r.positive_signals || []).length}) ---`,
      ...((r.positive_signals && r.positive_signals.length > 0) ? r.positive_signals.map(s => `* ${s}`) : ['* None detected']),
      ``,
      `--- RECOMMENDED NEXT STEPS ---`,
      ...((r.recommended_actions || []).map((a, i) => `${i + 1}. ${a}`)),
      ``,
      `--- LEGAL / HEURISTIC DISCLAIMER ---`,
      r.disclaimer || 'Heuristic assessment based on pattern detection — not a definitive determination of fraud or authenticity.',
      `========================================`
    ].join('\n');

    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(reportText);
      } else {
        const textarea = document.createElement('textarea');
        textarea.value = reportText;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
      }
      showToast('Assessment report copied to clipboard!');
    } catch (err) {
      console.error('Copy failure:', err);
      showToast('Failed to copy report to clipboard.');
    }
  }

  function showToast(msg) {
    toastMessage.textContent = msg;
    toastNotification.classList.remove('hidden');
    setTimeout(() => {
      toastNotification.classList.add('hidden');
    }, 3200);
  }

  /**
   * Modal Management (Keyboard Escape + Accessible Focus Trap)
   */
  function setupModal() {
    if (howItWorksBtn) howItWorksBtn.addEventListener('click', openModal);
    if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
    if (closeModalFooterBtn) closeModalFooterBtn.addEventListener('click', closeModal);

    if (howItWorksModal) {
      howItWorksModal.addEventListener('click', (e) => {
        if (e.target === howItWorksModal) {
          closeModal();
        }
      });
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && howItWorksModal && !howItWorksModal.classList.contains('hidden')) {
        closeModal();
      }
    });
  }

  function openModal() {
    if (howItWorksModal) {
      howItWorksModal.classList.remove('hidden');
      if (closeModalBtn) closeModalBtn.focus();
    }
  }

  function closeModal() {
    if (howItWorksModal) {
      howItWorksModal.classList.add('hidden');
      if (navLinkHowItWorks) {
        navLinkHowItWorks.focus();
      } else if (howItWorksBtn) {
        howItWorksBtn.focus();
      }
    }
  }

  function escapeAttr(str) {
    if (!str) return '';
    return String(str).replace(/[^a-zA-Z0-9_-]/g, '');
  }

  // Initialize on DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
