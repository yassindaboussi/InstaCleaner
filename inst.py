import json
import html
from datetime import datetime
from collections import Counter

# ── Load data ────────────────────────────────────────────────────────────────
with open('InstaNoBack_NonFollowers.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

users = data['non_followers']

# Fonction pour parser différents formats de date
def parse_date(date_str):
    formats = [
        '%d/%m/%Y',
        '%d %b %Y',
        '%d %B %Y',
        '%Y-%m-%d',
        '%d-%m-%Y',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Impossible de parser la date: {date_str}")

# Parse & enrich
for u in users:
    u['date_obj']      = parse_date(u['followed_date'])
    u['iso_date']      = u['date_obj'].strftime('%Y-%m-%d')
    u['display_date']  = u['date_obj'].strftime('%d %b %Y')
    u['year']          = u['date_obj'].year
    delta              = datetime.now() - u['date_obj']
    years_f            = delta.days / 365.25
    if years_f >= 1:
        u['since'] = f"{years_f:.1f}y ago"
    else:
        months = int(delta.days / 30.44)
        u['since'] = f"{months}mo ago" if months > 0 else "recently"
    u['safe_username'] = html.escape(u['username'])
    u['safe_url']      = f"https://www.instagram.com/{html.escape(u['username'])}/"
    
    import hashlib
    hash_val = int(hashlib.md5(u['username'].encode()).hexdigest()[:8], 16)
    u['avatar_hue'] = hash_val % 360

users.sort(key=lambda x: x['date_obj'])

total_users = len(users)

# ── Build card HTML ──────────────────────────────────────────────────────────
cards_html = ""
for u in users:
    cards_html += f"""
        <div class="card"
             data-username="{u['safe_username']}"
             data-url="{u['safe_url']}"
             data-date="{u['iso_date']}"
             data-year="{u['year']}">
          <button class="remove-btn" title="Dismiss" onclick="removeCard(this)">✕</button>
          <div class="card-avatar" style="background: hsl({u['avatar_hue']}, 70%, 55%);">{u['safe_username'][0].upper()}</div>
          <div class="card-username">@{u['safe_username']}</div>
          <div class="card-meta">
            <span class="badge-date">{u['display_date']}</span>
            <span class="badge-since">{u['since']}</span>
          </div>
          <div class="card-actions">
            <button class="btn-profile" onclick="openProfile('{u['safe_url']}')">View Profile</button>
            <button class="btn-copy" onclick="copyUsername('{u['safe_username']}', this)" title="Copy username">
              Copy
            </button>
          </div>
        </div>"""

# ── Full HTML ────────────────────────────────────────────────────────────────
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InstaNoBack — Non Followers Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #0a0a0c;
            color: #e4e4e7;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        /* Controls */
        .controls {{
            display: flex;
            gap: 12px;
            margin: 20px 0;
            flex-wrap: wrap;
            align-items: center;
        }}

        .search-box {{
            flex: 1;
            min-width: 200px;
        }}

        .search-box input {{
            width: 100%;
            padding: 10px 15px;
            background: #1a1a1e;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            color: #fff;
            font-size: 14px;
        }}

        .search-box input:focus {{
            outline: none;
            border-color: #e1306c;
        }}

        select, button {{
            padding: 10px 20px;
            background: #1a1a1e;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            color: #fff;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }}

        button:hover, select:hover {{
            background: #2a2a2e;
            border-color: #e1306c;
        }}

        .btn-primary {{
            background: linear-gradient(135deg, #405de6, #833ab4, #e1306c);
            border: none;
        }}

        .btn-primary:hover {{
            opacity: 0.9;
            transform: translateY(-1px);
        }}

        .btn-danger {{
            background: #1a1a1e;
            border-color: #e1306c;
        }}

        .btn-danger:hover {{
            background: #e1306c;
        }}

        .input-group {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: #1a1a1e;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 2px 8px;
        }}

        .input-group label {{
            font-size: 12px;
            color: #888;
        }}

        .input-group input {{
            width: 70px;
            background: transparent;
            border: none;
            color: #fff;
            font-size: 14px;
            padding: 8px 4px;
            text-align: center;
        }}

        .input-group input:focus {{
            outline: none;
        }}

        /* Progress bar with text on same line */
        .progress-container {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin: 20px 0;
        }}
        
        .progress-bar {{
            flex: 1;
            background: #1a1a1e;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
        }}

        .progress-fill {{
            background: linear-gradient(135deg, #405de6, #833ab4, #e1306c);
            height: 100%;
            transition: width 0.3s ease;
        }}
        
        .progress-text {{
            font-size: 12px;
            color: #888;
            white-space: nowrap;
            min-width: 180px;
            text-align: right;
        }}

        /* Grid */
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        /* Card */
        .card {{
            background: #1a1a1e;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.2s;
            position: relative;
        }}

        .card:hover {{
            transform: translateY(-2px);
            border-color: #e1306c;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}

        .card.hidden {{
            display: none;
        }}

        .card.removing {{
            opacity: 0;
            transform: scale(0.9);
            transition: all 0.3s;
        }}

        .remove-btn {{
            position: absolute;
            top: 10px;
            right: 10px;
            width: 28px;
            height: 28px;
            padding: 0;
            border-radius: 50%;
            background: rgba(255,255,255,0.1);
            font-size: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .remove-btn:hover {{
            background: #e1306c;
            transform: rotate(90deg);
        }}

        .card-avatar {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            margin: 0 auto 15px;
            color: white;
        }}

        .card-username {{
            text-align: center;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 10px;
            word-break: break-all;
        }}

        .card-meta {{
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-bottom: 15px;
            font-size: 11px;
            color: #888;
        }}

        .badge-date, .badge-since {{
            background: rgba(255,255,255,0.05);
            padding: 4px 8px;
            border-radius: 6px;
        }}

        .card-actions {{
            display: flex;
            gap: 8px;
        }}

        .card-actions button {{
            flex: 1;
            text-align: center;
            padding: 8px;
            font-size: 12px;
            text-decoration: none;
        }}

        .btn-profile, .btn-copy {{
            background: #1a1a1e;
            border: 1px solid rgba(255,255,255,0.1);
        }}

        .btn-profile:hover, .btn-copy:hover {{
            background: #2a2a2e;
            border-color: #e1306c;
        }}

        .btn-copy.copied {{
            background: #2ecc71;
            border-color: #2ecc71;
        }}

        /* Toast */
        #toast {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #2a2a2e;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 12px 20px;
            display: none;
            align-items: center;
            gap: 10px;
            z-index: 1001;
        }}

        #toast.show {{
            display: flex;
        }}

        .toast-undo {{
            background: #e1306c;
            border: none;
            padding: 4px 12px;
        }}

        /* Empty state */
        #empty-state {{
            text-align: center;
            padding: 60px;
            color: #888;
        }}

        /* Popup notice */
        #popup-notice {{
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #1a1a1e;
            border: 1px solid #e1306c;
            border-radius: 12px;
            padding: 30px;
            max-width: 400px;
            z-index: 1002;
        }}

        #popup-notice.show {{
            display: block;
        }}

        @media (max-width: 600px) {{
            body {{ padding: 10px; }}
            .grid {{ grid-template-columns: 1fr; }}
            .progress-text {{ font-size: 10px; min-width: 150px; }}
        }}
    </style>
</head>
<body>
<div class="container">
    <div class="controls">
        <div class="search-box">
            <input type="text" id="search" placeholder="Search username..." oninput="debouncedFilter()">
        </div>
        <select id="sort-select" onchange="applySort()">
            <option value="desc" selected>📅 Newest first</option>
            <option value="asc">📅 Oldest first</option>
            <option value="alpha">🔤 A → Z</option>
            <option value="alpha-rev">🔤 Z → A</option>
        </select>
        
        <div class="input-group">
            <label>🔗 Open:</label>
            <input type="number" id="action-count" min="1" max="100" value="5" oninput="syncInputs(this.value)">
            <button onclick="openLinks()" class="btn-primary">Open</button>
        </div>
        
        <div class="input-group">
            <label>❌ Dismiss:</label>
            <input type="number" id="dismiss-count" min="1" max="100" value="5" oninput="syncInputsReverse(this.value)">
            <button onclick="dismissTop()" class="btn-danger">Dismiss</button>
        </div>
        
        <button onclick="exportRemaining()" class="btn-primary">📥 Export JSON</button>
    </div>

    <div class="progress-container">
        <div class="progress-bar">
            <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
        </div>
        <div class="progress-text" id="progress-text">0 of {total_users} dismissed (0%)</div>
    </div>

    <div class="grid" id="grid">
        {cards_html}
        <div id="empty-state" style="display: none;">
            <p>✨ No accounts match your filters.<br>Great job cleaning up!</p>
        </div>
    </div>
</div>

<div id="toast"></div>
<div id="popup-notice">
    <h3>⚠️ Popups Blocked</h3>
    <p>Please allow popups for this site to open multiple tabs.</p>
    <button onclick="closePopup()" class="btn-primary">Got it</button>
</div>

<script>
    const TOTAL = {total_users};
    let removed = 0;
    let currentSort = 'desc';
    let filterTimeout;

    // Sync both input fields
    function syncInputs(value) {{
        const dismissInput = document.getElementById('dismiss-count');
        if (dismissInput) {{
            dismissInput.value = value;
        }}
    }}

    function syncInputsReverse(value) {{
        const openInput = document.getElementById('action-count');
        if (openInput) {{
            openInput.value = value;
        }}
    }}

    function toast(msg, duration = 2800, undoFn = null) {{
        const el = document.getElementById('toast');
        el.innerHTML = '';
        const text = document.createElement('span');
        text.textContent = msg;
        el.appendChild(text);
        if (undoFn) {{
            const btn = document.createElement('button');
            btn.textContent = '↩ Undo';
            btn.className = 'toast-undo';
            btn.onclick = () => {{ undoFn(); el.classList.remove('show'); }};
            el.appendChild(btn);
        }}
        el.classList.add('show');
        clearTimeout(toast._t);
        toast._t = setTimeout(() => el.classList.remove('show'), duration);
    }}

    function updateStats() {{
        const pct = TOTAL > 0 ? (removed / TOTAL * 100).toFixed(1) : 0;
        document.getElementById('progress-fill').style.width = pct + '%';
        document.getElementById('progress-text').textContent = removed + ' of ' + TOTAL + ' dismissed (' + pct + '%)';
        const visible = document.querySelectorAll('.card:not(.hidden)').length;
        const emptyState = document.getElementById('empty-state');
        emptyState.style.display = visible === 0 ? 'block' : 'none';
    }}

    function dismissCards(cards) {{
        if (cards.length === 0) return;
        const snapshot = cards.map(c => ({{
            html: c.outerHTML,
            nextSibling: c.nextSibling
        }}));
        const grid = document.getElementById('grid');
        cards.forEach(c => c.classList.add('removing'));
        setTimeout(() => {{
            cards.forEach(c => c.remove());
            removed += cards.length;
            saveState();
            updateStats();
            const undoFn = () => {{
                snapshot.forEach(s => {{
                    const tmp = document.createElement('div');
                    tmp.innerHTML = s.html;
                    const card = tmp.firstElementChild;
                    card.classList.remove('removing');
                    if (s.nextSibling && s.nextSibling.parentNode === grid) {{
                        grid.insertBefore(card, s.nextSibling);
                    }} else {{
                        grid.insertBefore(card, document.getElementById('empty-state'));
                    }}
                }});
                removed -= snapshot.length;
                saveState();
                updateStats();
                toast(`↩ Restored ${{snapshot.length}} accounts`);
            }};
            toast(`✓ Dismissed ${{cards.length}} accounts`, 4000, undoFn);
        }}, 300);
    }}

    function dismissTop() {{
        const countInput = document.getElementById('dismiss-count');
        let count = parseInt(countInput.value);
        if (isNaN(count) || count < 1) count = 1;
        
        const visible = [...document.querySelectorAll('.card:not(.hidden)')];
        const targets = visible.slice(0, count);
        if (targets.length === 0) {{ toast('Nothing to dismiss!'); return; }}
        dismissCards(targets);
    }}

    function removeCard(btn) {{
        const card = btn.closest('.card');
        if (!card) return;
        dismissCards([card]);
    }}

    function openProfile(url) {{
        window.open(url, '_blank');
    }}

    function openLinks() {{
        const countInput = document.getElementById('action-count');
        let count = parseInt(countInput.value);
        if (isNaN(count) || count < 1) count = 1;
        
        const cards = [...document.querySelectorAll('.card:not(.hidden)')];
        if (cards.length === 0) {{ toast('No accounts visible!'); return; }}
        const targets = cards.slice(0, count);
        let blocked = 0;
        targets.forEach(card => {{
            const url = card.getAttribute('data-url');
            const w = window.open(url, '_blank');
            if (!w || w.closed) blocked++;
        }});
        const opened = targets.length - blocked;
        if (blocked > 0 && opened === 0) {{
            document.getElementById('popup-notice').classList.add('show');
        }} else {{
            toast(`✓ Opened ${{opened}} tabs`);
        }}
    }}

    function closePopup() {{
        document.getElementById('popup-notice').classList.remove('show');
    }}

    function copyUsername(username, btn) {{
        navigator.clipboard.writeText('@' + username).then(() => {{
            const originalText = btn.textContent;
            btn.textContent = '✓ Copied!';
            btn.classList.add('copied');
            setTimeout(() => {{ 
                btn.textContent = originalText; 
                btn.classList.remove('copied');
            }}, 1500);
        }});
    }}

    function debouncedFilter() {{
        clearTimeout(filterTimeout);
        filterTimeout = setTimeout(applyFilters, 300);
    }}

    function applyFilters() {{
        const q = document.getElementById('search').value.trim().toLowerCase();
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {{
            const user = card.getAttribute('data-username').toLowerCase();
            const matchQ = !q || user.includes(q);
            if (!matchQ) {{
                card.classList.add('hidden');
            }} else {{
                card.classList.remove('hidden');
            }}
        }});
        updateStats();
    }}

    function applySort() {{
        currentSort = document.getElementById('sort-select').value;
        const grid = document.getElementById('grid');
        const empty = document.getElementById('empty-state');
        const cards = [...document.querySelectorAll('.card')];
        cards.sort((a, b) => {{
            if (currentSort === 'alpha') {{
                return a.getAttribute('data-username').localeCompare(b.getAttribute('data-username'));
            }}
            if (currentSort === 'alpha-rev') {{
                return b.getAttribute('data-username').localeCompare(a.getAttribute('data-username'));
            }}
            const da = new Date(a.getAttribute('data-date'));
            const db = new Date(b.getAttribute('data-date'));
            return currentSort === 'asc' ? da - db : db - da;
        }});
        cards.forEach(c => grid.insertBefore(c, empty));
    }}

    function exportRemaining() {{
        // Export ALL remaining users (not just filtered ones)
        const cards = [...document.querySelectorAll('.card')];
        const list = cards.map(c => ({{
            username: c.getAttribute('data-username'),
            followed_date: c.querySelector('.badge-date').textContent,
            profile_url: c.getAttribute('data-url')
        }}));
        const blob = new Blob([JSON.stringify({{ 
            non_followers: list, 
            total: list.length,
            export_date: new Date().toISOString(),
            dismissed_count: removed
        }}, null, 2)], {{ type: 'application/json' }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `non_followers_${{Date.now()}}.json`;
        a.click();
        URL.revokeObjectURL(url);
        toast(`✓ Exported ${{list.length}} accounts`);
    }}

    function saveState() {{
        const remaining = [...document.querySelectorAll('.card')].map(c => c.getAttribute('data-username'));
        try {{ 
            localStorage.setItem('instaNoBack_remaining', JSON.stringify(remaining));
            localStorage.setItem('instaNoBack_dismissed_count', removed);
        }} catch(e) {{}}
    }}

    function restoreState() {{
        try {{
            const savedRemaining = localStorage.getItem('instaNoBack_remaining');
            if (savedRemaining) {{
                const remainingSet = new Set(JSON.parse(savedRemaining));
                document.querySelectorAll('.card').forEach(card => {{
                    if (!remainingSet.has(card.getAttribute('data-username'))) {{
                        card.remove();
                        removed++;
                    }}
                }});
            }}
        }} catch(e) {{}}
        updateStats();
    }}

    // Initialize sorting on page load
    function initializeSort() {{
        const grid = document.getElementById('grid');
        const empty = document.getElementById('empty-state');
        const cards = [...document.querySelectorAll('.card')];
        cards.sort((a, b) => {{
            const da = new Date(a.getAttribute('data-date'));
            const db = new Date(b.getAttribute('data-date'));
            return db - da; // Newest first
        }});
        cards.forEach(c => grid.insertBefore(c, empty));
    }}

    // Initialize
    window.addEventListener('DOMContentLoaded', () => {{
        initializeSort();
        restoreState();
    }});
</script>
</body>
</html>
"""

with open('instagram_nonfollowers.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✓ Dashboard created successfully!")
print(f"  Total accounts: {total_users}")
print(f"\n✅ Open 'instagram_nonfollowers.html' in your browser to use the dashboard.")