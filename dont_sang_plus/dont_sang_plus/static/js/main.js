document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // ================================
    // FONCTIONS PRINCIPALES SIMPLIFIÉES
    // ================================
    
    // Navbar dynamique
    function initNavbar() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // Animations au scroll
    function initScrollAnimations() {
        const animatedElements = document.querySelectorAll('.animate-on-scroll:not([data-animated])');
        
        if (animatedElements.length === 0) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                    entry.target.setAttribute('data-animated', 'true');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        animatedElements.forEach(el => observer.observe(el));
    }

    // Notifications
    function showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        notification.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), duration);
    }

    // ================================
    // INITIALISATION SIMPLIFIÉE
    // ================================
    try {
        initNavbar();
        initScrollAnimations();
        console.log('✅ Interface initialisée');
    } catch (error) {
        console.error('Erreur initialisation:', error);
    }

    // Exposer les fonctions globales
    window.DonSangPlus = { showNotification };
});