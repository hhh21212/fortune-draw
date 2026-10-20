// 将 data.json 注入模板，生成自包含的单文件 三弘道长求签.html
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, '..');

const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'data.json'), 'utf8'));
const template = fs.readFileSync(path.join(__dirname, 'template.html'), 'utf8');

const json = JSON.stringify(data);
const html = template.replace('/*__DATA__*/', json);

const out = path.join(root, 'index.html');
fs.writeFileSync(out, html, 'utf8');
console.log('已生成:', out);
console.log('文件大小:', (fs.statSync(out).size / 1024).toFixed(1) + ' KB');
console.log('签条数据条数:', data.length);
