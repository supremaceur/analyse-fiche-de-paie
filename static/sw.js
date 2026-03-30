// Service worker minimal pour PaySlip Analyzer PWA
// Nécessaire pour que le navigateur propose "Installer l'application"

self.addEventListener('install', function(e) {
    self.skipWaiting();
});

self.addEventListener('activate', function(e) {
    e.waitUntil(self.clients.claim());
});

// Intercepter les requêtes vers le manifest Streamlit et servir le nôtre
self.addEventListener('fetch', function(e) {
    var url = e.request.url;
    // Si le navigateur demande un manifest qui n'est pas le nôtre, rediriger
    if (url.indexOf('manifest.json') !== -1 && url.indexOf('app/static') === -1) {
        e.respondWith(fetch(self.registration.scope + 'app/static/manifest.json'));
        return;
    }
    // Tout le reste passe normalement
});
