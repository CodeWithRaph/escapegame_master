// filepath: /home/raphael/Desktop/escapegame_master/static/chrono.js
// Minimal chrono helper. Templates will set window.__chrono_start_epoch when needed.
window.Chrono = (function(){
  return {
    setServerStart: function(epochSeconds){ window.__chrono_start_epoch = epochSeconds; },
    clear: function(){ delete window.__chrono_start_epoch; }
  };
})();
