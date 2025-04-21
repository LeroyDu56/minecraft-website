/**
 * Main JavaScript file for GeoMC website
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navbar = document.querySelector('.navbar');
    
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            console.log('Hamburger clicked'); // Pour le débogage
            navbar.classList.toggle('mobile-open');
        });
    }
    
    // Close mobile menu when clicking on links
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navbar.classList.remove('mobile-open');
            if (mobileMenuToggle) {
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
            }
        });
    });
    
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