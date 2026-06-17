// Minimal, dependency-free Markdown -> styled HTML converter for the planning
// docs in this repo (headings, GFM tables, bullet lists, bold/italic/code,
// wrapped paragraphs). Not a full CommonMark parser -- just the subset these
// docs use. Usage:  node build/md_to_html.mjs SESSION_PLAN.md > out.html
import fs from 'node:fs';

const path = process.argv[2];
if (!path) { console.error('usage: md_to_html.mjs <file.md>'); process.exit(1); }
const src = fs.readFileSync(path, 'utf8');

const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
function inline(text) {
  let t = esc(text);
  t = t.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');   // bold first
  t = t.replace(/\*(.+?)\*/g, '<em>$1</em>');                // then italic
  t = t.replace(/`(.+?)`/g, '<code>$1</code>');
  return t;
}
const isTableSep = (l) => /^\s*\|?[\s:|-]+\|?\s*$/.test(l) && l.includes('-');
function splitRow(l) {
  let s = l.trim();
  if (s.startsWith('|')) s = s.slice(1);
  if (s.endsWith('|')) s = s.slice(0, -1);
  return s.split('|').map((c) => c.trim());
}

const lines = src.split('\n');
let body = '';
let i = 0;
let title = 'Document';
while (i < lines.length) {
  const line = lines[i];
  if (line.trim() === '') { i++; continue; }

  if (/^#\s+/.test(line)) {
    const txt = line.replace(/^#\s+/, '');
    title = txt.replace(/\*\*?/g, '');
    body += `<h1>${inline(txt)}</h1>\n`; i++; continue;
  }
  if (/^##\s+/.test(line)) {
    body += `<h2>${inline(line.replace(/^##\s+/, ''))}</h2>\n`; i++; continue;
  }

  if (line.trim().startsWith('|')) {
    const tbl = [];
    while (i < lines.length && lines[i].trim().startsWith('|')) { tbl.push(lines[i]); i++; }
    const rows = tbl.filter((r) => !isTableSep(r));
    body += '<table>\n';
    rows.forEach((r, idx) => {
      const cells = splitRow(r);
      const tag = idx === 0 ? 'th' : 'td';
      body += '<tr>' + cells.map((c) => `<${tag}>${inline(c)}</${tag}>`).join('') + '</tr>\n';
    });
    body += '</table>\n';
    continue;
  }

  if (/^\s*-\s+/.test(line)) {
    body += '<ul>\n';
    while (i < lines.length) {
      if (/^\s*-\s+/.test(lines[i])) {
        let item = lines[i].replace(/^\s*-\s+/, '');
        i++;
        while (i < lines.length && lines[i].trim() !== '' &&
               !/^\s*-\s+/.test(lines[i]) && !/^#/.test(lines[i]) &&
               !lines[i].trim().startsWith('|')) {
          item += ' ' + lines[i].trim(); i++;
        }
        body += `<li>${inline(item)}</li>\n`;
      } else { if (lines[i].trim() === '') i++; break; }
    }
    body += '</ul>\n';
    continue;
  }

  let para = line.trim(); i++;
  while (i < lines.length && lines[i].trim() !== '' && !/^#/.test(lines[i]) &&
         !lines[i].trim().startsWith('|') && !/^\s*-\s+/.test(lines[i])) {
    para += ' ' + lines[i].trim(); i++;
  }
  body += `<p>${inline(para)}</p>\n`;
}

const css = `
@page { size: A4; margin: 15mm 16mm; }
* { box-sizing: border-box; }
body { font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  color: #222; font-size: 10.5pt; line-height: 1.5; margin: 0; }
h1 { font-size: 21pt; color: #1f2d3d; margin: 0 0 4px; line-height: 1.2;
  border-bottom: 3px solid #0b6e7a; padding-bottom: 6px; }
h2 { font-size: 13pt; color: #1f2d3d; margin: 18px 0 6px;
  border-bottom: 1px solid #d4dde2; padding-bottom: 3px; }
p { margin: 6px 0; }
ul { margin: 6px 0; padding-left: 18px; }
li { margin: 3px 0; }
table { width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 9.5pt; }
th { background: #1f2d3d; color: #fff; text-align: left; padding: 7px 9px; font-weight: 700; }
td { padding: 6px 9px; border-bottom: 1px solid #e3e8eb; vertical-align: top; }
tr:nth-child(even) td { background: #f4f7f8; }
code { background: #eef2f4; padding: 1px 4px; border-radius: 3px;
  font-family: 'SF Mono',Menlo,Consolas,monospace; font-size: 9pt; }
strong { color: #16222e; }
h2, table, ul { page-break-inside: avoid; }
`;

process.stdout.write(`<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>${esc(title)}</title>
<style>${css}</style></head>
<body>
${body}</body></html>
`);
