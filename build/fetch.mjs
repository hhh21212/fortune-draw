// 抓取吕祖灵签 1~100 签原始页面，缓存到 build/pages/，并解析为 build/raw.json
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BASE = 'https://m.zgjmorg.com/chouqian/lvzu/';
const PAGES_DIR = path.join(__dirname, 'pages');
const RAW = path.join(__dirname, 'raw.json');
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36';

fs.mkdirSync(PAGES_DIR, { recursive: true });

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

function decode(s) {
  return s
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&ldquo;|&rdquo;/g, '"')
    .replace(/&lsquo;|&rsquo;/g, "'");
}

function stripTags(s) {
  return s.replace(/<[^>]+>/g, '');
}

// 规范化：统一全角冒号、去空白，用于标签匹配
function norm(s) {
  return s.replace(/：/g, ':').replace(/[\s　]+/g, '');
}

// 判断某行是否为「吕祖灵签(第X签)?：标签」形式，返回标签词
function labelOf(t) {
  const s = norm(t)
    .replace(/^吕祖灵签/, '')
    .replace(/^第[一二三四五六七八九十百]+签/, '')
    .replace(/^:/, '');
  if (['解签', '诗曰', '解诗', '解曰', '签曰'].includes(s)) return s;
  return null;
}

async function fetchPage(i) {
  const file = path.join(PAGES_DIR, `${i}.html`);
  if (fs.existsSync(file)) {
    return fs.readFileSync(file, 'utf8');
  }
  const url = `${BASE}${i}.html`;
  const res = await fetch(url, { headers: { 'User-Agent': UA, 'Accept-Language': 'zh-CN,zh;q=0.9' } });
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  const html = await res.text();
  fs.writeFileSync(file, html, 'utf8');
  await sleep(180);
  return html;
}

function parse(html, id) {
  const m = html.match(/<div class="read-content">([\s\S]*?)<\/div>/);
  if (!m) return null;
  const block = m[1].replace(/<img[^>]*>/gi, '');
  const ps = [...block.matchAll(/<p[^>]*>([\s\S]*?)<\/p>/gi)].map(x => x[1]);
  const texts = ps.map(p => decode(stripTags(p)).replace(/[　\s]+/g, ' ').trim()).filter(Boolean);

  // 标题行（第 0 行）：提取典故
  const titleLine = texts[0] || '';
  const tm = titleLine.match(/第[一二三四五六七八九十百]+签[:：]?\s*(.*?)(?:吕祖灵签解签|$)/);
  const title = (tm ? tm[1] : '').trim();

  // 定位各标签
  let iJie = -1, iShi = -1, iJieshi = -1;
  for (let k = 1; k < texts.length; k++) {
    const lb = labelOf(texts[k]);
    if (lb === '解签' && iJie < 0) iJie = k;
    else if (lb === '诗曰' && iShi < 0) iShi = k;
    else if (lb === '解诗' && iJieshi < 0) iJieshi = k;
  }

  // 签文：标题行之后、解签标签（或诗曰）之前的所有行拼接
  const poemEnd = [iJie, iShi, iJieshi].filter(x => x > 0).sort((a, b) => a - b)[0] || texts.length;
  const poem = texts.slice(1, poemEnd).join('').trim();

  const jie = iJie >= 0 ? (texts[iJie + 1] || '').trim() : '';
  const shi = iShi >= 0 ? (texts[iShi + 1] || '').trim() : '';
  const jieshi = iJieshi >= 0 ? (texts[iJieshi + 1] || '').trim() : '';

  // 12 项运程
  const fortunes = {};
  const keys = ['谋望', '钱财', '婚姻', '自身', '家宅', '开业', '迁居', '出行', '疾病', '六甲', '行人', '诉讼'];
  const start = Math.max(iJieshi, iShi, iJie, 0) + 1;
  for (let k = start; k < texts.length; k++) {
    const t = norm(texts[k]);
    for (const key of keys) {
      if (t.startsWith(key + ':')) {
        fortunes[key] = texts[k].replace(/：/g, ':').replace(new RegExp('^' + key + ':'), '').trim();
        break;
      }
    }
  }

  return { id, title, poem, jie, shi, jieshi, fortunes };
}

const out = [];
for (let i = 1; i <= 100; i++) {
  const html = await fetchPage(i);
  const d = parse(html, i);
  if (!d) {
    console.error(`!! 第${i}签解析失败`);
    continue;
  }
  out.push(d);
  if (i % 10 === 0) console.log(`已处理 ${i}/100`);
}

fs.writeFileSync(RAW, JSON.stringify(out, null, 2), 'utf8');
console.log(`完成，共解析 ${out.length} 签 -> ${RAW}`);
