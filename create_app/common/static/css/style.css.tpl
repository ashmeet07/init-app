:root {
    color-scheme: light;
    --bg: #f7f8fb;
    --surface: #ffffff;
    --surface-strong: #f0f3f8;
    --text: #162033;
    --muted: #667085;
    --border: #d7deea;
    --brand: #f97316;
    --brand-strong: #c2410c;
    --ok: #0f9f6e;
    --shadow: 0 24px 70px rgba(21, 32, 51, 0.12);
}

[data-theme="dark"] {
    color-scheme: dark;
    --bg: #10131a;
    --surface: #171b24;
    --surface-strong: #202635;
    --text: #edf2f7;
    --muted: #9aa4b2;
    --border: #30384a;
    --brand: #fb923c;
    --brand-strong: #fdba74;
    --ok: #34d399;
    --shadow: 0 24px 70px rgba(0, 0, 0, 0.35);
}

body.fastapi { --accent: #05998b; }
body.flask { --accent: #111827; }
body.django { --accent: #0c4b33; }
body.bottle { --accent: #2563eb; }
body.sanic { --accent: #7c3aed; }
body.falcon { --accent: #334155; }
body.tornado { --accent: #0284c7; }
body.pyramid { --accent: #dc2626; }
body { --accent: var(--brand); }

* {
    box-sizing: border-box;
}

html {
    min-height: 100%;
}

body {
    min-height: 100vh;
    margin: 0;
    background:
        radial-gradient(circle at top left, color-mix(in srgb, var(--accent) 18%, transparent), transparent 34rem),
        linear-gradient(180deg, var(--bg), var(--surface-strong));
    color: var(--text);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    letter-spacing: 0;
}

a {
    color: inherit;
}

.topbar {
    min-height: 72px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    padding: 18px clamp(18px, 4vw, 56px);
    border-bottom: 1px solid var(--border);
    background: color-mix(in srgb, var(--surface) 84%, transparent);
    backdrop-filter: blur(16px);
}

.brand {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    text-decoration: none;
}

.brand-mark {
    width: 40px;
    height: 40px;
    display: inline-grid;
    place-items: center;
    border-radius: 8px;
    background: var(--brand);
    color: #111827;
    font-weight: 800;
}

.brand strong,
.brand small {
    display: block;
}

.brand strong {
    font-size: 16px;
}

.brand small {
    margin-top: 2px;
    color: var(--muted);
    font-size: 12px;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 14px;
}

.nav-links a {
    color: var(--muted);
    font-size: 14px;
    font-weight: 650;
    text-decoration: none;
}

.nav-links a:hover {
    color: var(--text);
}

.icon-button {
    width: 44px;
    height: 28px;
    padding: 3px;
    border: 1px solid var(--border);
    border-radius: 999px;
    background: var(--surface-strong);
    cursor: pointer;
}

.icon-button span {
    width: 20px;
    height: 20px;
    display: block;
    border-radius: 999px;
    background: var(--brand);
    transition: transform 160ms ease;
}

[data-theme="dark"] .icon-button span {
    transform: translateX(14px);
}

.hero {
    width: min(1160px, calc(100% - 36px));
    min-height: calc(100vh - 160px);
    margin: 0 auto;
    display: grid;
    grid-template-columns: minmax(0, 1.05fr) minmax(320px, 0.8fr);
    align-items: center;
    gap: clamp(28px, 5vw, 72px);
    padding: clamp(48px, 7vw, 86px) 0;
}

.eyebrow {
    margin: 0 0 14px;
    color: var(--brand-strong);
    font-size: 13px;
    font-weight: 800;
    text-transform: uppercase;
}

h1 {
    max-width: 760px;
    margin: 0;
    font-size: clamp(44px, 8vw, 82px);
    line-height: 0.96;
    letter-spacing: 0;
}

.lead {
    max-width: 660px;
    margin: 24px 0 0;
    color: var(--muted);
    font-size: clamp(17px, 2vw, 21px);
    line-height: 1.65;
}

.actions {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 32px;
}

.button {
    min-height: 44px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0 18px;
    border-radius: 8px;
    font-weight: 750;
    text-decoration: none;
}

.button.primary {
    background: var(--brand);
    color: #111827;
}

.button.secondary {
    border: 1px solid var(--border);
    background: var(--surface);
}

.status-panel {
    border: 1px solid var(--border);
    border-radius: 8px;
    background: color-mix(in srgb, var(--surface) 92%, transparent);
    box-shadow: var(--shadow);
    overflow: hidden;
}

.status-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 18px 20px;
    border-bottom: 1px solid var(--border);
    font-weight: 800;
}

.pulse {
    width: 10px;
    height: 10px;
    border-radius: 999px;
    background: var(--ok);
    box-shadow: 0 0 0 6px color-mix(in srgb, var(--ok) 18%, transparent);
}

.metrics {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    margin: 0;
    border-bottom: 1px solid var(--border);
}

.metrics div {
    padding: 18px 20px;
    border-right: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
}

.metrics div:nth-child(2n) {
    border-right: 0;
}

.metrics div:nth-last-child(-n + 2) {
    border-bottom: 0;
}

dt {
    color: var(--muted);
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
}

dd {
    margin: 6px 0 0;
    font-size: 16px;
    font-weight: 800;
}

.terminal {
    margin: 0;
    padding: 22px;
    overflow-x: auto;
    background: #0b1020;
    color: #d1e7ff;
    font: 14px/1.55 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}

.feature-band {
    width: min(1160px, calc(100% - 36px));
    margin: 0 auto 56px;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
}

.feature-band article {
    min-height: 150px;
    padding: 24px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--surface);
}

.feature-band h2 {
    margin: 0 0 10px;
    font-size: 18px;
}

.feature-band p {
    margin: 0;
    color: var(--muted);
    line-height: 1.6;
}

.footer {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    padding: 28px clamp(18px, 4vw, 56px);
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: 14px;
}

@media (max-width: 820px) {
    .topbar,
    .footer {
        align-items: flex-start;
        flex-direction: column;
    }

    .hero {
        grid-template-columns: 1fr;
        min-height: auto;
    }

    .feature-band {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 520px) {
    .nav-links {
        width: 100%;
        justify-content: space-between;
        gap: 10px;
    }

    .metrics {
        grid-template-columns: 1fr;
    }

    .metrics div,
    .metrics div:nth-child(2n),
    .metrics div:nth-last-child(-n + 2) {
        border-right: 0;
        border-bottom: 1px solid var(--border);
    }

    .metrics div:last-child {
        border-bottom: 0;
    }
}
