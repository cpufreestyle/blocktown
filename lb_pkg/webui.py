"""Luanti Builder - webui 模块。"""

# ============================================================
# Web 服务器
# ============================================================

HTML_PAGE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Luanti 自然语言建筑生成器</title>
<style>
:root {
  --bg: #0f0f1e;
  --bg-card: #16213e;
  --bg-deep: #0d1117;
  --bg-input: #1a1a2e;
  --accent: #50fa7b;
  --accent-dim: #0f3460;
  --accent-bright: #1a4080;
  --text: #e0e0e0;
  --text-dim: #6272a4;
  --text-bright: #ffffff;
  --border: #1a2040;
  --radius: 10px;
  --transition: 0.2s cubic-bezier(0.4,0,0.2,1);
}
* { margin:0; padding:0; box-sizing:border-box; }
body {
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",sans-serif;
  background:var(--bg); color:var(--text); min-height:100vh; font-size:15px;
  -webkit-font-smoothing:antialiased;
}
.container { max-width:960px; margin:0 auto; padding:24px 20px 60px; }

/* Header */
h1 { text-align:center; font-size:26px; margin:10px 0 6px; color:var(--accent); }
.subtitle { text-align:center; color:var(--text-dim); font-size:14px; margin-bottom:20px; }

/* Cards */
.card {
  background:var(--bg-card); border-radius:var(--radius); padding:22px;
  margin-bottom:16px; box-shadow:0 2px 8px rgba(0,0,0,0.25);
  transition:box-shadow var(--transition);
}
.card:hover { box-shadow:0 4px 16px rgba(0,0,0,0.35); }

/* Labels */
label { display:block; font-size:15px; color:var(--text-dim); margin-bottom:8px; font-weight:500; }
.section-label { font-size:12px; color:var(--text-dim); text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; font-weight:600; }

/* Inputs */
input[type="text"] {
  width:100%; padding:14px; font-size:17px; border:2px solid var(--accent-dim);
  border-radius:8px; background:var(--bg-input); color:var(--text-bright);
  transition:border-color var(--transition);
}
input[type="text"]:focus { outline:none; border-color:var(--accent); }
select {
  padding:8px 12px; background:var(--bg-input); color:var(--text);
  border:1px solid var(--accent-dim); border-radius:6px; font-size:14px;
}

/* Examples */
.examples { margin-top:10px; }
.example-btn {
  display:inline-block; background:var(--accent-dim); color:#8be9fd;
  padding:6px 12px; border-radius:6px; font-size:13px; margin:4px;
  cursor:pointer; border:1px solid var(--accent-bright); transition:var(--transition);
}
.example-btn:hover { background:var(--accent-bright); transform:translateY(-1px); }

/* Button groups */
.btn-group { margin-bottom:14px; }
.btn-row { display:flex; gap:10px; flex-wrap:wrap; }

button {
  padding:12px 20px; font-size:15px; border:none; border-radius:8px;
  cursor:pointer; font-weight:600; transition:var(--transition);
  display:inline-flex; align-items:center; gap:6px;
}
button:active { transform:scale(0.97); }
button:disabled { opacity:0.5; cursor:not-allowed; }
.btn-parse { background:var(--accent-dim); color:#8be9fd; }
.btn-parse:hover { background:var(--accent-bright); }
.btn-gen { background:#5046e5; color:#fff; }
.btn-gen:hover { background:#6056f5; }
.btn-install { background:var(--accent); color:var(--bg); }
.btn-install:hover { background:#60ffa0; box-shadow:0 0 12px rgba(80,250,123,0.4); }
.btn-all { background:#ff79c6; color:#fff; }
.btn-all:hover { background:#ff99d6; }
.btn-preview { background:#f1fa8c; color:var(--bg); }
.btn-preview:hover { background:#ffffaa; }
.btn-launch { background:var(--accent); color:var(--bg); border:2px solid var(--accent); }
.btn-launch:hover { background:#60ffa0; box-shadow:0 0 12px var(--accent); }
.btn-ai { background:#bd93f9; color:var(--bg); }
.btn-ai:hover { background:#caa0ff; }
.btn-ai-all { background:#ff6b6b; color:#fff; }
.btn-ai-all:hover { background:#ff8585; box-shadow:0 0 12px rgba(255,107,107,0.4); }
.btn-sm { padding:6px 12px; font-size:13px; }
.btn-ghost { background:transparent; color:var(--text-dim); border:1px solid var(--accent-dim); }
.btn-ghost:hover { background:var(--bg-input); color:var(--text); }

/* Collapsible AI settings */
.collapsible-header {
  display:flex; align-items:center; justify-content:space-between;
  cursor:pointer; padding:10px 0; user-select:none;
}
.collapsible-header .chevron { transition:transform var(--transition); }
.collapsible-header.open .chevron { transform:rotate(90deg); }
.collapsible-body {
  max-height:0; overflow:hidden; transition:max-height 0.3s ease;
}
.collapsible-body.open { max-height:600px; }

/* AI settings */
.ai-settings { background:var(--bg-deep); border:1px solid #333; border-radius:8px; padding:14px; margin-top:12px; }
.ai-settings label { font-size:13px; color:var(--text-dim); margin-bottom:4px; }
.ai-settings input { width:100%; padding:8px; background:var(--bg-input); color:var(--text); border:1px solid var(--accent-dim); border-radius:6px; font-size:14px; margin-bottom:8px; }
.ai-settings input:focus { outline:none; border-color:var(--accent); }
.ai-row { display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; }
@media(max-width:600px) { .ai-row { grid-template-columns:1fr; } }

/* Loading */
.ai-loading { display:none; text-align:center; padding:20px; }
.ai-loading.show { display:block; }
.spinner { display:inline-block; width:32px; height:32px; border:3px solid #333; border-top:3px solid var(--accent); border-radius:50%; animation:spin 1s linear infinite; }
.loading-text { margin-top:10px; color:var(--text-dim); font-size:14px; }
.loading-dots::after { content:''; animation:dots 1.5s steps(4) infinite; }
@keyframes dots { 0%{content:''} 25%{content:'.'} 50%{content:'..'} 75%{content:'...'} 100%{content:''} }

/* History */
.history-item { display:flex; gap:8px; align-items:center; padding:6px 10px; border-radius:6px; cursor:pointer; font-size:13px; border-bottom:1px solid var(--border); transition:var(--transition); }
.history-item:hover { background:var(--accent-dim); }
.history-time { color:var(--text-dim); font-size:11px; white-space:nowrap; }
.history-text { color:var(--text); flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.history-count { color:var(--accent); font-size:11px; white-space:nowrap; }

/* Tabs */
.tab-bar { display:flex; gap:8px; margin-bottom:16px; border-bottom:2px solid var(--accent-dim); padding-bottom:8px; }
.tab-btn { padding:10px 20px; background:var(--bg-card); color:var(--text-dim); border:1px solid var(--accent-dim); border-radius:8px 8px 0 0; cursor:pointer; font-size:15px; font-weight:600; transition:var(--transition); }
.tab-btn.active { background:var(--accent-bright); color:var(--accent); border-color:var(--accent); }
.tab-btn:hover:not(.active) { background:var(--bg-input); color:var(--text); }
.tab-panel { display:none; animation:fadeIn 0.3s ease; }
.tab-panel.active { display:block; }
@keyframes fadeIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }

/* NPC cards */
.npc-grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(180px, 1fr)); gap:12px; margin-bottom:16px; }
.npc-card { background:var(--bg-card); border:2px solid #333; border-radius:10px; padding:14px; cursor:pointer; transition:var(--transition); position:relative; }
.npc-card:hover { transform:translateY(-3px); box-shadow:0 6px 16px rgba(0,0,0,0.4); }
.npc-card.selected { border-color:var(--accent); box-shadow:0 0 12px rgba(80,250,123,0.3); }
.npc-card.selected::after { content:'✓'; position:absolute; top:6px; right:8px; color:var(--accent); font-weight:bold; }
.npc-emoji { font-size:32px; text-align:center; }
.npc-name { font-size:17px; font-weight:700; text-align:center; margin:6px 0; }
.npc-role { font-size:13px; color:#8be9fd; text-align:center; }
.npc-loc { font-size:12px; color:var(--text-dim); margin-top:6px; text-align:center; }
.npc-quest { font-size:12px; color:#f1fa8c; margin-top:4px; text-align:center; }

/* Chat box */
.chat-box { background:var(--bg-deep); border-radius:10px; padding:14px; min-height:260px; max-height:420px; overflow-y:auto; margin-bottom:10px; font-size:14px; scroll-behavior:smooth; }
.chat-box::-webkit-scrollbar { width:6px; }
.chat-box::-webkit-scrollbar-track { background:transparent; }
.chat-box::-webkit-scrollbar-thumb { background:var(--accent-dim); border-radius:3px; }
.chat-msg { padding:10px 14px; margin-bottom:8px; border-radius:12px; max-width:80%; word-wrap:break-word; line-height:1.5; animation:slideIn 0.25s ease; }
@keyframes slideIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
.chat-user { background:var(--accent-dim); color:var(--text-bright); margin-left:auto; text-align:right; border-bottom-right-radius:4px; }
.chat-npc { background:#1a3a2a; color:#d0ffd0; border-bottom-left-radius:4px; }
.chat-npc .npc-avatar { font-size:20px; margin-right:6px; }
.typing-indicator { display:flex; gap:4px; align-items:center; padding:10px 14px; background:#1a3a2a; border-radius:12px; border-bottom-left-radius:4px; max-width:60px; animation:slideIn 0.25s ease; }
.typing-dot { width:8px; height:8px; background:var(--accent); border-radius:50%; animation:typingBounce 1.4s infinite; }
.typing-dot:nth-child(2) { animation-delay:0.2s; }
.typing-dot:nth-child(3) { animation-delay:0.4s; }
@keyframes typingBounce { 0%,60%,100%{transform:translateY(0);opacity:0.4} 30%{transform:translateY(-6px);opacity:1} }

/* NPC controls */
.npc-controls { display:flex; gap:12px; margin-bottom:10px; flex-wrap:wrap; align-items:center; }
.npc-control-item { display:flex; align-items:center; gap:6px; font-size:13px; color:var(--text-dim); }
.npc-control-item input[type="range"] { width:80px; accent-color:var(--accent); }
.npc-control-item select { padding:4px 8px; font-size:13px; }

/* Toast */
.toast-container { position:fixed; top:16px; right:16px; z-index:9999; display:flex; flex-direction:column; gap:8px; pointer-events:none; }
.toast {
  background:var(--bg-card); border-radius:8px; padding:12px 18px; font-size:14px;
  box-shadow:0 4px 12px rgba(0,0,0,0.4); max-width:360px; pointer-events:auto;
  animation:toastIn 0.3s ease; border-left:4px solid var(--accent);
}
.toast.ok { border-left-color:var(--accent); }
.toast.warn { border-left-color:#f1fa8c; }
.toast.err { border-left-color:#ff5555; }
.toast.hide { animation:toastOut 0.3s ease forwards; }
@keyframes toastIn { from{opacity:0;transform:translateX(100px)} to{opacity:1;transform:translateX(0)} }
@keyframes toastOut { to{opacity:0;transform:translateX(100px)} }

/* Preview */
.preview-container { position:relative; background:var(--bg-deep); border-radius:8px; border:1px solid #333; overflow:hidden; }
.preview-canvas { display:block; margin:0 auto; cursor:grab; touch-action:none; }
.preview-canvas:active { cursor:grabbing; }
.preview-controls { position:absolute; top:8px; right:8px; display:flex; gap:6px; }
.preview-controls button { padding:5px 12px; font-size:13px; background:var(--accent-dim); color:#8be9fd; border-radius:4px; }
.preview-controls button:hover { background:var(--accent-bright); }
.preview-info { position:absolute; bottom:8px; left:8px; font-size:12px; color:var(--text-dim); background:rgba(0,0,0,0.5); padding:4px 8px; border-radius:4px; }

/* Result / Code */
.result { background:var(--bg-deep); border-radius:8px; padding:14px; font-family:monospace; font-size:14px; white-space:pre-wrap; color:#8be9fd; min-height:50px; }
.code-box { background:var(--bg-deep); border-radius:8px; padding:14px; font-family:"Courier New",monospace; font-size:13px; white-space:pre; overflow:auto; max-height:400px; color:#c0c0c0; border:1px solid #333; }

/* Status bar (kept for path info) */
.status { padding:10px 18px; border-radius:8px; margin-top:10px; font-size:15px; }
.status-ok { background:#1a3a1a; color:var(--accent); }
.status-warn { background:#3a3a1a; color:#f1fa8c; }
.status-err { background:#3a1a1a; color:#ff5555; }
.path-info { font-size:13px; color:var(--text-dim); margin-top:8px; word-break:break-all; }

/* Grid */
.grid { display:grid; grid-template-columns:1fr 1fr; gap:18px; }
@media(max-width:600px) { .grid { grid-template-columns:1fr; } .btn-row { flex-direction:column; } }

/* Table */
table { width:100%; border-collapse:collapse; font-size:14px; }
th,td { padding:8px 12px; border-bottom:1px solid #333; text-align:left; }
th { color:var(--accent); }
td { color:var(--text-dim); }

/* Install steps */
.install-steps { background:var(--bg-deep); border-radius:10px; padding:16px; font-size:14px; color:var(--text-dim); line-height:1.8; }
.install-steps code { background:var(--bg-input); padding:2px 6px; border-radius:4px; color:#8be9fd; }

@keyframes spin { 0%{transform:rotate(0)} 100%{transform:rotate(360deg)} }
@media(max-width:600px) { .container { padding:16px 12px 40px; } h1 { font-size:22px; } .npc-grid { grid-template-columns:1fr 1fr; } .npc-controls { flex-direction:column; align-items:flex-start; } }
</style>
</head>
<body>
<div class="toast-container" id="toastContainer"></div>
<div class="container">
<h1>🏗️ Luanti 工具套件</h1>
<p class="subtitle">自然语言建筑生成 + AI 小镇 NPC 对话</p>

<div class="tab-bar">
<button class="tab-btn active" data-tab="builder" onclick="switchTab('builder')">🏗️ 建筑生成器</button>
<button class="tab-btn" data-tab="town" onclick="switchTab('town')">🏘️ AI 小镇</button>
</div>

<div id="tab-builder" class="tab-panel active">
<div class="card">
<label>描述你想要的建筑：</label>
<input type="text" id="input" value="建一个红色的城堡，有塔楼" placeholder="例如：建造一座大型金字塔">
<div style="display:flex; gap:6px; margin-top:6px; align-items:center;">
<button id="micBtn" onclick="toggleVoice('input', function(){ doParse(); doPreview(); })" style="padding:6px 12px; background:var(--bg-input); color:var(--text); border:1px solid var(--accent-dim); border-radius:6px; font-size:14px; cursor:pointer;">🎤 语音输入</button>
<span id="micStatus" style="font-size:12px; color:var(--text-dim);">点击开始说话 (浏览器语音识别)</span>
</div>
<div class="examples">
<span style="color:#666;font-size:12px">示例：</span>
<span class="example-btn" onclick="setInput(this.textContent)">建一个红色的城堡，有塔楼</span>
<span class="example-btn" onclick="setInput(this.textContent)">建造一座大型金字塔</span>
<span class="example-btn" onclick="setInput(this.textContent)">做一个发光的灯塔</span>
<span class="example-btn" onclick="setInput(this.textContent)">建一座桥</span>
<span class="example-btn" onclick="setInput(this.textContent)">建造一个花园</span>
<span class="example-btn" onclick="setInput(this.textContent)">做一个爱心</span>
<span class="example-btn" onclick="setInput(this.textContent)">建一座神殿</span>
<span class="example-btn" onclick="setInput(this.textContent)">建造一棵巨大的树</span>
<span class="example-btn" onclick="setInput(this.textContent)">做一个飞船</span>
<span class="example-btn" onclick="setInput(this.textContent)">建一个村庄</span>
</div>

<!-- 快捷操作 -->
<div class="btn-group" style="margin-top:14px;">
<div class="section-label">快捷操作</div>
<div class="btn-row">
<button class="btn-parse" onclick="doParse()">🔍 解析</button>
<button class="btn-gen" onclick="doGen()">📋 生成 Lua</button>
<button class="btn-preview" onclick="doPreview()">👁️ 预览</button>
</div>
</div>

<!-- 一键流程 -->
<div class="btn-group">
<div class="section-label">一键流程</div>
<div class="btn-row">
<button class="btn-install" onclick="doInstall()">💾 安装</button>
<button class="btn-all" onclick="doAll()">🚀 生成并安装</button>
<button class="btn-launch" onclick="doJoin()">🎮 一键加入游戏</button>
</div>
<div class="btn-row" style="margin-top:8px;">
<button class="btn-ai" onclick="doAIPreview()">🤖 AI 预览</button>
<button class="btn-ai-all" onclick="doAIGenerate()">🤖 AI 生成并加入</button>
</div>
</div>

<div style="margin-top:8px; display:flex; align-items:center; gap:8px;">
<label style="font-size:13px; color:var(--text-dim); white-space:nowrap;">选择世界:</label>
<select id="worldSelect" style="flex:1; padding:6px; background:var(--bg-input); color:var(--text); border:1px solid var(--accent-dim); border-radius:6px; font-size:13px;">
<option value="">自动选择</option>
</select>
</div>

<!-- AI 大模型设置 (折叠) -->
<div class="ai-settings">
  <div class="collapsible-header" id="aiSettingsToggle" onclick="toggleCollapsible('aiSettingsToggle','aiSettingsBody')">
    <span style="font-size:15px; font-weight:600;">🤖 AI 大模型设置</span>
    <span class="chevron" style="color:var(--accent); font-size:18px;">▶</span>
  </div>
  <div class="collapsible-body" id="aiSettingsBody">
    <div style="margin-bottom:10px; margin-top:8px;">
    <label>快速选择</label>
    <select id="aiProvider" onchange="switchProvider()" style="width:100%; padding:8px; background:var(--bg-input); color:var(--text); border:1px solid var(--accent-dim); border-radius:6px; font-size:14px;">
    <optgroup label="─ 国内可用 ─">
    <option value="deepseek">DeepSeek (推荐, 便宜)</option>
    <option value="zhipu">智谱 GLM (免费额度)</option>
    <option value="qwen">通义千问 阿里 (免费额度)</option>
    <option value="moonshot">Moonshot Kimi (长上下文)</option>
    <option value="baichuan">百川 Baichuan</option>
    <option value="minimax">MiniMax</option>
    <option value="yi">零一万物 Yi</option>
    <option value="stepfun">阶跃星辰 Step</option>
    <option value="sensetime">商汤 SenseNova</option>
    <option value="iflytek">讯飞星火 iFlyTek</option>
    <option value="hunyuan">腾讯混元</option>
    <option value="ernie">百度文心 ERNIE</option>
    <option value="volcengine">火山引擎 豆包</option>
    <option value="siliconflow">硅基流动 SiliconFlow (聚合, 免费)</option>
    <option value="openrouter_cn">OpenRouter (国内代理)</option>
    </optgroup>
    <optgroup label="─ 国际 ─">
    <option value="openai">OpenAI GPT (需翻墙)</option>
    <option value="anthropic">Anthropic Claude (需翻墙)</option>
    <option value="google">Google Gemini (需翻墙)</option>
    <option value="openrouter">OpenRouter (聚合, 需翻墙)</option>
    <option value="groq">Groq (超快, 需翻墙)</option>
    <option value="together">Together AI (需翻墙)</option>
    <option value="mistral">Mistral AI (需翻墙)</option>
    <option value="cohere">Cohere (需翻墙)</option>
    <option value="perplexity">Perplexity (需翻墙)</option>
    <option value="anyscale">Anyscale (需翻墙)</option>
    <option value="fireworks">Fireworks AI (需翻墙)</option>
    <option value="lepton">Lepton AI (需翻墙)</option>
    <option value="novita">Novita AI (需翻墙)</option>
    </optgroup>
    <optgroup label="─ 其他 ─">
    <option value="ollama">Ollama 本地模型 (免费, 需安装)</option>
    <option value="lmstudio">LM Studio 本地 (免费, 需安装)</option>
    <option value="custom">自定义</option>
    </optgroup>
    </select>
    </div>
    <div class="ai-row">
    <div>
    <label>API Key</label>
    <input type="text" id="apiKey" placeholder="sk-..." oninput="saveAIConfig()">
    </div>
    <div>
    <label>Base URL</label>
    <input type="text" id="baseUrl" value="https://api.deepseek.com/v1" oninput="saveAIConfig()">
    </div>
    <div>
    <label>模型</label>
    <input type="text" id="modelName" value="deepseek-chat" oninput="saveAIConfig()">
    </div>
    </div>
    <p style="font-size:12px; color:var(--text-dim); margin-top:6px;">API Key 保存在浏览器本地，不会上传。</p>
  </div>
</div>

<!-- 对话式迭代建造 -->
<div class="card" style="border:1px solid var(--accent-dim); margin-top:12px;">
  <div class="collapsible-header open" id="chatToggle" onclick="toggleCollapsible('chatToggle','chatBody')">
    <span style="font-size:15px; font-weight:600;">💬 对话式迭代建造</span>
    <span class="chevron" style="color:var(--accent); font-size:18px;">▶</span>
  </div>
  <div class="collapsible-body open" id="chatBody">
    <div id="chatBox" style="max-height:200px; overflow-y:auto; background:var(--bg-deep); border:1px solid #333; border-radius:8px; padding:8px; margin-bottom:8px; font-size:13px;">
    <div style="color:var(--text-dim);">开始新对话：描述一个建筑，AI 生成后可继续提修改要求。</div>
    </div>
    <div style="display:flex; gap:6px;">
    <input type="text" id="chatInput" placeholder="例如：把屋顶改成金色" onkeydown="if(event.key==='Enter')sendChat(false)" style="flex:1; padding:8px; background:var(--bg-input); color:var(--text); border:1px solid var(--accent-dim); border-radius:6px; font-size:14px;">
    <button id="chatMicBtn" onclick="toggleVoice('chatInput', function(){ sendChat(false); })" style="padding:6px 10px; background:var(--bg-input); color:var(--text); border:1px solid var(--accent-dim); border-radius:6px; cursor:pointer;">🎤</button>
    <button class="btn-ai" onclick="sendChat(false)">💬 发送</button>
    <button class="btn-ai-all" onclick="sendChat(true)">🚀 修改并加入</button>
    <button class="btn-ghost btn-sm" onclick="resetChat()">🔄</button>
    </div>
  </div>
</div>

<!-- AI 加载动画 -->
<div class="ai-loading" id="aiLoading">
<div class="spinner"></div>
<p class="loading-text" id="loadingText">🤖 AI 正在生成建筑<span class="loading-dots"></span></p>
</div>
</div>

<div class="card">
<label>📜 生成历史 (点击可回看)</label>
<div id="historyList" style="max-height:120px; overflow-y:auto;"></div>
</div>

<div class="card">
<label>解析结果：</label>
<div class="result" id="result">等待输入...</div>
</div>

<div class="card">
<label>状态：</label>
<div id="status" class="status status-warn">就绪</div>
<div class="path-info" id="pathInfo"></div>
</div>
</div>

<div class="card">
<label>生成的 Lua 代码：</label>
<div class="code-box" id="code">点击「生成 Lua」按钮查看代码</div>
</div>

<div class="card">
<label>3D 预览 (拖拽旋转 · 滚轮缩放)：</label>
<div class="preview-container">
<canvas id="previewCanvas" class="preview-canvas" width="600" height="400"></canvas>
<div class="preview-controls">
<button onclick="zoomPreview(1.2)">➕</button>
<button onclick="zoomPreview(0.8)">➖</button>
<button onclick="resetPreview()">🔄</button>
</div>
<div class="preview-info" id="previewInfo"></div>
</div>
<div class="btn-row" style="margin-top:10px; align-items:center;">
<button class="btn-ai btn-sm" onclick="refineLoop()" id="refineBtn" disabled>🔄 AI 审美迭代</button>
<select id="refineRounds" style="padding:5px 8px; font-size:13px;">
<option value="1">迭代 1 轮</option>
<option value="2">迭代 2 轮</option>
<option value="3">迭代 3 轮</option>
</select>
<span style="font-size:12px; color:var(--text-dim);">需 AI 生成后可用 · 视觉模型效果更佳 (不支持时自动纯文本评审)</span>
</div>
<div class="btn-row" style="margin-top:10px;">
<button class="btn-ghost btn-sm" onclick="exportBlueprint()">📤 导出蓝图</button>
<button class="btn-ghost btn-sm" onclick="copyShareLink()">🔗 复制分享链接</button>
<button class="btn-ghost btn-sm" onclick="importBlueprint()">📥 导入蓝图</button>
<input type="file" id="bpFile" accept=".json" style="display:none;" onchange="handleBpFile(event)">
</div>
</div>

<div class="card">
<label>📦 蓝图库 (保存在浏览器本地)</label>
<div id="bpList" style="max-height:140px; overflow-y:auto;"></div>
<div class="btn-row" style="margin-top:8px;">
<button class="btn-parse btn-sm" onclick="saveBlueprintDialog()">💾 保存当前建筑</button>
</div>
</div>

<div class="card">
<label>支持的建筑类型：</label>
<table>
<tr><th>类型</th><th>关键词</th><th>类型</th><th>关键词</th></tr>
<tr><td>🏰 城堡</td><td>castle</td><td>🏠 房子</td><td>house</td></tr>
<tr><td>🗼 塔</td><td>tower</td><td>🔺 金字塔</td><td>pyramid</td></tr>
<tr><td>🌉 桥</td><td>bridge</td><td>🌷 花园</td><td>garden</td></tr>
<tr><td>⛩️ 神殿</td><td>temple</td><td>🗿 雕像</td><td>statue</td></tr>
<tr><td>⛲ 喷泉</td><td>fountain</td><td>💡 灯塔</td><td>lighthouse</td></tr>
<tr><td>🧱 城墙</td><td>wall</td><td>🌳 树</td><td>tree</td></tr>
<tr><td>🚀 飞船</td><td>spaceship</td><td>🍄 蘑菇</td><td>mushroom</td></tr>
<tr><td>❤️ 爱心</td><td>heart</td><td>🔮 球体</td><td>sphere</td></tr>
<tr><td>🌀 螺旋塔</td><td>spiral</td><td>🏘️ 村庄</td><td>village</td></tr>
</table>
</div>
</div>

<!-- ===== AI 小镇 Tab ===== -->
<div id="tab-town" class="tab-panel">
<div class="card">
<label>🎭 选择 NPC 开始聊天 (直连 AI，无需打开游戏)</label>
<div class="npc-grid" id="npcGrid">加载中...</div>
<div class="chat-box" id="townChatHeader" style="min-height:auto; padding:8px 12px; font-weight:700;">👆 点击上方 NPC 卡片开始对话</div>
<div class="chat-box" id="townChatBox">对话内容将显示在这里...</div>

<!-- NPC 状态控件 -->
<div class="npc-controls">
<div class="npc-control-item">
<span>😊 心情</span>
<input type="range" id="npcMood" min="0" max="100" value="50">
<span id="npcMoodVal" style="color:var(--accent); font-weight:600; min-width:24px;">50</span>
</div>
<div class="npc-control-item">
<span>❤️ 好感</span>
<input type="range" id="npcRelation" min="0" max="100" value="50">
<span id="npcRelationVal" style="color:var(--accent); font-weight:600; min-width:24px;">50</span>
</div>
<div class="npc-control-item">
<span>🌤️ 天气</span>
<select id="npcWeather">
<option value="clear">☀️ 晴</option>
<option value="rain">🌧️ 雨</option>
<option value="fog">🌫️ 雾</option>
</select>
</div>
</div>

<div style="display:flex; gap:8px;">
<input type="text" id="townMsg" placeholder="输入消息，按 Enter 发送" onkeydown="townChatEnter(event)" style="flex:1; padding:10px; background:var(--bg-input); color:var(--text); border:1px solid var(--accent-dim); border-radius:6px; font-size:14px;">
<button class="btn-ai" onclick="townSend()">💬 发送</button>
</div>
</div>

<div class="card">
<label>📥 在游戏中体验完整 AI 小镇</label>
<div class="install-steps">
<p>1️⃣ 安装 <b>Luanti</b> (Minetest)：<code>brew install --cask luanti</code> 或从官网下载</p>
<p>2️⃣ 复制 mod 到游戏目录：</p>
<p style="margin-left:20px;">macOS: <code>cp -r ai_town ~/Library/Application\\ Support/minetest/mods/</code></p>
<p style="margin-left:20px;">Linux: <code>cp -r ai_town ~/.minetest/mods/</code></p>
<p style="margin-left:20px;">Windows: 复制到 <code>%APPDATA%\\minetest\\mods\\</code></p>
<p>3️⃣ 在游戏世界中启用 <code>ai_town</code> mod</p>
<p>4️⃣ 进入游戏输入 <code>/town</code> 生成小镇</p>
<p>5️⃣ 右键 NPC 开始对话</p>
<p style="margin-top:8px; color:var(--text-dim);">🕹️ 游戏内命令: /town 生成 | /ai_npc 状态 | /weather 天气 | /ai_mem &lt;npc&gt; 记忆</p>
</div>
</div>

<div class="card">
<label>📖 小镇日报 (AI 生成各 NPC 第一人称日记)</label>
<div class="btn-row" style="margin-bottom:10px;">
<button class="btn-ai btn-sm" onclick="loadTownDiary()">📝 生成今日日报</button>
<span id="diaryStatus" style="font-size:12px; color:var(--text-dim);">6 位 NPC × 1 篇日记 · 按日缓存</span>
</div>
<div class="npc-grid" id="diaryGrid"><div style="color:var(--text-dim); font-size:13px;">点击「生成今日日报」查看小镇的一天</div></div>
</div>

<div class="card">
<label>🕸️ NPC 关系图谱 (线越粗越亲密)</label>
<div class="preview-container">
<canvas id="relationCanvas" width="600" height="320" style="display:block; margin:0 auto; cursor:default;"></canvas>
</div>
<div class="btn-row" style="margin-top:8px;">
<button class="btn-parse btn-sm" onclick="renderRelations()">🔄 刷新图谱</button>
</div>
</div>

<div class="card">
<label>🎮 游戏内 NPC 特性</label>
<table>
<tr><th>系统</th><th>说明</th></tr>
<tr><td>🧠 记忆系统</td><td>每个NPC 20条记忆流，按 recency+importance+relevance 检索</td></tr>
<tr><td>💭 反思机制</td><td>每8轮对话 AI 自动总结，形成自我认知</td></tr>
<tr><td>💬 NPC自主对话</td><td>NPC相遇自动聊天，互相传播八卦</td></tr>
<tr><td>📅 每日计划</td><td>每天 AI 生成当日活动计划</td></tr>
<tr><td>😊 情绪系统</td><td>0-100情绪，影响对话语气</td></tr>
<tr><td>❤️ 好感度</td><td>陌生人→熟人→朋友→挚友</td></tr>
<tr><td>🛒 经济系统</td><td>金锭买卖物品</td></tr>
<tr><td>🌤️ 天气系统</td><td>晴/雨/雾，影响NPC心情</td></tr>
</table>
</div>
</div>

<script>
// ===== Toast 通知 =====
function showToast(msg, type) {
    type = type || 'ok';
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = 'toast ' + type;
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(function() {
        toast.classList.add('hide');
        setTimeout(function() { toast.remove(); }, 300);
    }, 3500);
}

function setStatus(msg, cls) {
    const s = document.getElementById('status');
    s.textContent = msg;
    s.className = 'status ' + (cls || 'status-ok');
    showToast(msg, cls === 'status-err' ? 'err' : (cls === 'status-warn' ? 'warn' : 'ok'));
}

// ===== 折叠面板 =====
function toggleCollapsible(headerId, bodyId) {
    var header = document.getElementById(headerId);
    var body = document.getElementById(bodyId);
    header.classList.toggle('open');
    body.classList.toggle('open');
}

// ===== 加载进度文案 =====
var loadingMessages = [
    '🤖 AI 正在构思建筑结构',
    '🤖 正在生成方块布局',
    '🤖 优化建筑细节中',
    '🤖 渲染屋顶和装饰',
    '🤖 最终调整中'
];
var loadingTimer = null;
function startLoading(msg) {
    var el = document.getElementById('aiLoading');
    var txt = document.getElementById('loadingText');
    el.classList.add('show');
    var idx = 0;
    txt.innerHTML = (msg || loadingMessages[0]) + '<span class="loading-dots"></span>';
    loadingTimer = setInterval(function() {
        idx = (idx + 1) % loadingMessages.length;
        txt.innerHTML = loadingMessages[idx] + '<span class="loading-dots"></span>';
    }, 2500);
}
function stopLoading() {
    document.getElementById('aiLoading').classList.remove('show');
    if (loadingTimer) { clearInterval(loadingTimer); loadingTimer = null; }
}

function setInput(text) { document.getElementById('input').value = text; }

function fetchAPI(action) {
    var input = document.getElementById('input').value;
    var url = '/api?action=' + action + '&input=' + encodeURIComponent(input);
    return fetch(url).then(function(r) { return r.json(); });
}
function doParse() {
    fetchAPI('parse').then(function(data) {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        var p = data.params;
        var sizes = ['小','中','大','巨大'];
        var text = '类型: ' + (p.type || '未知') + '\\n颜色: ' + (p.color || '默认') + '\\n尺寸: ' + sizes[p.size] + '\\n材质: ' + (p.material || '默认') + '\\n特征: ' + (p.features && p.features.length ? p.features.join(', ') : '无');
        document.getElementById('result').textContent = text;
        setStatus('✅ 解析完成', 'status-ok');
    });
}
function doGen() {
    fetchAPI('generate').then(function(data) {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        document.getElementById('code').textContent = data.lua;
        setStatus('✅ Lua 代码已生成', 'status-ok');
    });
}
function doInstall() {
    fetchAPI('install').then(function(data) {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        document.getElementById('code').textContent = data.lua;
        document.getElementById('pathInfo').textContent = '安装路径: ' + data.path;
        setStatus('✅ 已安装到 Luanti mods 目录！进入游戏输入 /build', 'status-ok');
    });
}
function doAll() {
    doParse();
    doInstall();
    doPreview();
}
function doLaunch() {
    setStatus('⏳ 正在启动 Luanti...', 'status-warn');
    fetch('/api?action=launch').then(function(r) { return r.json(); }).then(function(data) {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        setStatus('✅ Luanti 已启动！进入游戏后输入 /build', 'status-ok');
    }).catch(function() {
        setStatus('❌ 启动失败，请手动打开 Luanti', 'status-err');
    });
}
function doJoin() {
    var world = document.getElementById('worldSelect').value;
    var input = document.getElementById('input').value;
    setStatus('⏳ 正在安装 mod + 启用世界 + 启动游戏...', 'status-warn');
    var url = '/api?action=join&input=' + encodeURIComponent(input) + (world ? '&world=' + encodeURIComponent(world) : '');
    fetch(url).then(function(r) { return r.json(); }).then(function(data) {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        document.getElementById('code').textContent = data.lua || '';
        document.getElementById('pathInfo').textContent = 'Mod: ' + (data.mod_path||'') + ' | 世界: ' + (data.world_path||'');
        var lr = data.launch || {};
        if(lr.error) {
            setStatus('⚠️ Mod已安装但启动失败: ' + lr.error, 'status-warn');
        } else {
            setStatus('✅ 一键完成！游戏已启动，进入后输入 /build', 'status-ok');
        }
    }).catch(function() {
        setStatus('❌ 请求失败', 'status-err');
    });
}

// ===== AI 大模型 =====
function saveAIConfig() {
    localStorage.setItem('ai_api_key', document.getElementById('apiKey').value);
    localStorage.setItem('ai_base_url', document.getElementById('baseUrl').value);
    localStorage.setItem('ai_model', document.getElementById('modelName').value);
    localStorage.setItem('ai_provider', document.getElementById('aiProvider').value);
}
function switchProvider() {
    var p = document.getElementById('aiProvider').value;
    var configs = {
        'deepseek':      {url:'https://api.deepseek.com/v1', model:'deepseek-chat'},
        'zhipu':         {url:'https://open.bigmodel.cn/api/paas/v4', model:'glm-4-flash'},
        'qwen':          {url:'https://dashscope.aliyuncs.com/compatible-mode/v1', model:'qwen-turbo'},
        'moonshot':      {url:'https://api.moonshot.cn/v1', model:'moonshot-v1-8k'},
        'baichuan':      {url:'https://api.baichuan-ai.com/v1', model:'Baichuan4'},
        'minimax':       {url:'https://api.minimax.chat/v1', model:'abab6.5-chat'},
        'yi':            {url:'https://api.lingyiwanwu.com/v1', model:'yi-large'},
        'stepfun':       {url:'https://api.stepfun.com/v1', model:'step-1-8k'},
        'sensetime':     {url:'https://api.sensenova.cn/compatible-mode/v1', model:'SenseChat-5'},
        'iflytek':       {url:'https://spark-api-open.xf-yun.com/v1', model:'4.0Ultra'},
        'hunyuan':       {url:'https://api.hunyuan.cloud.tencent.com/v1', model:'hunyuan-pro'},
        'ernie':         {url:'https://qianfan.baidubce.com/v2', model:'ernie-4.0-8k-latest'},
        'volcengine':    {url:'https://ark.cn-beijing.volces.com/api/v3', model:'doubao-pro-4k'},
        'siliconflow':   {url:'https://api.siliconflow.cn/v1', model:'Qwen/Qwen2.5-7B-Instruct'},
        'openrouter_cn': {url:'https://openrouter.ai/api/v1', model:'deepseek/deepseek-chat'},
        'openai':        {url:'https://api.openai.com/v1', model:'gpt-4o-mini'},
        'anthropic':     {url:'https://api.anthropic.com/v1', model:'claude-3-5-haiku-20241022'},
        'google':        {url:'https://generativelanguage.googleapis.com/v1beta/openai', model:'gemini-1.5-flash'},
        'openrouter':    {url:'https://openrouter.ai/api/v1', model:'openai/gpt-4o-mini'},
        'groq':          {url:'https://api.groq.com/openai/v1', model:'llama-3.3-70b-versatile'},
        'together':      {url:'https://api.together.xyz/v1', model:'meta-llama/Llama-3.3-70B-Instruct-Turbo'},
        'mistral':       {url:'https://api.mistral.ai/v1', model:'mistral-small-latest'},
        'cohere':        {url:'https://api.cohere.ai/v1', model:'command-r-plus'},
        'perplexity':    {url:'https://api.perplexity.ai', model:'llama-3.1-8b-instruct'},
        'anyscale':      {url:'https://api.endpoints.anyscale.com/v1', model:'meta-llama/Llama-3.1-8B-Instruct'},
        'fireworks':     {url:'https://api.fireworks.ai/inference/v1', model:'accounts/fireworks/models/llama-v3p1-8b-instruct'},
        'lepton':        {url:'https://llama3-1-8b.lepton.run/api/v1', model:'llama3.1-8b'},
        'novita':        {url:'https://api.novita.ai/v3/openai', model:'meta-llama/llama-3.1-8b-instruct'},
        'ollama':        {url:'http://localhost:11434/v1', model:'llama3.2'},
        'lmstudio':      {url:'http://localhost:1234/v1', model:'local-model'},
        'custom':        {url:'', model:''},
    };
    var c = configs[p];
    if (c) {
        document.getElementById('baseUrl').value = c.url;
        document.getElementById('modelName').value = c.model;
        saveAIConfig();
    }
}
function loadAIConfig() {
    document.getElementById('apiKey').value = localStorage.getItem('ai_api_key') || '';
    document.getElementById('baseUrl').value = localStorage.getItem('ai_base_url') || 'https://api.deepseek.com/v1';
    document.getElementById('modelName').value = localStorage.getItem('ai_model') || 'deepseek-chat';
    document.getElementById('aiProvider').value = localStorage.getItem('ai_provider') || 'deepseek';
}
function getAIUrl(action) {
    var input = document.getElementById('input').value;
    var key = encodeURIComponent(document.getElementById('apiKey').value);
    var url_val = encodeURIComponent(document.getElementById('baseUrl').value);
    var model = encodeURIComponent(document.getElementById('modelName').value);
    var world = document.getElementById('worldSelect').value;
    var url = '/api?action=' + action + '&input=' + encodeURIComponent(input) +
              '&api_key=' + key + '&base_url=' + url_val + '&model=' + model;
    if (world) url += '&world=' + encodeURIComponent(world);
    return url;
}

// ===== 生成历史 =====
function loadHistory() {
    var hist = JSON.parse(localStorage.getItem('lb_history') || '[]');
    var container = document.getElementById('historyList');
    if (!container) return;
    container.innerHTML = '';
    hist.slice(0, 10).forEach(function(item) {
        var btn = document.createElement('div');
        btn.className = 'history-item';
        btn.innerHTML = '<span class="history-time">' + item.time + '</span> <span class="history-text">' + item.input.substring(0,40) + '</span> <span class="history-count">' + (item.count||0) + ' blocks</span>';
        btn.onclick = function() {
            document.getElementById('input').value = item.input;
            if (item.blocks) { previewBlocks = item.blocks; renderPreview(); }
        };
        container.appendChild(btn);
    });
}
function saveHistory(input, blocks, count) {
    var hist = JSON.parse(localStorage.getItem('lb_history') || '[]');
    hist.unshift({time: new Date().toLocaleTimeString(), input: input, blocks: blocks, count: count});
    if (hist.length > 20) hist.pop();
    localStorage.setItem('lb_history', JSON.stringify(hist));
    loadHistory();
}
function doAIPreview() {
    var key = document.getElementById('apiKey').value;
    if (!key) { setStatus('⚠️ 请先填写 API Key', 'status-warn'); return; }
    startLoading('🤖 AI 正在生成建筑');
    setStatus('🤖 AI 正在生成... (通常 10-30 秒)', 'status-warn');
    fetch(getAIUrl('ai_preview')).then(function(r) { return r.json(); }).then(function(data) {
        stopLoading();
        if(data.error) {
            setStatus(data.error, 'status-err');
            if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; }
            return;
        }
        previewBlocks = data.blocks || [];
        lastCmds = data.cmds || lastCmds;
        setRefineEnabled();
        renderPreview();
        saveHistory(document.getElementById('input').value, previewBlocks, data.count||0);
        setStatus('✅ AI 预览已生成 (' + (data.count||0) + ' 个方块)', 'status-ok');
    }).catch(function() {
        stopLoading();
        setStatus('❌ AI 请求失败，请检查网络和 API Key', 'status-err');
    });
}
function doAIGenerate() {
    var key = document.getElementById('apiKey').value;
    if (!key) { setStatus('⚠️ 请先填写 API Key', 'status-warn'); return; }
    startLoading('🤖 AI 生成 + 安装 + 启动');
    setStatus('🤖 AI 生成中 + 安装 + 启动游戏...', 'status-warn');
    fetch(getAIUrl('ai_install')).then(function(r) { return r.json(); }).then(function(data) {
        stopLoading();
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        document.getElementById('code').textContent = data.lua || '';
        previewBlocks = data.blocks || [];
        lastCmds = data.cmds || lastCmds;
        setRefineEnabled();
        renderPreview();
        document.getElementById('pathInfo').textContent = 'Mod: ' + (data.mod_path||'') + ' | 方块: ' + (data.count||0);
        var lr = data.launch || {};
        if(lr.error) {
            setStatus('⚠️ Mod已安装但启动失败: ' + lr.error, 'status-warn');
        } else {
            setStatus('✅ AI 建筑已生成并安装！(' + (data.count||0) + ' 方块) 进入游戏输入 /build', 'status-ok');
        }
    }).catch(function() {
        stopLoading();
        setStatus('❌ AI 请求失败', 'status-err');
    });
}

// ===== 对话式迭代建造 =====
var chatHistory = [];
var chatCmds = null;
function loadChatState() {
    try {
        chatHistory = JSON.parse(localStorage.getItem('lb_chat_history') || '[]');
        chatCmds = JSON.parse(localStorage.getItem('lb_chat_cmds') || 'null');
    } catch (e) { chatHistory = []; chatCmds = null; }
    chatHistory.forEach(function(m) { appendChatBubble(m.role, m.content); });
}
function saveChatState() {
    localStorage.setItem('lb_chat_history', JSON.stringify(chatHistory));
    localStorage.setItem('lb_chat_cmds', JSON.stringify(chatCmds));
}
function appendChatBubble(role, text) {
    var box = document.getElementById('chatBox');
    var div = document.createElement('div');
    div.style.marginBottom = '6px';
    div.style.padding = '6px 8px';
    div.style.borderRadius = '6px';
    if (role === 'user') {
        div.style.background = '#0f3460'; div.style.color = '#e0e0e0';
        div.style.marginLeft = '40px'; div.style.textAlign = 'right';
    } else {
        div.style.background = '#1a1a2e'; div.style.color = '#50fa7b';
        div.style.marginRight = '40px';
    }
    div.textContent = text;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}
function resetChat() {
    chatHistory = []; chatCmds = null;
    localStorage.removeItem('lb_chat_history');
    localStorage.removeItem('lb_chat_cmds');
    document.getElementById('chatBox').innerHTML = '<div style="color:var(--text-dim);">已清空。描述一个新建筑开始吧。</div>';
}
function sendChat(withInstall) {
    var key = document.getElementById('apiKey').value;
    if (!key) { setStatus('⚠️ 请先填写 API Key', 'status-warn'); return; }
    var inputEl = document.getElementById('chatInput');
    var msg = inputEl.value.trim();
    if (!msg) return;
    inputEl.value = '';
    appendChatBubble('user', msg);
    chatHistory.push({role: 'user', content: msg});
    startLoading(chatCmds ? '🤖 AI 正在修改建筑' : '🤖 AI 正在生成建筑');
    setStatus('🤖 AI 正在' + (chatCmds ? '修改建筑' : '生成建筑') + '...', 'status-warn');
    var url = '/api?action=ai_chat' +
        '&input=' + encodeURIComponent(msg) +
        '&api_key=' + encodeURIComponent(key) +
        '&base_url=' + encodeURIComponent(document.getElementById('baseUrl').value) +
        '&model=' + encodeURIComponent(document.getElementById('modelName').value) +
        '&history=' + encodeURIComponent(JSON.stringify(chatHistory.slice(0, -1))) +
        '&cmds=' + encodeURIComponent(JSON.stringify(chatCmds || [])) +
        (withInstall ? '&install=1' : '');
    var worldEl = document.getElementById('worldSelect');
    if (worldEl && worldEl.value) url += '&world=' + encodeURIComponent(worldEl.value);
    fetch(url).then(function(r) { return r.json(); }).then(function(data) {
        stopLoading();
        if (data.error) {
            appendChatBubble('assistant', '❌ ' + data.error);
            chatHistory.push({role: 'assistant', content: data.error});
            setStatus(data.error, 'status-err');
            return;
        }
        var reply = '✅ 已生成 ' + (data.count || 0) + ' 方块的建筑' + (withInstall ? ' 并安装启动' : '');
        appendChatBubble('assistant', reply);
        chatHistory.push({role: 'assistant', content: reply});
        chatCmds = data.cmds || null;
        saveChatState();
        previewBlocks = data.blocks || [];
        lastCmds = data.cmds || lastCmds;
        setRefineEnabled();
        renderPreview();
        if (data.lua) document.getElementById('code').textContent = data.lua;
        if (withInstall) {
            document.getElementById('pathInfo').textContent = 'Mod: ' + (data.mod_path || '');
            setStatus('✅ 修改已安装！进入游戏输入 /build', 'status-ok');
        } else {
            setStatus('✅ 对话式生成完成 (' + (data.count || 0) + ' 方块)', 'status-ok');
        }
    }).catch(function() {
        stopLoading();
        appendChatBubble('assistant', '❌ 请求失败，请检查网络');
        setStatus('❌ AI 请求失败', 'status-err');
    });
}

// ===== 语音输入 =====
var voiceRec = null;
var voiceTarget = null;
function toggleVoice(inputId, callback) {
    if (voiceRec) { voiceRec.stop(); return; }
    var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    var statusEl = document.getElementById('micStatus');
    if (!SR) {
        if (statusEl) statusEl.textContent = '当前浏览器不支持语音识别 (建议 Chrome/Edge/Safari)';
        setStatus('⚠️ 浏览器不支持语音识别', 'status-warn');
        return;
    }
    voiceRec = new SR();
    voiceRec.lang = 'zh-CN';
    voiceRec.interimResults = false;
    voiceRec.maxAlternatives = 1;
    voiceTarget = {inputId: inputId, callback: callback};
    document.getElementById('micBtn').textContent = '🔴 听着呢...再说一句点击结束';
    if (inputId === 'chatInput') document.getElementById('chatMicBtn').textContent = '🔴';
    if (statusEl) statusEl.textContent = '请说话...';
    voiceRec.onresult = function(e) {
        var text = e.results[0][0].transcript;
        document.getElementById(voiceTarget.inputId).value = text;
        if (statusEl) statusEl.textContent = '识别: ' + text;
        if (voiceTarget.callback) voiceTarget.callback();
    };
    voiceRec.onerror = function(e) {
        if (statusEl) statusEl.textContent = '语音识别失败: ' + e.error;
    };
    voiceRec.onend = function() {
        voiceRec = null;
        document.getElementById('micBtn').textContent = '🎤 语音输入';
        document.getElementById('chatMicBtn').textContent = '🎤';
        if (statusEl && statusEl.textContent.indexOf('识别:') !== 0) statusEl.textContent = '点击开始说话 (浏览器语音识别)';
    };
    voiceRec.start();
}

// ===== 3D 预览 (立方体三面渲染) =====
var previewBlocks = [];
var previewState = { angleX: -0.5, angleY: 0.5, zoom: 1.0, dragging: false, lastX: 0, lastY: 0 };

function doPreview() {
    fetchAPI('preview').then(function(data) {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        previewBlocks = data.blocks || [];
        lastCmds = null;   // 关键词模式无 cmds，审美迭代不可用
        setRefineEnabled();
        renderPreview();
        setStatus('✅ 3D 预览已生成 (' + previewBlocks.length + ' 个方块)', 'status-ok');
    });
}

function zoomPreview(factor) {
    previewState.zoom *= factor;
    previewState.zoom = Math.max(0.3, Math.min(3.0, previewState.zoom));
    renderPreview();
}
function resetPreview() {
    previewState = { angleX: -0.5, angleY: 0.5, zoom: 1.0, dragging: false, lastX: 0, lastY: 0 };
    renderPreview();
}

function hexShade(hex, factor) {
    // 调整颜色亮度: factor>1 变亮, factor<1 变暗
    hex = hex.replace('#', '');
    var r = parseInt(hex.substr(0,2), 16);
    var g = parseInt(hex.substr(2,2), 16);
    var b = parseInt(hex.substr(4,2), 16);
    r = Math.min(255, Math.max(0, Math.round(r * factor)));
    g = Math.min(255, Math.max(0, Math.round(g * factor)));
    b = Math.min(255, Math.max(0, Math.round(b * factor)));
    return 'rgb(' + r + ',' + g + ',' + b + ')';
}

function renderPreview() {
    var canvas = document.getElementById('previewCanvas');
    var ctx = canvas.getContext('2d');
    var w = canvas.width, h = canvas.height;

    // 背景渐变
    var grad = ctx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, '#0d1117');
    grad.addColorStop(1, '#0a0a1a');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    if (previewBlocks.length === 0) {
        ctx.fillStyle = '#6272a4';
        ctx.font = '14px -apple-system,sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('点击「👁️ 预览」或「🤖 AI 预览」查看 3D 效果', w/2, h/2);
        document.getElementById('previewInfo').textContent = '';
        return;
    }

    var minX=Infinity, maxX=-Infinity, minY=Infinity, maxY=-Infinity, minZ=Infinity, maxZ=-Infinity;
    for (var i = 0; i < previewBlocks.length; i++) {
        var b = previewBlocks[i];
        minX = Math.min(minX, b.x); maxX = Math.max(maxX, b.x);
        minY = Math.min(minY, b.y); maxY = Math.max(maxY, b.y);
        minZ = Math.min(minZ, b.z); maxZ = Math.max(maxZ, b.z);
    }
    var cx = (minX + maxX) / 2;
    var cy = (minY + maxY) / 2;
    var cz = (minZ + maxZ) / 2;
    var range = Math.max(maxX-minX, maxY-minY, maxZ-minZ) + 2;
    var scale = Math.min(w, h) / range * 0.7 * previewState.zoom;

    function project(x, y, z) {
        var dx = (x - cx) * scale;
        var dy = (y - cy) * scale;
        var dz = (z - cz) * scale;
        var cosY = Math.cos(previewState.angleY);
        var sinY = Math.sin(previewState.angleY);
        var rx = dx * cosY - dz * sinY;
        var rz = dx * sinY + dz * cosY;
        var cosX = Math.cos(previewState.angleX);
        var sinX = Math.sin(previewState.angleX);
        var ry = dy * cosX - rz * sinX;
        var rz2 = dy * sinX + rz * cosX;
        return { sx: w/2 + rx, sy: h/2 + ry, depth: rz2 };
    }

    // 地面网格
    ctx.strokeStyle = '#1a2040';
    ctx.lineWidth = 1;
    var gridSize = Math.max(maxX-minX, maxZ-minZ) + 4;
    var gx0 = (minX + maxX) / 2 - gridSize/2;
    var gz0 = (minZ + maxZ) / 2 - gridSize/2;
    for (var gi = 0; gi <= gridSize; gi += 2) {
        var p1 = project(gx0 + gi, minY - 0.5, gz0);
        var p2 = project(gx0 + gi, minY - 0.5, gz0 + gridSize);
        ctx.beginPath(); ctx.moveTo(p1.sx, p1.sy); ctx.lineTo(p2.sx, p2.sy); ctx.stroke();
        var p3 = project(gx0, minY - 0.5, gz0 + gi);
        var p4 = project(gx0 + gridSize, minY - 0.5, gz0 + gi);
        ctx.beginPath(); ctx.moveTo(p3.sx, p3.sy); ctx.lineTo(p4.sx, p4.sy); ctx.stroke();
    }

    // 投影所有方块，按深度排序
    var projected = [];
    for (var i = 0; i < previewBlocks.length; i++) {
        var b = previewBlocks[i];
        var p = project(b.x, b.y, b.z);
        projected.push({ x: b.x, y: b.y, z: b.z, color: b.color || '#888888', sx: p.sx, sy: p.sy, depth: p.depth });
    }
    projected.sort(function(a, b) { return a.depth - b.depth; });

    // 画 3D 立方体 (三面)
    var halfBlock = Math.max(2, scale * 0.45);
    for (var i = 0; i < projected.length; i++) {
        var b = projected[i];
        var color = b.color;
        var sx = b.sx, sy = b.sy;

        // 计算三个面的四个角 (基于旋转角度)
        // 顶面、左面、右面
        var cosY = Math.cos(previewState.angleY);
        var sinY = Math.sin(previewState.angleY);
        var cosX = Math.cos(previewState.angleX);
        var sinX = Math.sin(previewState.angleX);

        // 顶面四个角 (y-1 的正方形)
        var topCorners = [
            project(b.x - 0.5, b.y + 0.5, b.z - 0.5),
            project(b.x + 0.5, b.y + 0.5, b.z - 0.5),
            project(b.x + 0.5, b.y + 0.5, b.z + 0.5),
            project(b.x - 0.5, b.y + 0.5, b.z + 0.5)
        ];
        // 底面四个角
        var botCorners = [
            project(b.x - 0.5, b.y - 0.5, b.z - 0.5),
            project(b.x + 0.5, b.y - 0.5, b.z - 0.5),
            project(b.x + 0.5, b.y - 0.5, b.z + 0.5),
            project(b.x - 0.5, b.y - 0.5, b.z + 0.5)
        ];

        // 顶面 (最亮)
        ctx.fillStyle = hexShade(color, 1.3);
        ctx.beginPath();
        ctx.moveTo(topCorners[0].sx, topCorners[0].sy);
        ctx.lineTo(topCorners[1].sx, topCorners[1].sy);
        ctx.lineTo(topCorners[2].sx, topCorners[2].sy);
        ctx.lineTo(topCorners[3].sx, topCorners[3].sy);
        ctx.closePath();
        ctx.fill();

        // 判断哪些侧面可见 (基于旋转角度)
        // 当 sinY > 0 时右侧面 (z+0.5) 可见
        // 当 sinY < 0 时左侧面 (z-0.5) 可见
        // 当 cosY > 0 时前面 (x+0.5) 可见
        // 当 cosY < 0 时后面 (x-0.5) 可见
        // 简化: 总是画两个侧面，根据角度选择

        // 右侧面 (z+ 方向, 较暗)
        if (sinY > 0) {
            ctx.fillStyle = hexShade(color, 0.7);
            ctx.beginPath();
            ctx.moveTo(topCorners[2].sx, topCorners[2].sy);
            ctx.lineTo(topCorners[3].sx, topCorners[3].sy);
            ctx.lineTo(botCorners[3].sx, botCorners[3].sy);
            ctx.lineTo(botCorners[2].sx, botCorners[2].sy);
            ctx.closePath();
            ctx.fill();
        }

        // 左侧面 (z- 方向, 中等)
        if (sinY < 0) {
            ctx.fillStyle = hexShade(color, 0.85);
            ctx.beginPath();
            ctx.moveTo(topCorners[0].sx, topCorners[0].sy);
            ctx.lineTo(topCorners[1].sx, topCorners[1].sy);
            ctx.lineTo(botCorners[1].sx, botCorners[1].sy);
            ctx.lineTo(botCorners[0].sx, botCorners[0].sy);
            ctx.closePath();
            ctx.fill();
        }

        // 前/后面 (x 方向)
        if (cosY > 0) {
            // x+ 面
            ctx.fillStyle = hexShade(color, 0.8);
            ctx.beginPath();
            ctx.moveTo(topCorners[1].sx, topCorners[1].sy);
            ctx.lineTo(topCorners[2].sx, topCorners[2].sy);
            ctx.lineTo(botCorners[2].sx, botCorners[2].sy);
            ctx.lineTo(botCorners[1].sx, botCorners[1].sy);
            ctx.closePath();
            ctx.fill();
        } else {
            // x- 面
            ctx.fillStyle = hexShade(color, 0.8);
            ctx.beginPath();
            ctx.moveTo(topCorners[3].sx, topCorners[3].sy);
            ctx.lineTo(topCorners[0].sx, topCorners[0].sy);
            ctx.lineTo(botCorners[0].sx, botCorners[0].sy);
            ctx.lineTo(botCorners[3].sx, botCorners[3].sy);
            ctx.closePath();
            ctx.fill();
        }

        // 边框
        ctx.strokeStyle = 'rgba(255,255,255,0.1)';
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        ctx.moveTo(topCorners[0].sx, topCorners[0].sy);
        ctx.lineTo(topCorners[1].sx, topCorners[1].sy);
        ctx.lineTo(topCorners[2].sx, topCorners[2].sy);
        ctx.lineTo(topCorners[3].sx, topCorners[3].sy);
        ctx.closePath();
        ctx.stroke();
    }

    // 信息栏
    var infoEl = document.getElementById('previewInfo');
    if (infoEl) {
        infoEl.textContent = previewBlocks.length + ' blocks · ' + Math.round(previewState.zoom * 100) + '%';
    }
}

// ===== 蓝图分享 (导出/导入/分享链接/本地蓝图库) =====
var lastCmds = null;   // AI 生成的 cmds (关键词模式为 null)

function setRefineEnabled() {
    var btn = document.getElementById('refineBtn');
    if (btn) btn.disabled = !(lastCmds && lastCmds.length > 0 && previewBlocks.length > 0);
}

// ===== AI 审美迭代 (多模态自评循环) =====
var refining = false;
function refineLoop() {
    if (refining) return;
    if (!lastCmds || lastCmds.length === 0) { showToast('请先用 AI 生成建筑', 'warn'); return; }
    var key = document.getElementById('apiKey').value;
    if (!key) { setStatus('⚠️ 请先填写 API Key', 'status-warn'); return; }
    var rounds = parseInt(document.getElementById('refineRounds').value, 10) || 1;
    refining = true;
    var btn = document.getElementById('refineBtn');
    btn.disabled = true;

    function round(i) {
        if (i > rounds) {
            refining = false;
            setRefineEnabled();
            setStatus('✅ 审美迭代完成 (' + rounds + ' 轮)，建筑已达 ' + previewBlocks.length + ' 方块', 'status-ok');
            saveHistory(document.getElementById('input').value, previewBlocks, previewBlocks.length);
            return;
        }
        startLoading('🎨 第 ' + i + '/' + rounds + ' 轮审美迭代');
        setStatus('🎨 第 ' + i + ' 轮: AI 正在审视自己的作品...', 'status-warn');
        var img = '';
        try { img = document.getElementById('previewCanvas').toDataURL('image/png'); } catch (e) { img = ''; }
        var url = '/api?action=ai_refine' +
            '&input=' + encodeURIComponent(document.getElementById('input').value) +
            '&api_key=' + encodeURIComponent(key) +
            '&base_url=' + encodeURIComponent(document.getElementById('baseUrl').value) +
            '&model=' + encodeURIComponent(document.getElementById('modelName').value) +
            '&cmds=' + encodeURIComponent(JSON.stringify(lastCmds)) +
            '&image=' + encodeURIComponent(img);
        fetch(url).then(function(r) { return r.json(); }).then(function(data) {
            stopLoading();
            if (data.error) {
                refining = false;
                setRefineEnabled();
                setStatus('❌ ' + data.error, 'status-err');
                return;
            }
            var before = previewBlocks.length;
            lastCmds = data.cmds || lastCmds;
            previewBlocks = data.blocks || [];
            renderPreview();
            if (data.lua) document.getElementById('code').textContent = data.lua;
            showToast('✅ 第 ' + i + ' 轮: ' + before + ' → ' + (data.count||0) + ' 方块 (' + (data.mode==='vision'?'视觉评审':'文本评审') + ')');
            setTimeout(function() { round(i + 1); }, 400);
        }).catch(function() {
            stopLoading();
            refining = false;
            setRefineEnabled();
            setStatus('❌ 审美迭代请求失败', 'status-err');
        });
    }
    round(1);
}

function _bpSlug(text) {
    var t = (text || 'building').replace(/\\s+/g, '_');
    return t.length > 20 ? t.substring(0, 20) : t;
}
function _bpPayload() {
    if (!previewBlocks || previewBlocks.length === 0) return null;
    return {
        v: 1,
        input: document.getElementById('input').value,
        cmds: lastCmds,
        blocks: previewBlocks,
        count: previewBlocks.length,
        time: new Date().toISOString()
    };
}
function exportBlueprint() {
    var data = _bpPayload();
    if (!data) { showToast('请先生成预览再导出', 'warn'); return; }
    var blob = new Blob([JSON.stringify(data)], {type: 'application/json'});
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'blocktown_' + _bpSlug(data.input) + '.json';
    a.click();
    URL.revokeObjectURL(a.href);
    showToast('✅ 蓝图已导出 (' + data.count + ' 方块)');
}
function copyShareLink() {
    var data = _bpPayload();
    if (!data) { showToast('请先生成预览', 'warn'); return; }
    // 优先只带 cmds (可重建且小); 无 cmds 时带 blocks
    var compact = {i: data.input};
    if (data.cmds) { compact.c = data.cmds; } else { compact.b = data.blocks; }
    var b64 = btoa(unescape(encodeURIComponent(JSON.stringify(compact))));
    var url = location.origin + '/#bp=' + b64;
    if (url.length > 8000) { showToast('⚠️ 蓝图太大，建议用导出文件分享', 'warn'); return; }
    navigator.clipboard.writeText(url).then(function() {
        showToast('✅ 分享链接已复制');
    }, function() {
        prompt('复制此链接:', url);
    });
}
function importBlueprint() {
    var raw = prompt('粘贴蓝图 JSON 或分享链接末尾的 #bp=... 内容:');
    if (!raw) return;
    try {
        if (raw.indexOf('#bp=') >= 0) raw = raw.split('#bp=')[1];
        raw = raw.trim();
        var obj;
        try { obj = JSON.parse(raw); }
        catch (e) { obj = JSON.parse(decodeURIComponent(escape(atob(raw)))); }
        applyBlueprint(obj);
    } catch (e) {
        showToast('❌ 蓝图解析失败: ' + e.message, 'err');
    }
}
function applyBlueprint(obj) {
    var input = obj.i || obj.input || '';
    var cmds = obj.c || obj.cmds || null;
    var blocks = obj.b || obj.blocks || null;
    document.getElementById('input').value = input;
    if (cmds) {
        // 有 cmds: 走服务端 expand 重建 (保证与生成一致)
        setStatus('⏳ 正在重建蓝图...', 'status-warn');
        fetch('/api?action=expand&input=' + encodeURIComponent(input) +
              '&cmds=' + encodeURIComponent(JSON.stringify(cmds)))
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.error) { setStatus(data.error, 'status-err'); return; }
                lastCmds = data.cmds || cmds;
                previewBlocks = data.blocks || [];
                setRefineEnabled();
                renderPreview();
                if (data.lua) document.getElementById('code').textContent = data.lua;
                setStatus('✅ 蓝图已导入 (' + (data.count||0) + ' 方块)，可继续编辑或安装', 'status-ok');
            }).catch(function() { setStatus('❌ 蓝图重建请求失败', 'status-err'); });
    } else if (blocks) {
        lastCmds = null;
        previewBlocks = blocks;
        renderPreview();
        setStatus('✅ 蓝图已导入 (' + blocks.length + ' 方块)', 'status-ok');
    } else {
        showToast('❌ 蓝图缺少方块数据', 'err');
    }
}
function handleBpFile(e) {
    var f = e.target.files[0];
    if (!f) return;
    var reader = new FileReader();
    reader.onload = function(ev) {
        try { applyBlueprint(JSON.parse(ev.target.result)); }
        catch (err) { showToast('❌ 文件不是有效蓝图', 'err'); }
    };
    reader.readAsText(f);
    e.target.value = '';
}
// 本地蓝图库
function loadBpList() {
    var list = JSON.parse(localStorage.getItem('lb_blueprints') || '[]');
    var el = document.getElementById('bpList');
    if (!el) return;
    el.innerHTML = '';
    if (list.length === 0) {
        el.innerHTML = '<div style="color:var(--text-dim); font-size:13px; padding:6px;">还没有保存的蓝图。生成建筑后点「保存当前建筑」。</div>';
        return;
    }
    list.forEach(function(bp, idx) {
        var item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = '<span class="history-time">' + (bp.date||'') + '</span>' +
            '<span class="history-text">' + bp.name + '</span>' +
            '<span class="history-count">' + (bp.count||0) + ' blocks</span>';
        item.onclick = function() { applyBlueprint(bp.data); };
        var del = document.createElement('span');
        del.textContent = ' ✕';
        del.style.color = '#ff5555';
        del.style.cursor = 'pointer';
        del.onclick = function(ev) {
            ev.stopPropagation();
            list.splice(idx, 1);
            localStorage.setItem('lb_blueprints', JSON.stringify(list));
            loadBpList();
        };
        item.appendChild(del);
        el.appendChild(item);
    });
}
function saveBlueprintDialog() {
    var data = _bpPayload();
    if (!data) { showToast('请先生成预览', 'warn'); return; }
    var name = prompt('蓝图名称:', data.input || '我的建筑');
    if (!name) return;
    var list = JSON.parse(localStorage.getItem('lb_blueprints') || '[]');
    list.unshift({name: name, date: new Date().toLocaleDateString(), count: data.count, data: data});
    if (list.length > 30) list.pop();
    localStorage.setItem('lb_blueprints', JSON.stringify(list));
    loadBpList();
    showToast('✅ 已保存到蓝图库');
}

// 拖拽 + 滚轮缩放
document.addEventListener('DOMContentLoaded', function() {
    var canvas = document.getElementById('previewCanvas');
    canvas.addEventListener('mousedown', function(e) {
        previewState.dragging = true;
        previewState.lastX = e.clientX;
        previewState.lastY = e.clientY;
    });
    document.addEventListener('mousemove', function(e) {
        if (!previewState.dragging) return;
        var dx = e.clientX - previewState.lastX;
        var dy = e.clientY - previewState.lastY;
        previewState.angleY += dx * 0.01;
        previewState.angleX += dy * 0.01;
        previewState.angleX = Math.max(-1.5, Math.min(1.5, previewState.angleX));
        previewState.lastX = e.clientX;
        previewState.lastY = e.clientY;
        renderPreview();
    });
    document.addEventListener('mouseup', function() { previewState.dragging = false; });
    // 触摸
    canvas.addEventListener('touchstart', function(e) {
        e.preventDefault();
        var t = e.touches[0];
        previewState.dragging = true;
        previewState.lastX = t.clientX;
        previewState.lastY = t.clientY;
    });
    canvas.addEventListener('touchmove', function(e) {
        e.preventDefault();
        if (!previewState.dragging) return;
        var t = e.touches[0];
        var dx = t.clientX - previewState.lastX;
        var dy = t.clientY - previewState.lastY;
        previewState.angleY += dx * 0.01;
        previewState.angleX += dy * 0.01;
        previewState.angleX = Math.max(-1.5, Math.min(1.5, previewState.angleX));
        previewState.lastX = t.clientX;
        previewState.lastY = t.clientY;
        renderPreview();
    });
    canvas.addEventListener('touchend', function() { previewState.dragging = false; });
    // 滚轮缩放
    canvas.addEventListener('wheel', function(e) {
        e.preventDefault();
        zoomPreview(e.deltaY < 0 ? 1.1 : 0.9);
    }, { passive: false });
    // 初始空预览
    renderPreview();
});

// 初始化
fetch('/api?action=info').then(function(r) { return r.json(); }).then(function(data) {
    document.getElementById('pathInfo').textContent = 'Mod 目录: ' + data.mods_dir;
    if(data.exists) setStatus('✅ Luanti 目录就绪', 'status-ok');
    else setStatus('⚠️ Luanti 目录不存在，可能需要手动设置', 'status-warn');
});
fetch('/api?action=worlds').then(function(r) { return r.json(); }).then(function(data) {
    var sel = document.getElementById('worldSelect');
    (data.worlds || []).forEach(function(w) {
        var opt = document.createElement('option');
        opt.value = w.dir;
        opt.textContent = w.name;
        sel.appendChild(opt);
    });
});
loadAIConfig();
loadHistory();
loadChatState();
loadBpList();
// 分享链接导入: #bp=<base64>
(function() {
    var h = location.hash || '';
    if (h.indexOf('#bp=') === 0) {
        try {
            var obj = JSON.parse(decodeURIComponent(escape(atob(h.substring(4)))));
            setTimeout(function() { applyBlueprint(obj); }, 300);
        } catch (e) { showToast('分享链接解析失败', 'err'); }
    }
})();
document.getElementById('input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        doPreview();
    }
});
document.getElementById('input').focus();

// NPC mood/relation slider live update
document.getElementById('npcMood').addEventListener('input', function() {
    document.getElementById('npcMoodVal').textContent = this.value;
});
document.getElementById('npcRelation').addEventListener('input', function() {
    document.getElementById('npcRelationVal').textContent = this.value;
});

// ===== AI 小镇 Tab =====
function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(function(b) {
        b.classList.toggle('active', b.dataset.tab === tab);
    });
    document.querySelectorAll('.tab-panel').forEach(function(p) {
        p.classList.toggle('active', p.id === 'tab-' + tab);
    });
    if (tab === 'town') { loadTownNpcs(); renderRelations(); }
}

var townNpcs = [];
var selectedNpc = null;
var townChatHistory = {};

function loadTownNpcs() {
    fetch('/api?action=town_npcs').then(function(r) { return r.json(); }).then(function(data) {
        townNpcs = data.npcs || [];
        var grid = document.getElementById('npcGrid');
        grid.innerHTML = '';
        townNpcs.forEach(function(npc) {
            var card = document.createElement('div');
            card.className = 'npc-card';
            card.style.borderColor = npc.color;
            card.innerHTML = '<div class="npc-emoji">' + npc.emoji + '</div>' +
                '<div class="npc-name" style="color:' + npc.color + '">' + npc.display + '</div>' +
                '<div class="npc-role">' + npc.role + '</div>' +
                '<div class="npc-loc">📍 ' + npc.location + '</div>' +
                '<div class="npc-quest">📋 ' + npc.quest + '</div>';
            card.onclick = function() { selectNpc(npc.name); };
            grid.appendChild(card);
        });
    });
}

function selectNpc(name) {
    selectedNpc = name;
    townChatHistory[name] = townChatHistory[name] || [];
    document.querySelectorAll('.npc-card').forEach(function(c) {
        c.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
    var npc = townNpcs.find(function(n) { return n.name === name; });
    if (npc) {
        document.getElementById('townChatHeader').innerHTML =
            '正在和 ' + npc.emoji + ' <span style="color:' + npc.color + '">' + npc.display + '</span> 聊天';
        document.getElementById('townChatBox').innerHTML = '';
    }
    document.getElementById('townMsg').focus();
}

function townSend() {
    if (!selectedNpc) { showToast('请先选择一个 NPC', 'warn'); return; }
    var msg = document.getElementById('townMsg').value.trim();
    if (!msg) return;
    var box = document.getElementById('townChatBox');
    var npc = townNpcs.find(function(n) { return n.name === selectedNpc; });
    var emoji = npc ? npc.emoji : '🎭';

    // 用户消息
    var userDiv = document.createElement('div');
    userDiv.className = 'chat-msg chat-user';
    userDiv.textContent = '🧑 ' + msg;
    box.appendChild(userDiv);

    document.getElementById('townMsg').value = '';

    // 打字指示器
    var typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
    box.appendChild(typingDiv);
    box.scrollTop = box.scrollHeight;

    var mood = document.getElementById('npcMood').value;
    var relation = document.getElementById('npcRelation').value;
    var weather = document.getElementById('npcWeather').value;
    var hist = townChatHistory[selectedNpc] || [];
    var url = '/api?action=town_chat&npc=' + encodeURIComponent(selectedNpc) +
        '&input=' + encodeURIComponent(msg) +
        '&mood=' + mood + '&relation=' + relation + '&weather=' + weather +
        '&history=' + encodeURIComponent(JSON.stringify(hist));

    fetch(url).then(function(r) { return r.json(); }).then(function(data) {
        document.getElementById('typingIndicator').remove();
        if (data.error) {
            var errDiv = document.createElement('div');
            errDiv.className = 'chat-msg chat-npc';
            errDiv.innerHTML = '⚠️ ' + data.error;
            box.appendChild(errDiv);
        } else {
            var npcDiv = document.createElement('div');
            npcDiv.className = 'chat-msg chat-npc';
            npcDiv.innerHTML = '<span class="npc-avatar">' + emoji + '</span> ' + data.reply;
            box.appendChild(npcDiv);
            townChatHistory[selectedNpc].push({role:'user', content:msg});
            townChatHistory[selectedNpc].push({role:'assistant', content:data.reply});
        }
        box.scrollTop = box.scrollHeight;
    }).catch(function() {
        document.getElementById('typingIndicator').remove();
        showToast('NPC 请求失败', 'err');
    });
}

function townChatEnter(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); townSend(); }
}

// ===== 小镇日报 (NPC 日记) =====
var diaryLoading = false;
function loadTownDiary() {
    if (diaryLoading) return;
    diaryLoading = true;
    var grid = document.getElementById('diaryGrid');
    var st = document.getElementById('diaryStatus');
    st.textContent = '⏳ AI 正在为 6 位 NPC 写日记...';
    grid.innerHTML = '';
    for (var i = 0; i < 6; i++) {
        var ph = document.createElement('div');
        ph.className = 'npc-card';
        ph.innerHTML = '<div class="npc-emoji">✍️</div><div class="npc-role">写作中...</div>';
        grid.appendChild(ph);
    }
    var weather = document.getElementById('npcWeather') ? document.getElementById('npcWeather').value : 'clear';
    fetch('/api?action=town_diary&weather=' + weather).then(function(r) { return r.json(); }).then(function(data) {
        diaryLoading = false;
        if (data.error) {
            st.textContent = '❌ ' + data.error;
            grid.innerHTML = '<div style="color:var(--text-dim); font-size:13px;">' + data.error + '</div>';
            return;
        }
        grid.innerHTML = '';
        var okCount = 0;
        (data.diaries || []).forEach(function(d) {
            var card = document.createElement('div');
            card.className = 'npc-card';
            card.style.borderColor = d.color;
            card.style.cursor = 'default';
            if (d.diary) {
                okCount++;
                card.innerHTML = '<div class="npc-emoji">' + d.emoji + '</div>' +
                    '<div class="npc-name" style="color:' + d.color + '; font-size:15px;">' + d.display + '</div>' +
                    '<div style="font-size:13px; line-height:1.6; color:var(--text); margin-top:6px;">' + d.diary + '</div>';
            } else {
                card.innerHTML = '<div class="npc-emoji">' + d.emoji + '</div>' +
                    '<div class="npc-name" style="color:' + d.color + '; font-size:15px;">' + d.display + '</div>' +
                    '<div style="font-size:12px; color:#ff8888; margin-top:6px;">⚠️ ' + (d.err || '生成失败') + '</div>';
            }
            grid.appendChild(card);
        });
        st.textContent = okCount > 0 ? ('✅ ' + okCount + '/6 篇日记已生成') : '❌ 全部生成失败 (检查 STEPFUN_API_KEY)';
        if (okCount > 0) showToast('📖 今日日报已生成 (' + okCount + '/6)');
    }).catch(function() {
        diaryLoading = false;
        st.textContent = '❌ 请求失败';
    });
}

// ===== NPC 关系图谱 (圆形布局 + 加权边) =====
function renderRelations() {
    var canvas = document.getElementById('relationCanvas');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    var w = canvas.width, h = canvas.height;
    ctx.fillStyle = '#0d1117';
    ctx.fillRect(0, 0, w, h);

    fetch('/api?action=town_relations').then(function(r) { return r.json(); }).then(function(data) {
        var nodes = data.nodes || [];
        var edges = data.edges || [];
        if (nodes.length === 0) { ctx.fillStyle = '#6272a4'; ctx.font = '14px sans-serif'; ctx.textAlign = 'center'; ctx.fillText('无数据', w/2, h/2); return; }

        var cx = w/2, cy = h/2 + 6;
        var radius = Math.min(w, h)/2 - 52;
        var posMap = {};
        nodes.forEach(function(n, i) {
            var angle = -Math.PI/2 + i * 2*Math.PI/nodes.length;
            posMap[n.name] = { x: cx + radius*Math.cos(angle), y: cy + radius*Math.sin(angle) };
        });

        // 边: 宽度/透明度按好感度
        edges.forEach(function(e) {
            var a = posMap[e.a], b = posMap[e.b];
            if (!a || !b) return;
            var t = Math.max(0, Math.min(1, (e.score - 30) / 50));  // 30-80 → 0-1
            ctx.strokeStyle = 'rgba(80,250,123,' + (0.18 + t*0.65).toFixed(2) + ')';
            ctx.lineWidth = 1 + t*5;
            ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
            // 边上分数
            var mx = (a.x+b.x)/2, my = (a.y+b.y)/2;
            ctx.fillStyle = 'rgba(139,233,253,0.85)';
            ctx.font = '11px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(e.score, mx, my - 4);
        });

        // 节点
        nodes.forEach(function(n) {
            var p = posMap[n.name];
            // 头像底
            ctx.fillStyle = n.color;
            ctx.globalAlpha = 0.25;
            ctx.beginPath(); ctx.arc(p.x, p.y, 26, 0, 2*Math.PI); ctx.fill();
            ctx.globalAlpha = 1;
            ctx.strokeStyle = n.color;
            ctx.lineWidth = 2;
            ctx.beginPath(); ctx.arc(p.x, p.y, 26, 0, 2*Math.PI); ctx.stroke();
            // emoji + 名字
            ctx.font = '20px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(n.emoji, p.x, p.y + 7);
            ctx.fillStyle = n.color;
            ctx.font = '600 12px sans-serif';
            ctx.fillText(n.display, p.x, p.y + 44);
        });
    }).catch(function() {
        ctx.fillStyle = '#ff5555';
        ctx.font = '13px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('图谱加载失败', w/2, h/2);
    });
}
</script>
</body>
</html>'''
