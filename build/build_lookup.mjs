// 将 full.json 注入查找页模板，生成自包含的 lookup.html（道长按签号查询）
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, '..');

const full = JSON.parse(fs.readFileSync(path.join(__dirname, 'full.json'), 'utf8'));
const template = fs.readFileSync(path.join(__dirname, 'lookup-template.html'), 'utf8');

const html = template.replace('/*__DATA__*/', JSON.stringify(full));

const out = path.join(root, 'lookup.html');
fs.writeFileSync(out, html, 'utf8');
console.log('已生成:', out);
console.log('文件大小:', (fs.statSync(out).size / 1024).toFixed(1) + ' KB');
console.log('签条数据条数:', full.length);
