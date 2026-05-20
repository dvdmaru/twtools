const u=["GPTBot","ChatGPT-User","OAI-SearchBot","ClaudeBot","anthropic-ai","Google-Extended","PerplexityBot","CCBot","Bytespider","Applebot-Extended"],m="https://corsproxy.io/?url=";function x(s,a){const t=s.split(/\r?\n/);let n=!1,o=!1,e=!1,r=!1,c=!1;for(const f of t){const l=f.replace(/#.*$/,"").trim();if(!l)continue;const p=l.match(/^User-agent:\s*(.+)$/i);if(p){const i=(p[1]??"").trim();n=i.toLowerCase()===a.toLowerCase(),o=!n,n&&(c=!0),i==="*"&&(o=!1);continue}const d=l.match(/^Disallow:\s*(.*)$/i);if(d){const i=(d[1]??"").trim();n&&i==="/"&&(r=!0),!n&&!o&&i==="/"&&(e=!0)}}return c?!r:!e}async function y(s){const a=new URL("/robots.txt",s).toString();try{const t=await fetch(a,{redirect:"follow"});if(t.ok)return{text:await t.text(),viaProxy:!1};if(t.status===404)return{text:null,viaProxy:!1,status:404}}catch{}try{const t=await fetch(m+encodeURIComponent(a),{redirect:"follow"});if(t.ok)return{text:await t.text(),viaProxy:!0};if(t.status===404)return{text:null,viaProxy:!0,status:404}}catch{}throw new Error("無法抓取 robots.txt（direct + proxy 都失敗）")}function v(s,a,t){if(t.text===null){s.innerHTML=`
          <div style="padding:1rem;border:1px dashed var(--tw-border);border-radius:8px;background:var(--tw-surface);">
            <p style="font-family:var(--font-mono);font-size:10px;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;color:var(--tw-text-muted);">NO ROBOTS · 404</p>
            <p style="font-size:14px;color:var(--tw-text-secondary);">站台沒有 robots.txt。對 AI bot 是「預設全開放」（好事），但建議建立 robots.txt 明確 allow 10 個 AI bot，避免未來 default 政策改變。</p>
          </div>`;return}const n=u.map(r=>({bot:r,allowed:x(t.text,r)})),o=n.filter(r=>r.allowed).length,e=n.map(r=>`
        <li style="display:flex;align-items:baseline;justify-content:space-between;padding:8px 12px;border:1px solid var(--tw-border);border-radius:6px;background:var(--tw-page-bg);">
          <span style="font-family:var(--font-mono);font-size:13px;color:var(--tw-text-primary);">${r.bot}</span>
          <span style="font-family:var(--font-mono);font-size:11px;color:${r.allowed?"var(--tw-hero-color)":"#b85c5c"};">
            ${r.allowed?"✓ ALLOW":"✗ DISALLOW"}
          </span>
        </li>`).join("");s.innerHTML=`
        <div style="margin-bottom:12px;display:flex;align-items:baseline;justify-content:space-between;flex-wrap:wrap;gap:8px;">
          <p style="font-family:var(--font-mono);font-size:10px;text-transform:uppercase;letter-spacing:0.1em;color:var(--tw-text-muted);">RESULT · ${a}</p>
          <p style="font-family:var(--font-mono);font-size:12px;color:var(--tw-text-primary);">
            <strong style="color:${o>=8?"var(--tw-hero-color)":o>=5?"#c8956d":"#b85c5c"};">${o}</strong> / 10 開放
            ${t.viaProxy?" · via proxy":""}
          </p>
        </div>
        <ul style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px;list-style:none;padding:0;margin:0;">${e}</ul>`}document.addEventListener("DOMContentLoaded",()=>{const s=document.getElementById("robots-scanner-form"),a=document.getElementById("robots-scanner-input"),t=document.getElementById("robots-scanner-result");if(!s||!a||!t)return;async function n(o){t.innerHTML='<p style="font-family:var(--font-mono);font-size:13px;color:var(--tw-text-muted);">掃描中…</p>';try{let e;try{e=new URL(/^https?:\/\//i.test(o)?o:`https://${o}`)}catch{throw new Error("URL 格式錯誤")}const r=await y(e.origin);v(t,e.origin,r)}catch(e){t.innerHTML=`
            <div style="padding:1rem;border:2px dashed var(--tw-border);border-radius:8px;background:var(--tw-surface);">
              <p style="font-family:var(--font-mono);font-size:10px;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;color:var(--tw-text-muted);">SCAN · FAILED</p>
              <p style="font-size:14px;color:var(--tw-text-secondary);">${e.message}</p>
            </div>`}}s.addEventListener("submit",o=>{o.preventDefault();const e=a.value.trim();e&&n(e)}),document.querySelectorAll("[data-sample]").forEach(o=>{o.addEventListener("click",()=>{const e=o.getAttribute("data-sample");e&&(a.value=e,n(e))})})});
