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
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; background:#1a1a2e; color:#e0e0e0; min-height:100vh; font-size:15px; }
.container { max-width:960px; margin:0 auto; padding:24px; }
h1 { text-align:center; font-size:26px; margin:10px 0 6px; color:#50fa7b; }
.subtitle { text-align:center; color:#888; font-size:14px; margin-bottom:20px; }
.card { background:#16213e; border-radius:12px; padding:24px; margin-bottom:18px; box-shadow:0 4px 6px rgba(0,0,0,0.3); }
label { display:block; font-size:15px; color:#aaa; margin-bottom:8px; }
input[type="text"] { width:100%; padding:14px; font-size:17px; border:2px solid #0f3460; border-radius:8px; background:#1a1a2e; color:#fff; }
input[type="text"]:focus { outline:none; border-color:#50fa7b; }
.examples { margin-top:10px; }
.example-btn { display:inline-block; background:#0f3460; color:#8be9fd; padding:6px 12px; border-radius:6px; font-size:13px; margin:4px; cursor:pointer; border:1px solid #1a4080; transition:0.2s; }
.example-btn:hover { background:#1a4080; }
.btn-row { display:flex; gap:12px; margin-top:14px; flex-wrap:wrap; }
button { padding:12px 24px; font-size:15px; border:none; border-radius:8px; cursor:pointer; font-weight:600; transition:0.2s; }
.btn-parse { background:#0f3460; color:#8be9fd; }
.btn-parse:hover { background:#1a4080; }
.btn-gen { background:#5046e5; color:#fff; }
.btn-gen:hover { background:#6056f5; }
.btn-install { background:#50fa7b; color:#1a1a2e; }
.btn-install:hover { background:#60ffa0; }
.btn-all { background:#ff79c6; color:#fff; }
.btn-all:hover { background:#ff99d6; }
.btn-preview { background:#f1fa8c; color:#1a1a2e; }
.btn-preview:hover { background:#ffffaa; }
.btn-launch { background:#50fa7b; color:#1a1a2e; border:2px solid #50fa7b; }
.btn-launch:hover { background:#60ffa0; box-shadow:0 0 12px #50fa7b; }
.btn-ai { background:#bd93f9; color:#1a1a2e; }
.btn-ai:hover { background:#caa0ff; }
.btn-ai-all { background:#ff6b6b; color:#fff; }
.btn-ai-all:hover { background:#ff8585; box-shadow:0 0 12px #ff6b6b; }
.ai-settings { background:#0d1117; border:1px solid #333; border-radius:8px; padding:14px; margin-top:12px; }
.ai-settings label { font-size:13px; color:#6272a4; margin-bottom:4px; }
.ai-settings input { width:100%; padding:8px; background:#1a1a2e; color:#e0e0e0; border:1px solid #0f3460; border-radius:6px; font-size:14px; margin-bottom:8px; }
.ai-settings input:focus { outline:none; border-color:#50fa7b; }
.ai-row { display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; }
@media(max-width:600px) { .ai-row { grid-template-columns:1fr; } }
.ai-loading { display:none; text-align:center; padding:20px; }
.ai-loading.show { display:block; }
.spinner { display:inline-block; width:32px; height:32px; border:3px solid #333; border-top:3px solid #50fa7b; border-radius:50%; animation:spin 1s linear infinite; }
@keyframes spin { 0%{transform:rotate(0)} 100%{transform:rotate(360deg)} }
.preview-container { position:relative; background:#0d1117; border-radius:8px; border:1px solid #333; overflow:hidden; }
.preview-canvas { display:block; margin:0 auto; cursor:grab; }
.preview-canvas:active { cursor:grabbing; }
.preview-controls { position:absolute; top:8px; right:8px; display:flex; gap:6px; }
.preview-controls button { padding:5px 12px; font-size:13px; background:#0f3460; color:#8be9fd; border-radius:4px; }
.result { background:#0d1117; border-radius:8px; padding:14px; font-family:monospace; font-size:14px; white-space:pre-wrap; color:#8be9fd; min-height:50px; }
.code-box { background:#0d1117; border-radius:8px; padding:14px; font-family:"Courier New",monospace; font-size:13px; white-space:pre; overflow:auto; max-height:400px; color:#c0c0c0; border:1px solid #333; }
.status { padding:10px 18px; border-radius:8px; margin-top:10px; font-size:15px; }
.status-ok { background:#1a3a1a; color:#50fa7b; }
.status-warn { background:#3a3a1a; color:#f1fa8c; }
.status-err { background:#3a1a1a; color:#ff5555; }
.path-info { font-size:13px; color:#6272a4; margin-top:8px; word-break:break-all; }
.grid { display:grid; grid-template-columns:1fr 1fr; gap:18px; }
@media(max-width:600px) { .grid { grid-template-columns:1fr; } .btn-row { flex-direction:column; } }
table { width:100%; border-collapse:collapse; font-size:14px; }
th,td { padding:8px 12px; border-bottom:1px solid #333; text-align:left; }
th { color:#50fa7b; }
td { color:#aaa; }
</style>
</head>
<body>
<div class="container">
<h1>🏗️ Luanti 自然语言建筑生成器</h1>
<p class="subtitle">输入自然语言 → 自动解析 → 生成 Lua mod → 安装到 Luanti</p>

<div class="card">
<label>描述你想要的建筑：</label>
<input type="text" id="input" value="建一个红色的城堡，有塔楼" placeholder="例如：建造一座大型金字塔">
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
<div class="btn-row">
<button class="btn-parse" onclick="doParse()">🔍 解析</button>
<button class="btn-gen" onclick="doGen()">📋 生成 Lua</button>
<button class="btn-install" onclick="doInstall()">💾 安装</button>
<button class="btn-all" onclick="doAll()">🚀 生成并安装</button>
<button class="btn-preview" onclick="doPreview()">👁️ 预览</button>
<button class="btn-launch" onclick="doJoin()">🎮 一键加入游戏</button>
<button class="btn-ai" onclick="doAIPreview()">🤖 AI 预览</button>
<button class="btn-ai-all" onclick="doAIGenerate()">🤖 AI 生成并加入</button>
</div>
<div style="margin-top:8px; display:flex; align-items:center; gap:8px;">
<label style="font-size:13px; color:#6272a4; white-space:nowrap;">选择世界:</label>
<select id="worldSelect" style="flex:1; padding:6px; background:#1a1a2e; color:#e0e0e0; border:1px solid #0f3460; border-radius:6px; font-size:13px;">
<option value="">自动选择</option>
</select>
</div>

<!-- AI 大模型设置 -->
<div class="ai-settings">
<label>🤖 AI 大模型设置 (用于复杂建筑，如"比萨斜塔""埃菲尔铁塔")</label>
<div style="margin-bottom:10px;">
<label>快速选择</label>
<select id="aiProvider" onchange="switchProvider()" style="width:100%; padding:8px; background:#1a1a2e; color:#e0e0e0; border:1px solid #0f3460; border-radius:6px; font-size:14px;">
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
<p style="font-size:12px; color:#6272a4; margin-top:6px;">API Key 保存在浏览器本地，不会上传。</p>
</div>

<!-- AI 加载动画 -->
<div class="ai-loading" id="aiLoading">
<div class="spinner"></div>
<p style="margin-top:10px; color:#6272a4;">🤖 AI 正在生成建筑，请稍候...</p>
</div>
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
<label>3D 预览 (拖拽旋转)：</label>
<div class="preview-container">
<canvas id="previewCanvas" class="preview-canvas" width="600" height="400"></canvas>
<div class="preview-controls">
<button onclick="zoomPreview(1.2)">➕</button>
<button onclick="zoomPreview(0.8)">➖</button>
<button onclick="resetPreview()">🔄</button>
</div>
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

<script>
function setInput(text) { document.getElementById('input').value = text; }
function setStatus(msg, cls) {
    const s = document.getElementById('status');
    s.textContent = msg;
    s.className = 'status ' + (cls || 'status-ok');
}
function fetchAPI(action, params) {
    const input = document.getElementById('input').value;
    const url = '/api?action=' + action + '&input=' + encodeURIComponent(input);
    return fetch(url).then(r => r.json());
}
function doParse() {
    fetchAPI('parse').then(data => {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        const p = data.params;
        const sizes = ['小','中','大','巨大'];
        const text = `类型: ${p.type || '未知'}\\n颜色: ${p.color || '默认'}\\n尺寸: ${sizes[p.size]}\\n材质: ${p.material || '默认'}\\n特征: ${p.features && p.features.length ? p.features.join(', ') : '无'}`;
        document.getElementById('result').textContent = text;
        setStatus('✅ 解析完成', 'status-ok');
    });
}
function doGen() {
    fetchAPI('generate').then(data => {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        document.getElementById('code').textContent = data.lua;
        setStatus('✅ Lua 代码已生成', 'status-ok');
    });
}
function doInstall() {
    fetchAPI('install').then(data => {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        document.getElementById('code').textContent = data.lua;
        document.getElementById('pathInfo').textContent = '安装路径: ' + data.path;
        setStatus('✅ 已安装到 Luanti mods 目录！进入游戏输入 /build 生成建筑', 'status-ok');
    });
}
function doAll() {
    doParse();
    doInstall();
    doPreview();
}
function doLaunch() {
    setStatus('⏳ 正在启动 Luanti...', 'status-warn');
    fetch('/api?action=launch').then(r => r.json()).then(data => {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        setStatus('✅ Luanti 已启动！进入游戏后输入 /build 生成建筑', 'status-ok');
    }).catch(() => {
        setStatus('❌ 启动失败，请手动打开 Luanti', 'status-err');
    });
}
function doJoin() {
    const world = document.getElementById('worldSelect').value;
    const input = document.getElementById('input').value;
    setStatus('⏳ 正在安装 mod + 启用世界 + 启动游戏...', 'status-warn');
    const url = '/api?action=join&input=' + encodeURIComponent(input) + (world ? '&world=' + encodeURIComponent(world) : '');
    fetch(url).then(r => r.json()).then(data => {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        document.getElementById('code').textContent = data.lua || '';
        document.getElementById('pathInfo').textContent = 'Mod: ' + (data.mod_path||'') + ' | 世界: ' + (data.world_path||'');
        const lr = data.launch || {};
        if(lr.error) {
            setStatus('⚠️ Mod已安装但启动失败: ' + lr.error + '。请手动启动', 'status-warn');
        } else {
            setStatus('✅ 一键完成！游戏已启动，进入后输入 /build 生成建筑', 'status-ok');
        }
    }).catch(() => {
        setStatus('❌ 请求失败', 'status-err');
    });
}

// ===== AI 大模型功能 =====
function saveAIConfig() {
    localStorage.setItem('ai_api_key', document.getElementById('apiKey').value);
    localStorage.setItem('ai_base_url', document.getElementById('baseUrl').value);
    localStorage.setItem('ai_model', document.getElementById('modelName').value);
    localStorage.setItem('ai_provider', document.getElementById('aiProvider').value);
}
function switchProvider() {
    const p = document.getElementById('aiProvider').value;
    const configs = {
        // 国内
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
        // 国际
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
        // 本地
        'ollama':        {url:'http://localhost:11434/v1', model:'llama3.2'},
        'lmstudio':      {url:'http://localhost:1234/v1', model:'local-model'},
        'custom':        {url:'', model:''},
    };
    const c = configs[p];
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
    const input = document.getElementById('input').value;
    const key = encodeURIComponent(document.getElementById('apiKey').value);
    const url_val = encodeURIComponent(document.getElementById('baseUrl').value);
    const model = encodeURIComponent(document.getElementById('modelName').value);
    const world = document.getElementById('worldSelect').value;
    let url = '/api?action=' + action + '&input=' + encodeURIComponent(input) +
              '&api_key=' + key + '&base_url=' + url_val + '&model=' + model;
    if (world) url += '&world=' + encodeURIComponent(world);
    return url;
}
function showAILoading(show) {
    document.getElementById('aiLoading').classList.toggle('show', show);
}
function doAIPreview() {
    const key = document.getElementById('apiKey').value;
    if (!key) { setStatus('⚠️ 请先填写 API Key', 'status-warn'); return; }
    showAILoading(true);
    setStatus('🤖 AI 正在生成...', 'status-warn');
    fetch(getAIUrl('ai_preview')).then(r => r.json()).then(data => {
        showAILoading(false);
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        previewBlocks = data.blocks || [];
        renderPreview();
        setStatus('✅ AI 预览已生成 (' + (data.count||0) + ' 个方块)', 'status-ok');
    }).catch(() => {
        showAILoading(false);
        setStatus('❌ AI 请求失败', 'status-err');
    });
}
function doAIGenerate() {
    const key = document.getElementById('apiKey').value;
    if (!key) { setStatus('⚠️ 请先填写 API Key', 'status-warn'); return; }
    showAILoading(true);
    setStatus('🤖 AI 生成中 + 安装 + 启动游戏...', 'status-warn');
    fetch(getAIUrl('ai_install')).then(r => r.json()).then(data => {
        showAILoading(false);
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        document.getElementById('code').textContent = data.lua || '';
        previewBlocks = data.blocks || [];
        renderPreview();
        document.getElementById('pathInfo').textContent = 'Mod: ' + (data.mod_path||'') + ' | 方块: ' + (data.count||0);
        const lr = data.launch || {};
        if(lr.error) {
            setStatus('⚠️ Mod已安装但启动失败: ' + lr.error, 'status-warn');
        } else {
            setStatus('✅ AI 建筑已生成并安装！(' + (data.count||0) + ' 方块) 进入游戏输入 /build', 'status-ok');
        }
    }).catch(() => {
        showAILoading(false);
        setStatus('❌ AI 请求失败', 'status-err');
    });
}

// ===== 3D 预览 =====
let previewBlocks = [];
let previewState = { angleX: -0.5, angleY: 0.5, zoom: 1.0, dragging: false, lastX: 0, lastY: 0 };

function doPreview() {
    fetchAPI('preview').then(data => {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        previewBlocks = data.blocks || [];
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

function renderPreview() {
    const canvas = document.getElementById('previewCanvas');
    const ctx = canvas.getContext('2d');
    const w = canvas.width, h = canvas.height;
    ctx.fillStyle = '#0d1117';
    ctx.fillRect(0, 0, w, h);

    if (previewBlocks.length === 0) {
        ctx.fillStyle = '#6272a4';
        ctx.font = '14px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('点击「👁️ 预览」按钮查看 3D 效果', w/2, h/2);
        return;
    }

    // 找到边界
    let minX=Infinity, maxX=-Infinity, minY=Infinity, maxY=-Infinity, minZ=Infinity, maxZ=-Infinity;
    for (const b of previewBlocks) {
        minX = Math.min(minX, b.x); maxX = Math.max(maxX, b.x);
        minY = Math.min(minY, b.y); maxY = Math.max(maxY, b.y);
        minZ = Math.min(minZ, b.z); maxZ = Math.max(maxZ, b.z);
    }
    const cx = (minX + maxX) / 2;
    const cy = (minY + maxY) / 2;
    const cz = (minZ + maxZ) / 2;
    const range = Math.max(maxX-minX, maxY-minY, maxZ-minZ) + 2;
    const scale = Math.min(w, h) / range * 0.8 * previewState.zoom;

    // 等距投影变换
    function project(x, y, z) {
        const dx = (x - cx) * scale;
        const dy = (y - cy) * scale;
        const dz = (z - cz) * scale;
        // 先 Y 轴旋转
        const cosY = Math.cos(previewState.angleY);
        const sinY = Math.sin(previewState.angleY);
        const rx = dx * cosY - dz * sinY;
        const rz = dx * sinY + dz * cosY;
        // 再 X 轴旋转
        const cosX = Math.cos(previewState.angleX);
        const sinX = Math.sin(previewState.angleX);
        const ry = dy * cosX - rz * sinX;
        const rz2 = dy * sinX + rz * cosX;
        // 投影
        return {
            sx: w/2 + rx,
            sy: h/2 + ry,
            depth: rz2
        };
    }

    // 画地面网格
    ctx.strokeStyle = '#1a2040';
    ctx.lineWidth = 1;
    const gridSize = Math.max(maxX-minX, maxZ-minZ) + 4;
    const gx0 = (minX + maxX) / 2 - gridSize/2;
    const gz0 = (minZ + maxZ) / 2 - gridSize/2;
    for (let i = 0; i <= gridSize; i += 2) {
        const p1 = project(gx0 + i, minY - 0.5, gz0, 0);
        const p2 = project(gx0 + i, minY - 0.5, gz0 + gridSize, 0);
        ctx.beginPath(); ctx.moveTo(p1.sx, p1.sy); ctx.lineTo(p2.sx, p2.sy); ctx.stroke();
        const p3 = project(gx0, minY - 0.5, gz0 + i, 0);
        const p4 = project(gx0 + gridSize, minY - 0.5, gz0 + i, 0);
        ctx.beginPath(); ctx.moveTo(p3.sx, p3.sy); ctx.lineTo(p4.sx, p4.sy); ctx.stroke();
    }

    // 按深度排序方块
    const projected = previewBlocks.map(b => {
        const p = project(b.x, b.y, b.z);
        return { ...b, ...p };
    });
    projected.sort((a, b) => a.depth - b.depth);

    // 画方块
    const blockSize = Math.max(2, scale * 0.9);
    for (const b of projected) {
        const color = b.color || '#888888';
        ctx.fillStyle = color;
        ctx.fillRect(b.sx - blockSize/2, b.sy - blockSize/2, blockSize, blockSize);
        ctx.strokeStyle = 'rgba(255,255,255,0.15)';
        ctx.lineWidth = 1;
        ctx.strokeRect(b.sx - blockSize/2, b.sy - blockSize/2, blockSize, blockSize);
    }
}

// 拖拽旋转
document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('previewCanvas');
    canvas.addEventListener('mousedown', function(e) {
        previewState.dragging = true;
        previewState.lastX = e.clientX;
        previewState.lastY = e.clientY;
    });
    document.addEventListener('mousemove', function(e) {
        if (!previewState.dragging) return;
        const dx = e.clientX - previewState.lastX;
        const dy = e.clientY - previewState.lastY;
        previewState.angleY += dx * 0.01;
        previewState.angleX += dy * 0.01;
        previewState.angleX = Math.max(-1.5, Math.min(1.5, previewState.angleX));
        previewState.lastX = e.clientX;
        previewState.lastY = e.clientY;
        renderPreview();
    });
    document.addEventListener('mouseup', function() { previewState.dragging = false; });
    // 触摸支持
    canvas.addEventListener('touchstart', function(e) {
        e.preventDefault();
        const t = e.touches[0];
        previewState.dragging = true;
        previewState.lastX = t.clientX;
        previewState.lastY = t.clientY;
    });
    canvas.addEventListener('touchmove', function(e) {
        e.preventDefault();
        if (!previewState.dragging) return;
        const t = e.touches[0];
        const dx = t.clientX - previewState.lastX;
        const dy = t.clientY - previewState.lastY;
        previewState.angleY += dx * 0.01;
        previewState.angleX += dy * 0.01;
        previewState.angleX = Math.max(-1.5, Math.min(1.5, previewState.angleX));
        previewState.lastX = t.clientX;
        previewState.lastY = t.clientY;
        renderPreview();
    });
    canvas.addEventListener('touchend', function() { previewState.dragging = false; });
    // 初始空预览
    renderPreview();
});
// 初始化
fetch('/api?action=info').then(r=>r.json()).then(data => {
    document.getElementById('pathInfo').textContent = 'Mod 目录: ' + data.mods_dir;
    if(data.exists) setStatus('✅ Luanti 目录就绪', 'status-ok');
    else setStatus('⚠️ Luanti 目录不存在，可能需要手动设置', 'status-warn');
});
// 加载世界列表
fetch('/api?action=worlds').then(r=>r.json()).then(data => {
    const sel = document.getElementById('worldSelect');
    (data.worlds || []).forEach(w => {
        const opt = document.createElement('option');
        opt.value = w.dir;
        opt.textContent = w.name;
        sel.appendChild(opt);
    });
});
// 加载 AI 配置
loadAIConfig();
</script>
</body>
</html>'''
