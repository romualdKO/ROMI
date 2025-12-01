/**
 * Don Sang Plus - Mobile Menu Handler
 * Gestion du menu mobile et de la sidebar responsive
 */

(function() {
    'use strict';

    // Vérifier si on est sur mobile
    function isMobile() {
        return window.innerWidth <= 768;
    }

    // Initialiser le menu mobile
    function initMobileMenu() {
        // Créer le bouton hamburger s'il n'existe pas
        if (!document.querySelector('.mobile-menu-btn') && isMobile()) {
            const mobileBtn = document.createElement('button');
            mobileBtn.className = 'mobile-menu-btn';
            mobileBtn.innerHTML = '<i class="fas fa-bars"></i>';
            mobileBtn.setAttribute('aria-label', 'Ouvrir le menu');
            document.body.appendChild(mobileBtn);

            // Créer l'overlay
            const overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            document.body.appendChild(overlay);

            // Event listeners
            mobileBtn.addEventListener('click', toggleSidebar);
            overlay.addEventListener('click', closeSidebar);
        }
    }

    // Toggle sidebar
    function toggleSidebar() {
        const sidebar = document.querySelector('.modern-sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        const btn = document.querySelector('.mobile-menu-btn');

        if (sidebar && overlay && btn) {
            const isActive = sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
            
            // Changer l'icône
            btn.innerHTML = isActive 
                ? '<i class="fas fa-times"></i>' 
                : '<i class="fas fa-bars"></i>';
            
            // Accessibility
            btn.setAttribute('aria-label', isActive ? 'Fermer le menu' : 'Ouvrir le menu');
            btn.setAttribute('aria-expanded', isActive);
            
            // Empêcher le scroll du body quand menu ouvert
            document.body.style.overflow = isActive ? 'hidden' : '';
        }
    }

    // Fermer sidebar
    function closeSidebar() {
        const sidebar = document.querySelector('.modern-sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        const btn = document.querySelector('.mobile-menu-btn');

        if (sidebar && overlay && btn) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
            btn.innerHTML = '<i class="fas fa-bars"></i>';
            btn.setAttribute('aria-label', 'Ouvrir le menu');
            btn.setAttribute('aria-expanded', 'false');
            document.body.style.overflow = '';
        }
    }

    // Fermer la sidebar sur click d'un lien (mobile)
    function handleSidebarLinks() {
        const sidebarLinks = document.querySelectorAll('.modern-sidebar a');
        sidebarLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (isMobile()) {
                    closeSidebar();
                }
            });
        });
    }

    // Gérer le redimensionnement de la fenêtre
    let resizeTimeout;
    function handleResize() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            const mobileBtn = document.querySelector('.mobile-menu-btn');
            const overlay = document.querySelector('.sidebar-overlay');
            
            if (isMobile()) {
                // Mode mobile
                initMobileMenu();
            } else {
                // Mode desktop - retirer les éléments mobiles
                if (mobileBtn) mobileBtn.remove();
                if (overlay) overlay.remove();
                
                const sidebar = document.querySelector('.modern-sidebar');
                if (sidebar) {
                    sidebar.classList.remove('active');
                }
                document.body.style.overflow = '';
            }
        }, 250);
    }

    // Gérer l'orientation de l'appareil
    function handleOrientation() {
        if (isMobile()) {
            closeSidebar();
        }
    }

    // Améliorer la navbar mobile Bootstrap
    function enhanceBootstrapNavbar() {
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');

        if (navbarToggler && navbarCollapse) {
            // Fermer le menu au click d'un lien
            const navLinks = navbarCollapse.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                link.addEventListener('click', () => {
                    if (isMobile() && navbarCollapse.classList.contains('show')) {
                        navbarToggler.click();
                    }
                });
            });

            // Fermer au click en dehors
            document.addEventListener('click', (e) => {
                if (isMobile() && 
                    navbarCollapse.classList.contains('show') && 
                    !navbarCollapse.contains(e.target) && 
                    !navbarToggler.contains(e.target)) {
                    navbarToggler.click();
                }
            });
        }
    }

    // Gérer les dropdowns sur mobile
    function handleMobileDropdowns() {
        const dropdowns = document.querySelectorAll('.dropdown');
        
        dropdowns.forEach(dropdown => {
            const toggle = dropdown.querySelector('.dropdown-toggle');
            const menu = dropdown.querySelector('.dropdown-menu');
            
            if (toggle && menu && isMobile()) {
                toggle.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Fermer les autres dropdowns
                    document.querySelectorAll('.dropdown-menu.show').forEach(m => {
                        if (m !== menu) m.classList.remove('show');
                    });
                    
                    menu.classList.toggle('show');
                });
            }
        });
    }

    // Smooth scroll pour les ancres
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const href = this.getAttribute('href');
                if (href !== '#' && href !== '') {
                    e.preventDefault();
                    const target = document.querySelector(href);
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                        
                        // Fermer le menu mobile si ouvert
                        if (isMobile()) {
                            closeSidebar();
                        }
                    }
                }
            });
        });
    }

    // Gérer le focus trap dans le menu mobile
    function handleFocusTrap() {
        const sidebar = document.querySelector('.modern-sidebar');
        if (!sidebar) return;

        const focusableElements = sidebar.querySelectorAll(
            'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        sidebar.addEventListener('keydown', (e) => {
            if (e.key !== 'Tab' || !sidebar.classList.contains('active')) return;

            if (e.shiftKey) {
                // Shift + Tab
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else {
                // Tab
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        });
    }

    // Escape key pour fermer le menu
    function handleEscapeKey() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeSidebar();
                
                // Fermer aussi les dropdowns
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                });
            }
        });
    }

    // Détection du swipe pour fermer le menu
    function initSwipeGestures() {
        let touchStartX = 0;
        let touchEndX = 0;

        const sidebar = document.querySelector('.modern-sidebar');
        if (!sidebar) return;

        sidebar.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        sidebar.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, { passive: true });

        function handleSwipe() {
            const swipeThreshold = 50;
            const diff = touchStartX - touchEndX;

            // Swipe vers la gauche pour fermer
            if (diff > swipeThreshold && sidebar.classList.contains('active')) {
                closeSidebar();
            }
        }
    }

    // Améliorer les tables responsive
    function enhanceResponsiveTables() {
        const tables = document.querySelectorAll('.modern-table');
        
        tables.forEach(table => {
            if (!table.closest('.modern-table-container')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'modern-table-container';
                table.parentNode.insertBefore(wrapper, table);
                wrapper.appendChild(table);
            }
        });
    }

    // Lazy loading pour les images
    function initLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                            observer.unobserve(img);
                        }
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    // Améliorer la performance sur mobile
    function optimizePerformance() {
        // Utiliser passive listeners pour le scroll
        document.addEventListener('scroll', () => {
            // Performance optimizations
        }, { passive: true });

        // Débouncer le resize
        window.addEventListener('resize', handleResize);
    }

    // Ajouter des classes utilitaires
    function addUtilityClasses() {
        // Ajouter la classe mobile/desktop
        const updateDeviceClass = () => {
            document.body.classList.toggle('is-mobile', isMobile());
            document.body.classList.toggle('is-desktop', !isMobile());
        };
        
        updateDeviceClass();
        window.addEventListener('resize', updateDeviceClass);
    }

    // Initialisation
    function init() {
        // Attendre que le DOM soit chargé
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        console.log('🚀 Initialisation du menu mobile...');

        // Initialiser tous les modules
        initMobileMenu();
        handleSidebarLinks();
        enhanceBootstrapNavbar();
        handleMobileDropdowns();
        initSmoothScroll();
        handleFocusTrap();
        handleEscapeKey();
        initSwipeGestures();
        enhanceResponsiveTables();
        initLazyLoading();
        optimizePerformance();
        addUtilityClasses();

        // Gérer les changements d'orientation
        window.addEventListener('orientationchange', handleOrientation);

        console.log('✅ Menu mobile initialisé');
    }

    // Démarrer l'initialisation
    init();

})();
