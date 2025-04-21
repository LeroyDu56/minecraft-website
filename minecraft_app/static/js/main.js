/**
 * Main JavaScript file for GeoMC website
 */

document.addEventListener('DOMContentLoaded', function() {
    // Ajoutons un script de débogage pour voir si le document est bien chargé
    console.log('DOM chargé - Script initialisé');
    
    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navbar = document.querySelector('.navbar');
    
    if (mobileMenuToggle) {
        console.log('Bouton hamburger trouvé');
        
        // Solution directe et simple pour la gestion du clic
        mobileMenuToggle.onclick = function() {
            console.log('Clic sur hamburger détecté');
            navbar.classList.toggle('mobile-open');
            console.log('État de la classe mobile-open:', navbar.classList.contains('mobile-open'));
        };
    } else {
        console.error('Bouton hamburger non trouvé!');
    }
    
    // Close mobile menu when clicking on links
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navbar.classList.remove('mobile-open');
        });
    });
    
    // User dropdown menu toggle
    const userDropdownToggle = document.getElementById('user-dropdown-toggle');
    const userDropdownMenu = document.getElementById('user-dropdown-menu');
    
    if (userDropdownToggle && userDropdownMenu) {
        // Toggle dropdown when clicking on avatar
        userDropdownToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdownMenu.classList.toggle('active');
        });
        
        // Close dropdown when clicking elsewhere
        document.addEventListener('click', function() {
            if (userDropdownMenu.classList.contains('active')) {
                userDropdownMenu.classList.remove('active');
            }
        });
        
        // Prevent dropdown from closing when clicking inside it
        userDropdownMenu.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
    
    // Handle message notifications
    const messageCloseButtons = document.querySelectorAll('.message-close');
    if (messageCloseButtons.length > 0) {
        messageCloseButtons.forEach(button => {
            button.addEventListener('click', function() {
                const message = this.parentElement;
                message.style.opacity = '0';
                setTimeout(() => {
                    message.remove();
                }, 300);
            });
        });
        
        // Auto-hide messages after 5 seconds
        setTimeout(() => {
            document.querySelectorAll('.message').forEach(message => {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.remove();
                }, 300);
            });
        }, 5000);
    }
    
    // Copy server IP functionality
    const copyIpButton = document.getElementById('copy-ip');
    if (copyIpButton) {
        copyIpButton.addEventListener('click', function() {
            const serverIP = 'play.geomc.fr';
            navigator.clipboard.writeText(serverIP).then(function() {
                // Change button text temporarily
                const btn = document.getElementById('copy-ip');
                const originalText = btn.textContent;
                btn.textContent = 'IP Copied!';
                setTimeout(function() {
                    btn.textContent = originalText;
                }, 2000);
            });
        });
    }
    
    // FAQ Toggle functionality
    const faqQuestions = document.querySelectorAll('.faq-question');
    if (faqQuestions.length > 0) {
        faqQuestions.forEach(question => {
            question.addEventListener('click', function() {
                const answer = this.nextElementSibling;
                
                // Toggle display
                if (answer.style.display === 'block') {
                    answer.style.display = 'none';
                    this.querySelector('i').classList.replace('fa-chevron-up', 'fa-chevron-down');
                } else {
                    answer.style.display = 'block';
                    this.querySelector('i').classList.replace('fa-chevron-down', 'fa-chevron-up');
                }
            });
        });
        
        // Initially hide all answers
        document.querySelectorAll('.faq-answer').forEach(answer => {
            answer.style.display = 'none';
        });
    }
    
    // Add active class to current page in navigation
    const currentLocation = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-links a');
    
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (currentLocation === href || (href !== '/' && currentLocation.includes(href))) {
            item.classList.add('active');
        }
    });
});