/* ================================
   MOBILE MENU SIDEBAR TOGGLE
   Gestion du menu mobile responsive
   ================================ */

// Fonction pour ouvrir/fermer le sidebar mobile
function toggleMobileSidebar() {
    const sidebar = document.getElementById('mobileSidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (!sidebar || !overlay) return;
    
    sidebar.classList.toggle('open');
    overlay.classList.toggle('active');
    
    // Empêcher le scroll du body quand le menu est ouvert
    if (sidebar.classList.contains('open')) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
}

// Fermer le sidebar automatiquement en cliquant sur un lien (sur mobile)
document.addEventListener('DOMContentLoaded', function() {
    const sidebarLinks = document.querySelectorAll('.sidebar-nav-item');
    
    sidebarLinks.forEach(link => {
        link.addEventListener('click', () => {
            // Seulement sur mobile (écrans < 768px)
            if (window.innerWidth <= 768) {
                const sidebar = document.getElementById('mobileSidebar');
                const overlay = document.querySelector('.sidebar-overlay');
                
                if (sidebar && sidebar.classList.contains('open')) {
                    toggleMobileSidebar();
                }
            }
        });
    });
    
    // Fermer le sidebar si on redimensionne la fenêtre au-dessus de 768px
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            const sidebar = document.getElementById('mobileSidebar');
            const overlay = document.querySelector('.sidebar-overlay');
            
            if (sidebar && sidebar.classList.contains('open')) {
                sidebar.classList.remove('open');
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        }
    });
});
