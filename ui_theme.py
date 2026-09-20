"""
Grand Royale Hotel - Modern Luxury UI Theme & Styling
Provides bespoke CSS, custom color tokens, and responsive layout styling for Gradio.
"""

CUSTOM_CSS = """
/* ==========================================================================
   Grand Royale Luxury Hotel Design System
   ========================================================================== */

@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --primary-gold: #c5a059;
    --primary-gold-bright: #dfb76c;
    --primary-gold-glow: rgba(197, 160, 89, 0.25);
    --bg-dark-obsidian: #080c14;
    --bg-surface-card: #0f172a;
    --bg-surface-card-subtle: rgba(19, 27, 46, 0.85);
    --border-gold-subtle: rgba(197, 160, 89, 0.25);
    --border-card: rgba(255, 255, 255, 0.08);
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --urgent-red: #ef4444;
    --high-orange: #f97316;
    --medium-yellow: #eab308;
    --low-green: #10b981;
}

/* Global Container Polish */
.gradio-container {
    background: radial-gradient(circle at 50% 0%, #17223b 0%, #080c14 70%) !important;
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text-main) !important;
    max-width: 1500px !important;
    margin: 0 auto !important;
    padding: 16px 24px !important;
}

/* Header Banner */
.hotel-header {
    background: linear-gradient(135deg, rgba(23, 34, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
    border: 1px solid var(--border-gold-subtle);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45), 0 0 20px var(--primary-gold-glow);
    display: flex;
    justify-content: space-between;
    align-items: center;
    backdrop-filter: blur(12px);
}

.hotel-title {
    font-family: 'Cinzel', serif !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px;
    background: linear-gradient(90deg, #dfb76c 0%, #fef3c7 50%, #c5a059 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 !important;
    padding: 0 !important;
}

.hotel-subtitle {
    font-size: 14px;
    color: var(--text-muted);
    letter-spacing: 0.5px;
    margin-top: 4px;
}

.hotel-badge {
    background: rgba(197, 160, 89, 0.15);
    border: 1px solid var(--primary-gold);
    color: var(--primary-gold-bright);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

/* Tabs Styling */
.tabs {
    border-bottom: 1px solid var(--border-gold-subtle) !important;
    margin-bottom: 20px !important;
    gap: 8px !important;
}

.tab-nav button {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    color: var(--text-muted) !important;
    padding: 12px 20px !important;
    border-radius: 10px 10px 0 0 !important;
    transition: all 0.25s ease !important;
    border: none !important;
    background: transparent !important;
}

.tab-nav button:hover {
    color: var(--primary-gold-bright) !important;
    background: rgba(197, 160, 89, 0.08) !important;
}

.tab-nav button.selected {
    color: var(--primary-gold-bright) !important;
    border-bottom: 3px solid var(--primary-gold) !important;
    background: rgba(197, 160, 89, 0.12) !important;
}

/* KPI Stat Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.kpi-card {
    background: linear-gradient(145deg, #131d31 0%, #0c1220 100%);
    border: 1px solid var(--border-gold-subtle);
    border-radius: 14px;
    padding: 18px 20px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4), 0 0 15px var(--primary-gold-glow);
}

.kpi-label {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-muted);
    font-weight: 600;
}

.kpi-value {
    font-size: 28px;
    font-weight: 700;
    font-family: 'Cinzel', serif;
    color: var(--primary-gold-bright);
    margin-top: 6px;
}

.kpi-sub {
    font-size: 11px;
    color: #64748b;
    margin-top: 2px;
}

/* Luxury Form Inputs & Buttons */
input, textarea, select {
    background: rgba(15, 23, 42, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    color: #f8fafc !important;
    border-radius: 10px !important;
}

input:focus, textarea:focus, select:focus {
    border-color: var(--primary-gold) !important;
    box-shadow: 0 0 0 2px var(--primary-gold-glow) !important;
}

button.primary {
    background: linear-gradient(135deg, #c5a059 0%, #a27e38 100%) !important;
    color: #080c14 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 14px rgba(197, 160, 89, 0.35) !important;
    transition: all 0.2s ease !important;
}

button.primary:hover {
    background: linear-gradient(135deg, #dfb76c 0%, #c5a059 100%) !important;
    transform: scale(1.02) !important;
    box-shadow: 0 6px 20px rgba(197, 160, 89, 0.5) !important;
}

/* Chatbot Customization */
.chatbot {
    border: 1px solid var(--border-gold-subtle) !important;
    border-radius: 16px !important;
    background: rgba(15, 23, 42, 0.75) !important;
    backdrop-filter: blur(8px) !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.35) !important;
}

/* Code / Ticket Blocks */
pre, code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
}

/* Status Badges */
.badge-urgent {
    background: rgba(239, 68, 68, 0.2);
    color: #fca5a5;
    border: 1px solid #ef4444;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
}

.badge-high {
    background: rgba(249, 115, 22, 0.2);
    color: #fdba74;
    border: 1px solid #f97316;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
}

.badge-medium {
    background: rgba(234, 179, 8, 0.2);
    color: #fde047;
    border: 1px solid #eab308;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
}

.badge-low {
    background: rgba(16, 185, 129, 0.2);
    color: #86efac;
    border: 1px solid #10b981;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
}

/* Smooth Tables */
.table-wrap {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border-gold-subtle);
}

/* Quick prompt pills */
.quick-pill {
    background: rgba(30, 41, 59, 0.8) !important;
    border: 1px solid rgba(197, 160, 89, 0.3) !important;
    color: #e2e8f0 !important;
    font-size: 12px !important;
    border-radius: 20px !important;
    padding: 6px 14px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

.quick-pill:hover {
    background: rgba(197, 160, 89, 0.2) !important;
    border-color: var(--primary-gold-bright) !important;
    color: var(--primary-gold-bright) !important;
    transform: translateY(-1px) !important;
}
"""
