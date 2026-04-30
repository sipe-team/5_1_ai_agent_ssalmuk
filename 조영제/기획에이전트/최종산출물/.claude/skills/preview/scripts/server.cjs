const crypto = require('crypto');
const http = require('http');
const fs = require('fs');
const path = require('path');

// ========== WebSocket Protocol (RFC 6455) ==========

const OPCODES = { TEXT: 0x01, CLOSE: 0x08, PING: 0x09, PONG: 0x0A };
const WS_MAGIC = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11';

function computeAcceptKey(clientKey) {
  return crypto.createHash('sha1').update(clientKey + WS_MAGIC).digest('base64');
}

function encodeFrame(opcode, payload) {
  const fin = 0x80;
  const len = payload.length;
  let header;
  if (len < 126) {
    header = Buffer.alloc(2);
    header[0] = fin | opcode;
    header[1] = len;
  } else if (len < 65536) {
    header = Buffer.alloc(4);
    header[0] = fin | opcode;
    header[1] = 126;
    header.writeUInt16BE(len, 2);
  } else {
    header = Buffer.alloc(10);
    header[0] = fin | opcode;
    header[1] = 127;
    header.writeBigUInt64BE(BigInt(len), 2);
  }
  return Buffer.concat([header, payload]);
}

function decodeFrame(buffer) {
  if (buffer.length < 2) return null;
  const secondByte = buffer[1];
  const opcode = buffer[0] & 0x0F;
  const masked = (secondByte & 0x80) !== 0;
  let payloadLen = secondByte & 0x7F;
  let offset = 2;
  if (!masked) throw new Error('Client frames must be masked');
  if (payloadLen === 126) {
    if (buffer.length < 4) return null;
    payloadLen = buffer.readUInt16BE(2);
    offset = 4;
  } else if (payloadLen === 127) {
    if (buffer.length < 10) return null;
    payloadLen = Number(buffer.readBigUInt64BE(2));
    offset = 10;
  }
  const maskOffset = offset;
  const dataOffset = offset + 4;
  const totalLen = dataOffset + payloadLen;
  if (buffer.length < totalLen) return null;
  const mask = buffer.slice(maskOffset, dataOffset);
  const data = Buffer.alloc(payloadLen);
  for (let i = 0; i < payloadLen; i++) {
    data[i] = buffer[dataOffset + i] ^ mask[i % 4];
  }
  return { opcode, payload: data, bytesConsumed: totalLen };
}

// ========== Configuration ==========

const PORT = process.env.PREVIEW_PORT || (49152 + Math.floor(Math.random() * 16383));
const HOST = process.env.PREVIEW_HOST || '127.0.0.1';
const URL_HOST = process.env.PREVIEW_URL_HOST || (HOST === '127.0.0.1' ? 'localhost' : HOST);
const PROJECT_DIR = process.env.PREVIEW_PROJECT_DIR || process.cwd();
const STATE_DIR = process.env.PREVIEW_STATE_DIR || '/tmp/preview-gallery';
let ownerPid = process.env.PREVIEW_OWNER_PID ? Number(process.env.PREVIEW_OWNER_PID) : null;

const MIME_TYPES = {
  '.html': 'text/html', '.css': 'text/css', '.js': 'application/javascript',
  '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.svg': 'image/svg+xml'
};

// ========== File Scanner ==========

function scanHtmlFiles() {
  const specsDir = path.join(PROJECT_DIR, 'docs', 'specs');
  const files = [];

  if (!fs.existsSync(specsDir)) return files;

  const features = fs.readdirSync(specsDir).filter(f => {
    const fp = path.join(specsDir, f);
    return fs.statSync(fp).isDirectory();
  });

  for (const feature of features) {
    const featureDir = path.join(specsDir, feature);
    const subdirs = ['designs', 'diagrams'];

    for (const sub of subdirs) {
      const subDir = path.join(featureDir, sub);
      if (!fs.existsSync(subDir)) continue;

      const htmlFiles = fs.readdirSync(subDir).filter(f => f.endsWith('.html'));
      for (const file of htmlFiles) {
        const filePath = path.join(subDir, file);
        const stat = fs.statSync(filePath);
        files.push({
          feature,
          category: sub === 'designs' ? 'design' : 'diagram',
          name: file.replace('.html', ''),
          filename: file,
          path: filePath,
          relativePath: `/${feature}/${sub}/${file}`,
          mtime: stat.mtime.getTime()
        });
      }
    }
  }

  return files.sort((a, b) => b.mtime - a.mtime);
}

// ========== Gallery HTML Generator ==========

function generateGallery(files) {
  const designCount = files.filter(f => f.category === 'design').length;
  const diagramCount = files.filter(f => f.category === 'diagram').length;
  const features = [...new Set(files.map(f => f.feature))];

  const cards = files.map(f => `
      <div class="card" data-category="${f.category}" data-feature="${f.feature}">
        <div class="card-badge ${f.category}">${f.category === 'design' ? 'Design' : 'Diagram'}</div>
        <div class="card-body">
          <div class="card-feature">${f.feature}</div>
          <div class="card-name">${f.name}</div>
          <div class="card-time">${new Date(f.mtime).toLocaleString('ko-KR')}</div>
        </div>
        <a class="card-link" href="${f.relativePath}" target="_blank">Open</a>
      </div>`).join('\n');

  return `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Preview Gallery</title>
<link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/variable/pretendardvariable-dynamic-subset.css" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Pretendard Variable', -apple-system, sans-serif;
    background: #0f0f0f; color: #e0e0e0;
    min-height: 100vh;
  }
  .header {
    padding: 2rem 2rem 1rem;
    border-bottom: 1px solid #222;
  }
  .header h1 { font-size: 1.5rem; font-weight: 600; color: #fff; }
  .header .stats {
    margin-top: 0.5rem; font-size: 0.85rem; color: #888;
  }
  .filters {
    display: flex; gap: 0.5rem;
    padding: 1rem 2rem;
    border-bottom: 1px solid #1a1a1a;
    flex-wrap: wrap;
  }
  .filter-btn {
    padding: 0.4rem 0.9rem; border-radius: 6px;
    border: 1px solid #333; background: transparent;
    color: #aaa; cursor: pointer; font-size: 0.8rem;
    font-family: inherit; transition: all 0.15s;
  }
  .filter-btn:hover { border-color: #555; color: #ddd; }
  .filter-btn.active { background: #fff; color: #000; border-color: #fff; }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem; padding: 1.5rem 2rem;
  }
  .card {
    background: #181818; border: 1px solid #252525;
    border-radius: 8px; overflow: hidden;
    transition: border-color 0.15s, transform 0.15s;
    position: relative;
  }
  .card:hover { border-color: #444; transform: translateY(-2px); }
  .card.hidden { display: none; }
  .card-badge {
    display: inline-block; padding: 0.25rem 0.6rem;
    font-size: 0.7rem; font-weight: 500;
    border-radius: 4px; margin: 1rem 1rem 0;
    text-transform: uppercase; letter-spacing: 0.05em;
  }
  .card-badge.design { background: #1a1a2e; color: #818cf8; }
  .card-badge.diagram { background: #1a2e1a; color: #6ee7b7; }
  .card-body { padding: 0.75rem 1rem 1rem; }
  .card-feature {
    font-size: 0.75rem; color: #666;
    margin-bottom: 0.25rem;
  }
  .card-name {
    font-size: 1rem; font-weight: 500;
    color: #f0f0f0; margin-bottom: 0.5rem;
  }
  .card-time { font-size: 0.7rem; color: #555; }
  .card-link {
    display: block; text-align: center;
    padding: 0.6rem; border-top: 1px solid #252525;
    color: #aaa; text-decoration: none;
    font-size: 0.8rem; font-weight: 500;
    transition: background 0.15s, color 0.15s;
  }
  .card-link:hover { background: #222; color: #fff; }
  .empty {
    text-align: center; padding: 4rem 2rem;
    color: #555; font-size: 0.95rem;
  }
  .empty code {
    display: block; margin-top: 1rem;
    color: #777; font-size: 0.85rem;
  }
</style>
</head>
<body>
  <div class="header">
    <h1>Preview Gallery</h1>
    <div class="stats">${files.length}개 파일 | ${designCount} design, ${diagramCount} diagram | ${features.length} feature</div>
  </div>
  <div class="filters">
    <button class="filter-btn active" data-filter="all">All (${files.length})</button>
    <button class="filter-btn" data-filter="design">Design (${designCount})</button>
    <button class="filter-btn" data-filter="diagram">Diagram (${diagramCount})</button>
    ${features.map(f => `<button class="filter-btn" data-filter="feature:${f}">${f}</button>`).join('\n    ')}
  </div>
  ${files.length > 0 ? `<div class="grid">${cards}</div>` : `
  <div class="empty">
    아직 HTML 파일이 없습니다.
    <code>docs/specs/{기능명}/designs/*.html<br>docs/specs/{기능명}/diagrams/*.html</code>
  </div>`}
<script>
  // Filters
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.dataset.filter;
      document.querySelectorAll('.card').forEach(card => {
        if (filter === 'all') {
          card.classList.remove('hidden');
        } else if (filter.startsWith('feature:')) {
          card.classList.toggle('hidden', card.dataset.feature !== filter.slice(8));
        } else {
          card.classList.toggle('hidden', card.dataset.category !== filter);
        }
      });
    });
  });

  // WebSocket auto-reload
  (function() {
    function connect() {
      const ws = new WebSocket('ws://' + window.location.host);
      ws.onmessage = (msg) => {
        const data = JSON.parse(msg.data);
        if (data.type === 'reload') window.location.reload();
      };
      ws.onclose = () => setTimeout(connect, 2000);
    }
    connect();
  })();
</script>
</body>
</html>`;
}

// ========== HTTP Request Handler ==========

function handleRequest(req, res) {
  touchActivity();

  if (req.method === 'GET' && req.url === '/') {
    const files = scanHtmlFiles();
    const html = generateGallery(files);
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(html);
    return;
  }

  // Serve files from docs/specs/
  if (req.method === 'GET') {
    const urlPath = decodeURIComponent(req.url);
    const filePath = path.join(PROJECT_DIR, 'docs', 'specs', urlPath);
    const resolved = path.resolve(filePath);
    const specsRoot = path.resolve(path.join(PROJECT_DIR, 'docs', 'specs'));

    // Security: prevent path traversal
    if (!resolved.startsWith(specsRoot)) {
      res.writeHead(403);
      res.end('Forbidden');
      return;
    }

    if (fs.existsSync(resolved) && fs.statSync(resolved).isFile()) {
      const ext = path.extname(resolved).toLowerCase();
      const contentType = MIME_TYPES[ext] || 'application/octet-stream';
      res.writeHead(200, { 'Content-Type': contentType + '; charset=utf-8' });
      res.end(fs.readFileSync(resolved));
      return;
    }
  }

  res.writeHead(404);
  res.end('Not found');
}

// ========== WebSocket ==========

const clients = new Set();

function handleUpgrade(req, socket) {
  const key = req.headers['sec-websocket-key'];
  if (!key) { socket.destroy(); return; }
  const accept = computeAcceptKey(key);
  socket.write(
    'HTTP/1.1 101 Switching Protocols\r\n' +
    'Upgrade: websocket\r\n' +
    'Connection: Upgrade\r\n' +
    'Sec-WebSocket-Accept: ' + accept + '\r\n\r\n'
  );
  let buffer = Buffer.alloc(0);
  clients.add(socket);
  socket.on('data', (chunk) => {
    buffer = Buffer.concat([buffer, chunk]);
    while (buffer.length > 0) {
      let result;
      try { result = decodeFrame(buffer); } catch (e) {
        socket.end(encodeFrame(OPCODES.CLOSE, Buffer.alloc(0)));
        clients.delete(socket);
        return;
      }
      if (!result) break;
      buffer = buffer.slice(result.bytesConsumed);
      if (result.opcode === OPCODES.CLOSE) {
        socket.end(encodeFrame(OPCODES.CLOSE, Buffer.alloc(0)));
        clients.delete(socket);
        return;
      }
      if (result.opcode === OPCODES.PING) {
        socket.write(encodeFrame(OPCODES.PONG, result.payload));
      }
    }
  });
  socket.on('close', () => clients.delete(socket));
  socket.on('error', () => clients.delete(socket));
}

function broadcast(msg) {
  const frame = encodeFrame(OPCODES.TEXT, Buffer.from(JSON.stringify(msg)));
  for (const socket of clients) {
    try { socket.write(frame); } catch (e) { clients.delete(socket); }
  }
}

// ========== Activity Tracking ==========

const IDLE_TIMEOUT_MS = 60 * 60 * 1000; // 1 hour (gallery is less interactive)
let lastActivity = Date.now();
function touchActivity() { lastActivity = Date.now(); }

// ========== File Watching ==========

function watchSpecsDir() {
  const specsDir = path.join(PROJECT_DIR, 'docs', 'specs');
  if (!fs.existsSync(specsDir)) return null;

  const watchers = [];
  const debounceTimer = { id: null };

  function notifyReload() {
    if (debounceTimer.id) clearTimeout(debounceTimer.id);
    debounceTimer.id = setTimeout(() => {
      debounceTimer.id = null;
      touchActivity();
      broadcast({ type: 'reload' });
      console.log(JSON.stringify({ type: 'files-changed' }));
    }, 300);
  }

  // Watch top-level specs dir for new feature folders
  try {
    const w = fs.watch(specsDir, () => notifyReload());
    w.on('error', () => {});
    watchers.push(w);
  } catch (e) {}

  // Watch each feature's designs/ and diagrams/ dirs
  const features = fs.readdirSync(specsDir).filter(f => {
    return fs.statSync(path.join(specsDir, f)).isDirectory();
  });

  for (const feature of features) {
    for (const sub of ['designs', 'diagrams']) {
      const dir = path.join(specsDir, feature, sub);
      if (!fs.existsSync(dir)) continue;
      try {
        const w = fs.watch(dir, () => notifyReload());
        w.on('error', () => {});
        watchers.push(w);
      } catch (e) {}
    }
  }

  return watchers;
}

// ========== Server Startup ==========

function startServer() {
  if (!fs.existsSync(STATE_DIR)) fs.mkdirSync(STATE_DIR, { recursive: true });

  const server = http.createServer(handleRequest);
  server.on('upgrade', handleUpgrade);

  const watchers = watchSpecsDir();

  function ownerAlive() {
    if (!ownerPid) return true;
    try { process.kill(ownerPid, 0); return true; } catch (e) { return e.code === 'EPERM'; }
  }

  function shutdown(reason) {
    console.log(JSON.stringify({ type: 'server-stopped', reason }));
    const infoFile = path.join(STATE_DIR, 'server-info');
    if (fs.existsSync(infoFile)) fs.unlinkSync(infoFile);
    fs.writeFileSync(
      path.join(STATE_DIR, 'server-stopped'),
      JSON.stringify({ reason, timestamp: Date.now() }) + '\n'
    );
    if (watchers) watchers.forEach(w => w.close());
    clearInterval(lifecycleCheck);
    server.close(() => process.exit(0));
  }

  const lifecycleCheck = setInterval(() => {
    if (!ownerAlive()) shutdown('owner process exited');
    else if (Date.now() - lastActivity > IDLE_TIMEOUT_MS) shutdown('idle timeout');
  }, 60 * 1000);
  lifecycleCheck.unref();

  if (ownerPid) {
    try { process.kill(ownerPid, 0); }
    catch (e) {
      if (e.code !== 'EPERM') {
        console.log(JSON.stringify({ type: 'owner-pid-invalid', pid: ownerPid, reason: 'dead at startup' }));
        ownerPid = null;
      }
    }
  }

  server.listen(PORT, HOST, () => {
    const files = scanHtmlFiles();
    const info = JSON.stringify({
      type: 'server-started', port: Number(PORT), host: HOST,
      url_host: URL_HOST, url: 'http://' + URL_HOST + ':' + PORT,
      project_dir: PROJECT_DIR, file_count: files.length
    });
    console.log(info);
    fs.writeFileSync(path.join(STATE_DIR, 'server-info'), info + '\n');
  });
}

if (require.main === module) {
  startServer();
}
