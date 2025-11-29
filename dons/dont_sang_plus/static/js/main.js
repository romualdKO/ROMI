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
    // CARROUSEL D'IMAGES SIMPLE
    // ================================
    function initSimpleImageCarousel() {
        const carouselImage = document.getElementById('carousel-image');
        if (!carouselImage) {
            console.log('❌ Element carousel-image non trouvé');
            return;
        }

        // Liste des images disponibles avec chemins Django
        const images = [
            'urgence.jpeg',
            'solidarite.jpg', 
            'rupture_stock.jpg',
            'Don de Sang Stylisé.png',
            'don_sang_illustration.svg',
            'don_sang_forum.svg',
            'collecte_sang.svg'
        ];
        
        const imageAlts = [
            'Urgence médicale - Don de sang',
            'Solidarité - Don de sang', 
            'Rupture de stock - Besoin urgent',
            'Don de sang stylisé',
            'Illustration don de sang médecin-patient',
            'Don du sang au forum - Je sauve des vies',
            'Collecte de sang - Scène de donation'
        ];
        
        let currentIndex = 0;

        function changeImage() {
            console.log('🔄 Changement d\'image vers index:', currentIndex + 1);
            
            // Effet de fondu sortant
            carouselImage.style.opacity = '0.3';
            
            setTimeout(() => {
                // Changer l'image après le fondu
                currentIndex = (currentIndex + 1) % images.length;
                
                // Construire le chemin de l'image
                const staticUrl = '/static/images/';
                carouselImage.src = staticUrl + images[currentIndex];
                carouselImage.alt = imageAlts[currentIndex];
                
                console.log('📷 Nouvelle image:', images[currentIndex]);
                
                // Effet de fondu entrant
                carouselImage.style.opacity = '1';
            }, 300);
        }

        // Test initial après 2 secondes pour vérifier que ça fonctionne
        setTimeout(() => {
            console.log('🚀 Test initial du carrousel');
            changeImage();
        }, 2000);

        // Démarrer le carrousel automatique (change toutes les 3 secondes pour être plus visible)
        setInterval(changeImage, 3000);
        
        console.log('✅ Carrousel d\'images simple initialisé avec', images.length, 'images');
        console.log('📋 Images disponibles:', images);
    }

    // ================================
    // INITIALISATION SIMPLIFIÉE
    // ================================
    try {
        initNavbar();
        initScrollAnimations();
        initSimpleImageCarousel();
        console.log('✅ Interface initialisée');
    } catch (error) {
        console.error('Erreur initialisation:', error);
    }

    // Exposer les fonctions globales
    window.DonSangPlus = { showNotification };
});