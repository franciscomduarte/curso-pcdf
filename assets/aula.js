/* =========================================================================
   Curso PCDF — comportamentos compartilhados das aulas
   1) barra de progresso de rolagem
   2) reveal-on-scroll
   3) realçador de sintaxe (Python) sobre blocos <pre data-lang="python">
   ========================================================================= */

// 1) Barra de progresso ----------------------------------------------------
(function () {
  const barra = document.getElementById('progresso');
  if (!barra) return;
  const atualizar = () => {
    const h = document.documentElement;
    const total = h.scrollHeight - h.clientHeight;
    barra.style.width = (total > 0 ? (h.scrollTop / total) * 100 : 0) + '%';
  };
  document.addEventListener('scroll', atualizar, { passive: true });
  atualizar();
})();

// 2) Reveal on scroll ------------------------------------------------------
(function () {
  const alvos = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window) || !alvos.length) {
    alvos.forEach(el => el.classList.add('visivel'));
    return;
  }
  const obs = new IntersectionObserver((entradas) => {
    entradas.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visivel'); obs.unobserve(e.target); } });
  }, { threshold: 0.12 });
  alvos.forEach(el => obs.observe(el));
})();

// 3) Realçador de sintaxe Python ------------------------------------------
(function () {
  const KEYWORDS = new Set(('def class return if elif else for while in not and or is None True False '
    + 'import from as with try except finally raise pass break continue lambda global nonlocal yield '
    + 'assert del async await match case').split(' '));

  function escapar(t) {
    return t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // tokeniza uma linha já escapada, respeitando strings e comentários
  function realcarLinha(linha) {
    let out = '';
    let i = 0;
    while (i < linha.length) {
      const resto = linha.slice(i);

      // comentário até o fim da linha
      const com = resto.match(/^#.*/);
      if (com) { out += `<span class="tok-com">${com[0]}</span>`; break; }

      // strings (aspas simples/duplas, incl. f-strings) — versão simples de aula
      const str = resto.match(/^(?:[frbFRB]{0,2})(?:"[^"]*"|'[^']*')/);
      if (str) { out += `<span class="tok-str">${str[0]}</span>`; i += str[0].length; continue; }

      // decoradores
      const dec = resto.match(/^@[A-Za-z_][\w.]*/);
      if (dec) { out += `<span class="tok-dec">${dec[0]}</span>`; i += dec[0].length; continue; }

      // números
      const num = resto.match(/^\d+(?:\.\d+)?/);
      if (num) { out += `<span class="tok-num">${num[0]}</span>`; i += num[0].length; continue; }

      // identificadores / palavras
      const id = resto.match(/^[A-Za-z_]\w*/);
      if (id) {
        const palavra = id[0];
        if (KEYWORDS.has(palavra)) out += `<span class="tok-kw">${palavra}</span>`;
        else if (palavra === 'self' || palavra === 'cls') out += `<span class="tok-self">${palavra}</span>`;
        else if (linha.slice(i + palavra.length).match(/^\s*\(/) || linha.slice(0, i).match(/\bdef\s+$/))
          out += `<span class="tok-fn">${palavra}</span>`;
        else out += palavra;
        i += palavra.length; continue;
      }

      // qualquer outro caractere
      out += linha[i]; i += 1;
    }
    return out;
  }

  document.querySelectorAll('pre[data-lang="python"]').forEach(pre => {
    const bruto = pre.textContent.replace(/\s+$/, '');
    const linhas = escapar(bruto).split('\n');
    pre.innerHTML = linhas.map(realcarLinha).join('\n');
  });
})();

// 4) Mermaid — só quando a página carrega a biblioteca --------------------
(function () {
  if (!window.mermaid) return;
  const semAnim = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  window.mermaid.initialize({
    startOnLoad: true,
    securityLevel: 'strict',
    theme: 'base',
    themeVariables: {
      fontFamily: 'Inter, system-ui, sans-serif',
      primaryColor: '#0F1C36',
      primaryTextColor: '#EAF0FA',
      primaryBorderColor: '#B8892B',
      lineColor: '#B8892B',
      secondaryColor: '#1C7C74',
      tertiaryColor: '#F2EEE3',
      noteBkgColor: '#F2EEE3',
      noteTextColor: '#0F1C36'
    },
    flowchart: { curve: semAnim ? 'linear' : 'basis' }
  });
})();
