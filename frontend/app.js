// --- State Management ---
let currentConversation = [];
let chatsHistory = JSON.parse(localStorage.getItem('genie_v22_history') || '[]');
let currentChatId = null;
let currentUser = null;

// --- New Chat Handlers ---
function initiateNewChat() {
    currentConversation = [];
    currentChatId = null;
    document.getElementById('current-title').innerText = 'New Intelligence';
    renderFlow();
    setTimeout(() => document.getElementById('ai-input').focus(), 100);
}

// --- Auth Architecture ---
async function fetchUser() {
    try {
        const resp = await fetch('/api/me');
        if (resp.status === 401) {
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
            return;
        }
        currentUser = await resp.json();
        updateUIWithUser(currentUser);
    } catch (e) {
        console.error("Auth Check Failed:", e);
    }
}

function updateUIWithUser(user) {
    document.getElementById('username-display').innerText = user.name;
    document.getElementById('user-email').innerText = user.email;
    document.getElementById('user-avatar').src = user.picture || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(user.name);
    lucide.createIcons();
}

function handleLogout() {
    window.location.href = '/auth/logout';
}

// --- Messaging Engine ---
async function handleRequest() {
    const aiInput = document.getElementById('ai-input');
    const fireBtn = document.getElementById('fire-request');
    const text = aiInput.value.trim();
    
    if (!text || fireBtn.disabled) return;
    
    currentConversation.push({ role: 'user', text });
    aiInput.value = ''; 
    aiInput.style.height = '64px';
    fireBtn.disabled = true;
    renderFlow();

    const botMsg = { role: 'bot', answer: "Synthesizing data insight...", streaming: false };
    currentConversation.push(botMsg);
    renderFlow();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: text })
        });
        
        if (response.status === 401) {
            window.location.href = '/login';
            return;
        }

        const result = await response.json();
        currentConversation[currentConversation.length - 1] = {
            role: 'bot', answer: result.answer, query: result.query,
            data: result.data, suggested_questions: result.suggested_questions, streaming: true
        };
        renderFlow();
        saveSession();
    } catch (e) {
        currentConversation[currentConversation.length - 1].answer = "Network connectivity lost.";
        renderFlow();
    } finally {
        fireBtn.disabled = false;
        aiInput.focus();
    }
}

// --- Rich Rendering Persistence ---
function saveSession() {
    if (currentConversation.length === 0) return;
    if (!currentChatId) {
        currentChatId = Date.now();
        const first = currentConversation.find(m => m.role === 'user');
        const title = first ? (first.text.substring(0, 30) + '...') : 'Genie Session';
        chatsHistory.unshift({ id: currentChatId, title, messages: [...currentConversation] });
    } else {
        const index = chatsHistory.findIndex(ch => ch.id === currentChatId);
        if (index !== -1) chatsHistory[index].messages = [...currentConversation];
    }
    localStorage.setItem('genie_v22_history', JSON.stringify(chatsHistory));
    renderHistory();
}

function renderHistory() {
    const list = document.getElementById('history-list');
    list.innerHTML = '';
    chatsHistory.forEach(chat => {
        const div = document.createElement('div');
        div.className = "group flex items-center gap-3 p-3 rounded-xl hover:bg-white/5 cursor-pointer text-slate-400 hover:text-white transition-all";
        div.innerHTML = `<i data-lucide="message-square" class="w-4 h-4"></i> <span class="text-xs font-medium truncate">${chat.title}</span>`;
        div.onclick = () => {
            currentChatId = chat.id;
            currentConversation = [...chat.messages];
            document.getElementById('current-title').innerText = chat.title;
            renderFlow();
        };
        list.appendChild(div);
    });
    lucide.createIcons();
}

// (Helper rendering functions like createSQLBlock, createDataVisual, typeMessage, initChart, etc. 
// follow the same optimized patterns we built previously)

window.copyToClipboard = async (id, btn) => {
    try {
        await navigator.clipboard.writeText(document.getElementById(id).innerText);
        const originalHtml = btn.innerHTML;
        btn.innerHTML = `<i data-lucide="check" class="w-3 h-3 text-green-400"></i> <span class="text-green-400">Copied!</span>`;
        lucide.createIcons();
        setTimeout(() => {
            btn.innerHTML = originalHtml;
            lucide.createIcons();
        }, 2000);
    } catch (err) {
        console.error('Copy failed', err);
    }
};

function createSQLBlock(sql) {
    if (!sql) return '';
    const id = 'sql-' + Math.random().toString(36).substr(2, 9);
    return `<div class="mt-4 bg-[#0a0a0a] rounded-xl overflow-hidden border border-white/5 shadow-2xl">
                <div class="flex justify-between items-center px-4 py-2 bg-gradient-to-r from-white/5 to-transparent border-b border-white/5">
                    <span class="text-[9px] font-black text-blue-500 uppercase tracking-[0.2em]">Data Logic Layer</span>
                    <button onclick="copyToClipboard('${id}', this)" class="text-[10px] text-slate-500 hover:text-white flex items-center gap-1.5 transition-colors">
                        <i data-lucide="copy" class="w-3 h-3"></i> Copy Logic
                    </button>
                </div>
                <pre class="p-5 overflow-x-auto custom-scrollbar"><code id="${id}" class="text-blue-400/90 font-mono text-[11px] leading-relaxed">${sql}</code></pre>
            </div>`;
}

function createDataVisual(data) {
    if (!data || !data.rows || data.rows.length === 0) return '';
    const numericColIndex = data.rows[0].findIndex((val, i) => i > 0 && !isNaN(parseFloat(val)));
    if (numericColIndex !== -1 && data.rows.length <= 25) {
        return `<div class="mt-6 bg-white p-6 rounded-2xl border border-slate-100 shadow-xl"><div class="h-[280px] relative"><canvas class="chart-canvas-element"></canvas></div></div>`;
    }
    let html = `<div class="mt-4 overflow-x-auto rounded-xl border border-slate-200 bg-white"><table class="w-full text-sm">`;
    html += `<thead class="bg-slate-50 text-[10px] uppercase font-bold text-slate-500"><tr>`;
    data.columns.forEach(col => html += `<th class="px-4 py-3">${col}</th>`);
    html += `</tr></thead><tbody class="divide-y divide-slate-100">`;
    data.rows.slice(0, 10).forEach(row => {
        html += `<tr>`;
        row.forEach(cell => html += `<td class="px-4 py-3 text-slate-600">${cell}</td>`);
        html += `</tr>`;
    });
    html += `</tbody></table></div>`;
    return html;
}

async function typeMessage(element, fullText, onFinish) {
    const words = fullText.split(' ');
    let currentText = "";
    element.innerHTML = "";
    for (let i = 0; i < words.length; i++) {
        currentText += words[i] + " ";
        element.innerHTML = marked.parse(currentText);
        document.getElementById('chat-canvas').scrollTop = document.getElementById('chat-canvas').scrollHeight;
        await new Promise(r => setTimeout(r, 5));
    }
    if (onFinish) onFinish();
}

function renderFlow() {
    const messageContainer = document.getElementById('message-container');
    messageContainer.innerHTML = '';
    const welcomeMsg = document.getElementById('welcome-msg');
    if (currentConversation.length > 0) welcomeMsg.classList.add('hidden');
    else welcomeMsg.classList.remove('hidden');

    currentConversation.forEach((msg, idx) => {
        const row = document.createElement('div');
        row.className = `flex w-full mb-8 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`;
        const bubble = document.createElement('div');
        bubble.className = `max-w-[85%] p-6 rounded-3xl shadow-sm text-[15px] relative ${
            msg.role === 'user' ? 'bg-slate-900 text-white rounded-br-none' : 'bg-white border border-slate-100 text-slate-800 rounded-bl-none shadow-md'
        }`;
        row.appendChild(bubble);
        messageContainer.appendChild(row);

        if (msg.role === 'user') {
            bubble.innerText = msg.text;
        } else {
            if (msg.streaming && idx === currentConversation.length - 1) {
                typeMessage(bubble, msg.answer, () => {
                    msg.streaming = false;
                    renderBotPayload(bubble, msg);
                });
            } else {
                bubble.innerHTML = marked.parse(msg.answer || msg.text);
                renderBotPayload(bubble, msg);
            }
        }
    });
    document.getElementById('chat-canvas').scrollTop = document.getElementById('chat-canvas').scrollHeight;
}

function renderBotPayload(bubble, msg) {
    let payloadHtml = marked.parse(msg.answer || msg.text);
    if (msg.query) payloadHtml += createSQLBlock(msg.query);
    if (msg.data) payloadHtml += createDataVisual(msg.data);
    if (msg.suggested_questions) {
        payloadHtml += `<div class="mt-6 flex flex-wrap gap-2">`;
        msg.suggested_questions.forEach(q => {
            payloadHtml += `<button onclick="setQuery('${q.replace(/'/g, "\\'")}'); handleRequest();" class="px-3 py-1.5 bg-blue-50 text-blue-600 rounded-full border border-blue-100 text-[11px] font-bold hover:bg-blue-600 hover:text-white transition-all shadow-sm">${q}</button>`;
        });
        payloadHtml += `</div>`;
    }
    bubble.innerHTML = payloadHtml;
    if (msg.data) {
        const canvas = bubble.querySelector('.chart-canvas-element');
        if (canvas) setTimeout(() => initChart(canvas, msg.data), 150);
    }
    lucide.createIcons();
}

function initChart(canvas, data) {
    const valIdx = data.rows[0].findIndex((val, i) => i > 0 && !isNaN(parseFloat(val)));
    const labels = data.rows.map(r => r[0]);
    const values = data.rows.map(r => parseFloat(r[valIdx]) || 0);
    
    // Luxury dynamic chart selection
    let chartType = 'bar';
    if (data.rows.length <= 5) chartType = 'doughnut';
    else if (data.rows.length > 15 || labels.some(l => l.includes('-') || l.includes('/'))) chartType = 'line';

    new Chart(canvas, {
        type: chartType,
        data: {
            labels: labels,
            datasets: [{
                label: data.columns[valIdx],
                data: values,
                backgroundColor: chartType === 'line' ? 'rgba(99, 102, 241, 0.1)' : ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f59e0b'],
                borderColor: chartType === 'line' ? '#6366f1' : 'transparent',
                borderWidth: chartType === 'line' ? 3 : 0,
                borderRadius: chartType === 'bar' ? 6 : 0,
                fill: chartType === 'line',
                tension: 0.4,
                pointRadius: chartType === 'line' ? 4 : 0,
                pointBackgroundColor: '#6366f1'
            }]
        },
        options: { 
            responsive: true, 
            maintainAspectRatio: false,
            plugins: {
                legend: { display: chartType === 'doughnut', position: 'bottom', labels: { boxWidth: 12, usePointStyle: true, font: { size: 10 } } }
            },
            scales: chartType !== 'doughnut' ? {
                y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.03)' }, border: { display: false }, ticks: { font: { size: 10 } } },
                x: { grid: { display: false }, border: { display: false }, ticks: { font: { size: 10 } } }
            } : {}
        }
    });
}

// --- Responsive Navigation ---
function toggleSidebarSync() {
    document.body.classList.toggle('sidebar-closed');
    document.getElementById('sidebar').classList.toggle('sidebar-collapse');
    lucide.createIcons();
}

// --- Media Synthesis Hub (+) Logic ---
let selectedFiles = [];

function handleMediaSelect(input) {
    const feedback = document.getElementById('media-feedback');
    feedback.innerHTML = ''; // Clear old
    selectedFiles = Array.from(input.files);

    selectedFiles.forEach(file => {
        const item = document.createElement('div');
        item.className = "flex items-center gap-2 bg-white/80 backdrop-blur-md px-3 py-1.5 rounded-full border border-blue-100 shadow-sm animate-in fade-in slide-in-from-bottom-2";
        
        let icon = "file";
        if (file.type.startsWith('image/')) icon = "image";
        if (file.type.startsWith('audio/')) icon = "mic";
        
        item.innerHTML = `
            <i data-lucide="${icon}" class="w-3.5 h-3.5 text-blue-600"></i>
            <span class="text-[10px] font-bold text-slate-700 truncate max-w-[80px]">${file.name}</span>
            <button onclick="removeFile('${file.name}')" class="text-slate-400 hover:text-red-500"><i data-lucide="x" class="w-3 h-3"></i></button>
        `;
        feedback.appendChild(item);
    });
    lucide.createIcons();
}

window.removeFile = (name) => {
    selectedFiles = selectedFiles.filter(f => f.name !== name);
    // Refresh feedback
    const input = document.getElementById('media-upload');
    const dt = new DataTransfer();
    selectedFiles.forEach(f => dt.items.add(f));
    input.files = dt.files;
    handleMediaSelect(input);
};

// Update handleRequest to include "Media Uploading" simulation
const originalHandleRequest = handleRequest;
window.handleRequest = async () => {
    if (selectedFiles.length > 0) {
        console.log("Analyzing media bundle...", selectedFiles);
        // Clear media after simulated read
        document.getElementById('media-feedback').innerHTML = '';
        selectedFiles = [];
    }
    await originalHandleRequest();
};

window.toggleSidebarSync = toggleSidebarSync;
window.handleMediaSelect = handleMediaSelect;

// --- Global Exports ---
window.handleLogout = handleLogout;
window.setQuery = (q) => { 
    const input = document.getElementById('ai-input');
    input.value = q; input.focus(); 
    document.getElementById('fire-request').disabled = false;
};

// --- Initialization ---
lucide.createIcons();
marked.setOptions({ breaks: true, gfm: true });
fetchUser();
renderHistory();
renderFlow();

// Handle responsive sidebar behavior on mobile
if (window.innerWidth < 768) {
    document.body.classList.add('sidebar-closed');
    document.getElementById('sidebar').classList.add('sidebar-collapse');
}

document.getElementById('ai-input').oninput = (e) => { 
    document.getElementById('fire-request').disabled = !e.target.value.trim(); 
    e.target.style.height = 'auto'; e.target.style.height = e.target.scrollHeight + 'px';
};
document.getElementById('ai-input').onkeydown = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleRequest(); } };
document.getElementById('fire-request').onclick = handleRequest;
document.getElementById('new-chat-btn').onclick = initiateNewChat;
