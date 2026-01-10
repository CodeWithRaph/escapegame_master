window.Chrono = (function(){
  let rafId = null;
  let el = null;
  let startMs = null;

  function toStartMs(raw){
    if (raw === undefined || raw === null) return null;
    const num = Number(raw);
    if (!Number.isFinite(num)) return null;
    // detect seconds vs milliseconds
    return (Math.abs(num) > 1e12) ? num : num * 1000;
  }

  function pad(n){ return String(n).padStart(2,'0'); }

  function renderNow(){
    if (!el || startMs === null) return;
    const elapsedMs = Math.max(0, Date.now() - startMs);
    const totalSec = Math.floor(elapsedMs / 1000);
    const hrs = Math.floor(totalSec / 3600);
    const mins = Math.floor((totalSec % 3600) / 60);
    const secs = totalSec % 60;
    el.textContent = pad(hrs) + ':' + pad(mins) + ':' + pad(secs);
  }

  function tick(){
    renderNow();
    rafId = requestAnimationFrame(tick);
  }

  return {
    setServerStart: function(epoch){
      startMs = toStartMs(epoch);
      // keep a copy on window for backward-compatibility
      try{ window.__chrono_start_epoch = epoch; }catch(e){}
    },
    clear: function(){
      startMs = null;
      try{ delete window.__chrono_start_epoch; }catch(e){}
    },
    attach: function(elementId){
      el = document.getElementById(elementId);
      if (!el) return;
      // prefer global value, else data-start attribute on element
      if (window.__chrono_start_epoch && startMs === null){
        startMs = toStartMs(window.__chrono_start_epoch);
      } else if (!window.__chrono_start_epoch && el.dataset && el.dataset.start){
        startMs = toStartMs(el.dataset.start);
        try{ window.__chrono_start_epoch = el.dataset.start; }catch(e){}
      }
      renderNow();
      if (rafId === null) tick();
    },
    detach: function(){
      if (rafId !== null){ cancelAnimationFrame(rafId); rafId = null; }
      el = null;
    },
    formatFromEpoch: function(epoch){
      const sMs = toStartMs(epoch);
      if (sMs === null) return '00:00:00';
      const elapsedMs = Math.max(0, Date.now() - sMs);
      const totalSec = Math.floor(elapsedMs / 1000);
      const hrs = Math.floor(totalSec / 3600);
      const mins = Math.floor((totalSec % 3600) / 60);
      const secs = totalSec % 60;
      return pad(hrs) + ':' + pad(mins) + ':' + pad(secs);
    }
  };
})();
