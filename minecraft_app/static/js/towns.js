/**
 * JavaScript for the Towns page
 * Handles filtering, searching, and sorting of towns
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const townSearch = document.getElementById('town-search');
    const nationFilter = document.getElementById('nation-filter');
    const sortBy = document.getElementById('sort-by');
    const townCards = document.querySelectorAll('.town-card');
    
    // Search functionality
    if (townSearch) {
        townSearch.addEventListener('input', function() {
            filterTowns();
        });
    }
    
    // Nation filter
    if (nationFilter) {
        nationFilter.addEventListener('change', function() {
            filterTowns();
        });
    }
    
    // Sort functionality
    if (sortBy) {
        sortBy.addEventListener('change', function() {
            sortTowns(this.value);
        });
    }
    
    /**
     * Filter towns based on search input and nation filter
     */
    function filterTowns() {
        const searchTerm = townSearch.value.toLowerCase();
        const nationValue = nationFilter.value.toLowerCase();
        
        townCards.forEach(card => {
            const townName = card.querySelector('.town-name').textContent.toLowerCase();
            const nationElement = card.querySelector('.town-nation');
            const nationName = nationElement ? nationElement.textContent.toLowerCase() : '';
            const isIndependent = nationElement && nationElement.classList.contains('town-independent');
            
            // Check if matches search term
            const matchesSearch = townName.includes(searchTerm);
            
            // Check if matches nation filter
            let matchesNation = true;
            if (nationValue) {
                if (nationValue === 'no-nation') {
                    matchesNation = isIndependent;
                } else {
                    matchesNation = nationName === nationValue;
                }
            }
            
            // Show or hide based on filters
            if (matchesSearch && matchesNation) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    /**
     * Sort towns based on selected criteria
     * @param {string} criteria - The sorting criteria
     */
    function sortTowns(criteria) {
        const townsContainer = document.querySelector('.towns-grid');
        const towns = Array.from(townCards);
        
        towns.sort((a, b) => {
            if (criteria === 'name') {
                const nameA = a.querySelector('.town-name').textContent.toLowerCase();
                const nameB = b.querySelector('.town-name').textContent.toLowerCase();
                return nameA.localeCompare(nameB);
            } 
            else if (criteria === 'residents') {
                const residentsA = parseInt(a.querySelector('.info-item:nth-child(2) .info-value').textContent);
                const residentsB = parseInt(b.querySelector('.info-item:nth-child(2) .info-value').textContent);
                return residentsB - residentsA; // Highest first
            }
            else if (criteria === 'founded') {
                const foundedA = new Date(a.querySelector('.info-item:nth-child(3) .info-value').textContent);
                const foundedB = new Date(b.querySelector('.info-item:nth-child(3) .info-value').textContent);
                return foundedA - foundedB; // Oldest first
            }
            
            return 0;
        });
        
        // Reorder DOM elements
        towns.forEach(town => {
            townsContainer.appendChild(town);
        });
    }
    
    // Initialize with default sort (residents)
    if (sortBy && sortBy.value) {
        sortTowns(sortBy.value);
    }
    
    // Pagination (Example functionality)
    const pageLinks = document.querySelectorAll('.page-numbers a');
    const prevPageLink = document.querySelector('.page-nav:first-child');
    const nextPageLink = document.querySelector('.page-nav:last-child');
    
    pageLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all page links
            pageLinks.forEach(pageLink => {
                pageLink.classList.remove('active');
            });
            
            // Add active class to the clicked link
            this.classList.add('active');
            
            // Here you would typically load the page data via AJAX
            // For demo purposes, we're just updating the UI
            
            // Update prev/next buttons state
            if (this.textContent === '1') {
                prevPageLink.classList.add('disabled');
            } else {
                prevPageLink.classList.remove('disabled');
            }
            
            if (this.textContent === '8') { // Assuming 8 is the last page
                nextPageLink.classList.add('disabled');
            } else {
                nextPageLink.classList.remove('disabled');
            }
        });
    });
    
    // Previous page button
    if (prevPageLink) {
        prevPageLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (this.classList.contains('disabled')) {
                return;
            }
            
            const activePage = document.querySelector('.page-numbers a.active');
            const currentPage = parseInt(activePage.textContent);
            
            if (currentPage > 1) {
                const prevPage = document.querySelector(`.page-numbers a:nth-child(${currentPage - 1})`);
                if (prevPage) {
                    prevPage.click();
                }
            }
        });
    }
    
    // Next page button
    if (nextPageLink) {
        nextPageLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (this.classList.contains('disabled')) {
                return;
            }
            
            const activePage = document.querySelector('.page-numbers a.active');
            const currentPage = parseInt(activePage.textContent);
            
            const nextPage = document.querySelector(`.page-numbers a:nth-child(${currentPage + 1})`);
            if (nextPage) {
                nextPage.click();
            }
        });
    }
});