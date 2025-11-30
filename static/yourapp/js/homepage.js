/**
 * SAFE LET STAYS — HOMEPAGE JAVASCRIPT
 * =====================================
 */

document.addEventListener('DOMContentLoaded', () => {
    initHeader();
    initMobileMenu();
    initScrollAnimations();
    initModal();
    initSearchForm();
    initViewToggle();
});

// Sticky Header & Scroll Effects
function initHeader() {
    const header = document.getElementById('header');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
}

// Mobile Menu Toggle
function initMobileMenu() {
    const toggle = document.querySelector('.mobile-menu-toggle');
    const nav = document.getElementById('header-nav');
    const links = document.querySelectorAll('.nav-link');
    const header = document.getElementById('header');
    
    if (!toggle || !nav) return;
    
    // Create overlay element for closing menu
    const overlay = document.createElement('div');
    overlay.className = 'mobile-menu-overlay';
    document.body.appendChild(overlay);
    
    const closeMenu = () => {
        toggle.setAttribute('aria-expanded', 'false');
        toggle.classList.remove('active');
        nav.classList.remove('active');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    };
    
    const openMenu = () => {
        toggle.setAttribute('aria-expanded', 'true');
        toggle.classList.add('active');
        nav.classList.add('active');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    };
    
    toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
        if (isExpanded) {
            closeMenu();
        } else {
            openMenu();
        }
    });
    
    // Close menu when clicking overlay
    overlay.addEventListener('click', closeMenu);
    
    // Close menu when clicking a link
    links.forEach(link => {
        link.addEventListener('click', closeMenu);
    });
    
    // Close menu on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && nav.classList.contains('active')) {
            closeMenu();
        }
    });
}

// Scroll Reveal Animations
function initScrollAnimations() {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.reveal-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

// View Toggle (Grid/List)
function initViewToggle() {
    const toggles = document.querySelectorAll('.view-btn');
    const grid = document.querySelector('.properties-grid');
    
    if (!toggles.length || !grid) return;
    
    toggles.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all
            toggles.forEach(t => t.classList.remove('active'));
            // Add to clicked
            btn.classList.add('active');
            
            const view = btn.dataset.view;
            if (view === 'list') {
                grid.classList.add('list-view');
            } else {
                grid.classList.remove('list-view');
            }
        });
    });
}

// Contact Modal
function initModal() {
    const modal = document.getElementById('contact-modal');
    const openBtns = document.querySelectorAll('#open-contact-modal, #open-contact-modal-empty, #open-contact-modal-cta');
    const closeBtn = document.getElementById('close-contact-modal');
    const form = document.getElementById('contact-form');
    
    if (!modal || !openBtns.length || !closeBtn) return;
    
    const open = () => {
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    };
    
    const close = () => {
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    };
    
    openBtns.forEach(btn => {
        btn.addEventListener('click', open);
    });
    
    closeBtn.addEventListener('click', close);
    
    // Close on outside click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) close();
    });
    
    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.getAttribute('aria-hidden') === 'false') {
            close();
        }
    });
    
    // Handle Form Submission (Mailto builder)
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const name = document.getElementById('contact-name').value;
            const email = document.getElementById('contact-email').value;
            const subject = document.getElementById('contact-subject').value;
            const message = document.getElementById('contact-message').value;
            
            const body = `Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`;
            
            // Get destination email from page context or fallback
            const destEmail = 'hello@safeletstays.co.uk'; // Ideally passed from template
            
            window.location.href = `mailto:${destEmail}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
            
            setTimeout(close, 1000);
        });
    }
}

// Search Form Logic
function initSearchForm() {
    // Handle both the main search form and the filter form on properties page
    const form = document.getElementById('availability-form');
    const filterForm = document.querySelector('.filter-form');
    const summaryContainer = document.getElementById('booking-summary');
    const summaryText = document.getElementById('booking-summary-text');
    const copyBtn = document.getElementById('copy-summary');
    
    // Set min dates to TOMORROW
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const year = tomorrow.getFullYear();
    const month = String(tomorrow.getMonth() + 1).padStart(2, '0');
    const day = String(tomorrow.getDate()).padStart(2, '0');
    const tomorrowStr = `${year}-${month}-${day}`;
    
    const checkIn = document.getElementById('check-in');
    const checkOut = document.getElementById('check-out');
    
    // Ensure min is set to tomorrow
    if (checkIn) checkIn.min = tomorrowStr;
    
    if (checkIn && checkOut) {
        // Initialize date inputs with empty class logic
        [checkIn, checkOut].forEach(input => {
            const updateClass = () => {
                if (!input.value) input.classList.add('date-empty');
                else input.classList.remove('date-empty');
            };
            input.addEventListener('input', updateClass);
            input.addEventListener('change', updateClass);
            updateClass(); // Init
        });

        // Only update checkout min when check-in changes - NO validation alerts here
        checkIn.addEventListener('change', () => {
            if (checkIn.value) {
                // Create date object from input value
                const checkInDate = new Date(checkIn.value);
                
                // Calculate next day for minimum checkout
                const nextDay = new Date(checkInDate);
                nextDay.setDate(checkInDate.getDate() + 1);
                
                // Format as YYYY-MM-DD
                const nextYear = nextDay.getFullYear();
                const nextMonth = String(nextDay.getMonth() + 1).padStart(2, '0');
                const nextDayDate = String(nextDay.getDate()).padStart(2, '0');
                const nextDayStr = `${nextYear}-${nextMonth}-${nextDayDate}`;
                
                checkOut.min = nextDayStr;
                
                // If current checkout is invalid (<= checkin), clear it so user picks a new one
                if (checkOut.value && checkOut.value <= checkIn.value) {
                    checkOut.value = nextDayStr;
                    checkOut.classList.remove('date-empty');
                }
            }
        });

        checkOut.addEventListener('blur', () => {
            if (!checkOut.value && checkIn.value) {
                // If check-in is set and user leaves checkout empty, default to day after check-in
                const checkInDate = new Date(checkIn.value);
                const nextDay = new Date(checkInDate);
                nextDay.setDate(checkInDate.getDate() + 1);
                
                const nextYear = nextDay.getFullYear();
                const nextMonth = String(nextDay.getMonth() + 1).padStart(2, '0');
                const nextDayDate = String(nextDay.getDate()).padStart(2, '0');
                
                checkOut.value = `${nextYear}-${nextMonth}-${nextDayDate}`;
                checkOut.classList.remove('date-empty');
            }
        });
    }
    
    // Form submission validation function
    function validateAndSubmit(e, formElement) {
        const data = new FormData(formElement);
        const checkInStr = data.get('check_in');
        const checkOutStr = data.get('check_out');
        
        // Only validate dates if they were entered
        if (checkInStr) {
            const now = new Date();
            const tomorrowDate = new Date(now);
            tomorrowDate.setDate(tomorrowDate.getDate() + 1);
            const localTomorrowStr = `${tomorrowDate.getFullYear()}-${String(tomorrowDate.getMonth() + 1).padStart(2, '0')}-${String(tomorrowDate.getDate()).padStart(2, '0')}`;

            if (checkInStr < localTomorrowStr) {
                e.preventDefault();
                alert("Check-in date cannot be in the past or today. Please select tomorrow or a future date.");
                if (checkIn) {
                    checkIn.value = localTomorrowStr;
                    checkIn.classList.remove('date-empty');
                    checkIn.dispatchEvent(new Event('change'));
                }
                return false;
            }
        }
        
        if (checkInStr && checkOutStr) {
            const checkInDate = new Date(checkInStr);
            const checkOutDate = new Date(checkOutStr);

            if (checkOutDate <= checkInDate) {
                e.preventDefault();
                alert("Check-out date must be after check-in date.");
                // Calculate next day
                const nextDay = new Date(checkInDate);
                nextDay.setDate(checkInDate.getDate() + 1);
                const nextYear = nextDay.getFullYear();
                const nextMonth = String(nextDay.getMonth() + 1).padStart(2, '0');
                const nextDayDate = String(nextDay.getDate()).padStart(2, '0');
                if (checkOut) {
                    checkOut.value = `${nextYear}-${nextMonth}-${nextDayDate}`;
                    checkOut.classList.remove('date-empty');
                }
                return false;
            }
        }
        
        // If we have the main availability form, require both dates
        if (formElement.id === 'availability-form' && (!checkInStr || !checkOutStr)) {
            e.preventDefault();
            alert("Please select both check-in and check-out dates.");
            return false;
        }
        
        return true;
    }
    
    // Attach validation to main availability form
    if (form) {
        form.addEventListener('submit', (e) => validateAndSubmit(e, form));
    }
    
    // Attach validation to filter form on properties page
    if (filterForm) {
        filterForm.addEventListener('submit', (e) => validateAndSubmit(e, filterForm));
    }
    
    if (copyBtn && summaryText) {
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(summaryText.textContent).then(() => {
                const originalText = copyBtn.textContent;
                copyBtn.textContent = 'Copied!';
                setTimeout(() => copyBtn.textContent = originalText, 2000);
            });
        });
    }
}
