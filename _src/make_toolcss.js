// 검사 도구(humanize.js) 화면에 필요한 AIMarker 스타일만 추려 docs/assets/tool.css 로. node _src/make_toolcss.js
const { PurgeCSS } = require('/tmp/purge/node_modules/purgecss');
const fs = require('fs'), path = require('path');
const A = '/home/claude/codediarty/aimarker/assets/';
const OUT = path.join(__dirname, '..', 'docs', 'assets', 'tool.css');
let css = ['am.css', 'v9.css', 'v10.css', 'v11.css', 'v13.css', 'humanize.css', 'hz12.css'].map(f => fs.readFileSync(A + f, 'utf8')).join('\n');
css = css.replace(/@font-face\s*\{[^}]*\}/g, '');
(async () => {
  const r = await new PurgeCSS().purge({
    content: [{ raw: fs.readFileSync(path.join(__dirname, 'pages.py'), 'utf8'), extension: 'html' },
              path.join(__dirname, '..', 'docs', 'assets', 'humanize.js'), path.join(__dirname, '..', 'docs', 'assets', 'am.js'), path.join(__dirname, '..', 'docs', 'assets', 'textin.js')],
    css: [{ raw: css }],
    safelist: { standard: [/^hz\d*-?/, /^ds-/, /^k-btn/, /^twa-/, /^is-/, /^on$/, /^open$/, /^arm$/, /^ico$/, /^sr$/, /^k-sr$/, /^msg/, /^field/, /^inp/, /^sel/, /^hp$/], greedy: [/hz\d/, /dlg/, /prog/] },
    variables: true, keyframes: true, fontFace: false
  });
  let out = r[0].css;
  // 사이트 기본(글꼴 · 본문 · 제목 · 링크)은 hz.css 가 맡음: 요소 하나만 고르는 전역 규칙은 뺌
  out = out.replace(/(^|\})\s*(html|body|html,\s*body|a|a:hover|h1|h2|h3|h4|p|img|button|\*|\*,\s*\*::before,\s*\*::after|::selection)\s*\{[^}]*\}/g, '$1');
  fs.writeFileSync(OUT, '/* 한국휴머나이저 검사 도구 스타일(AIMarker 도구 스타일에서 이 화면에 쓰는 것만 추림, 빌드가 만듦) */\n' + out);
  console.log('tool.css', (out.length / 1024).toFixed(1) + 'KB from', (css.length / 1024).toFixed(1) + 'KB');
})();
