/* odd.js - Homepage Interactivity */

document.addEventListener('DOMContentLoaded', () => {
    
    // --- HERO NAV INDICES HOVER ---
    const navItems = document.querySelectorAll('.nav-index-item');
    const heroBgLayerA = document.querySelector('.bg-layer.layer-a');

    navItems.forEach(item => {
        item.addEventListener('mouseenter', () => {
            // For mobile, change the main background image
            if (window.innerWidth <= 768) {
                const bgImage = item.getAttribute('data-bg');
                if (bgImage && heroBgLayerA) {
                    heroBgLayerA.src = bgImage;
                }
            }
        });
    });
    // --- REVEAL ON SCROLL ---
    const revealElements = document.querySelectorAll('.reveal');
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, { threshold: 0.1 });

    revealElements.forEach(el => revealObserver.observe(el));

    // --- DYNAMIC IMAGE CYCLE ---
    const dynamicTrigger = document.getElementById('dynamic-trigger');
    const cycleTarget = document.getElementById('cycle-target');
    
    const galleryImages = [
        "/static/images/Home_Gallery4.webp",
        "/static/images/Home_Gallery5.webp",
        "/static/images/Home_Gallery1.webp",
        "/static/images/Home_Gallery2.webp"
    ];
    
    let currentIdx = 0;

    if (dynamicTrigger && cycleTarget) {
        dynamicTrigger.addEventListener('click', () => {
            currentIdx = (currentIdx + 1) % galleryImages.length;
            
            // Subtle fade transition
            cycleTarget.style.opacity = '0';
            setTimeout(() => {
                cycleTarget.style.backgroundImage = `url('${galleryImages[currentIdx]}')`;
                cycleTarget.style.opacity = '1';
            }, 400);
        });
    }

    // --- SMOOTH PARALLAX HERO ---
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const hero = document.querySelector('.hero-section');
        if (hero) {
            hero.style.backgroundPositionY = -(scrolled * 0.3) + 'px';
        }
    });

    // --- ABOUT PAGE IMAGE LOOP ---
    const loopImages = document.querySelectorAll('.loop-img');
    if (loopImages.length > 0) {
        let loopIdx = 0;
        setInterval(() => {
            loopImages[loopIdx].classList.remove('active');
            loopIdx = (loopIdx + 1) % loopImages.length;
            loopImages[loopIdx].classList.add('active');
        }, 3000); // Cycle every 3 seconds
    }

    // --- ABOUT PAGE HERO BLACKOUT ---
    const heroOne = document.querySelector('.hero-one');
    const heroH1 = document.querySelector('.hero-one .hero-h1');

    if (heroOne && heroH1) {
        heroH1.addEventListener('mouseenter', () => {
            heroOne.classList.add('blackout');
        });

        heroH1.addEventListener('mouseleave', () => {
            heroOne.classList.remove('blackout');
        });
    }

    // --- PRODUCT DETAIL PAGE: DYNAMIC CYCLE ---
    const pdpTrigger = document.getElementById('pdp-cycle-trigger');
    const pdpTarget = document.getElementById('pdp-cycle-target');
    
    if (pdpTrigger && pdpTarget) {
        const imagesStr = pdpTarget.getAttribute('data-images');
        const pdpImages = imagesStr ? imagesStr.split(',').filter(url => url.trim() !== "") : [];
        let pdpIdx = 0;

        if (pdpImages.length > 0) {
            pdpTrigger.addEventListener('click', () => {
                pdpIdx = (pdpIdx + 1) % pdpImages.length;
                pdpTarget.classList.add('fade-out');
                setTimeout(() => {
                    pdpTarget.style.backgroundImage = `url('${pdpImages[pdpIdx]}')`;
                    setTimeout(() => {
                        pdpTarget.classList.remove('fade-out');
                    }, 50);
                }, 800);
            });
        }
    }

    // --- PRODUCT DETAIL PAGE: TOGGLES ---
    window.toggleSection = function(header) {
        const item = header.parentElement;
        item.classList.toggle('active');
    };

    // --- MEGA SECTION (EDITORIAL GRID): LINEAR MOUSE TRACKING ---
    const megaWrappers = document.querySelectorAll('.image-wrapper');
    
    megaWrappers.forEach(wrapper => {
        const follower = wrapper.querySelector('.hover-follow');
        
        wrapper.addEventListener('mousemove', (e) => {
            const rect = wrapper.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Linear tracking (very low duration for 'pinned' feel)
            gsap.to(follower, {
                x: x,
                y: y,
                duration: 0.1,
                ease: "none", // Linear movement
                overwrite: true
            });
        });
        
        wrapper.addEventListener('mouseenter', () => {
            gsap.to(follower, {
                opacity: 1,
                duration: 0.3
            });
        });
        
        wrapper.addEventListener('mouseleave', () => {
            gsap.to(follower, {
                opacity: 0,
                duration: 0.3
            });
        });
    });

    // --- EDITORIAL FOOTER: INTERACTIONS ---
    const footerLinks = document.querySelectorAll(".footer-block li");
    footerLinks.forEach((item) => {
        item.addEventListener("mouseenter", () => {
            item.style.transform = "translateX(4px)";
            item.style.transition = "transform 0.3s cubic-bezier(0.22, 1, 0.36, 1)";
        });
        item.addEventListener("mouseleave", () => {
            item.style.transform = "translateX(0px)";
        });
    });

    const footerInputs = document.querySelectorAll(".editorial-footer input");
    footerInputs.forEach((input) => {
        input.addEventListener("focus", () => {
            input.parentElement.style.borderTop = "1px solid rgba(0, 0, 0, 0.8)";
        });
        input.addEventListener("blur", () => {
            input.parentElement.style.borderTop = "1px solid rgba(0, 0, 0, 0.25)";
        });
    });

    // --- FULL-SCREEN NAV OVERLAY TOGGLE ---
    const menuToggle = document.getElementById('menu-toggle');
    const closeMenuToggle = document.getElementById('close-menu-toggle');
    const navOverlay = document.getElementById('nav-overlay');

    if (menuToggle && navOverlay) {
        menuToggle.addEventListener('click', () => {
            navOverlay.classList.add('active');
        });
    }

    if (closeMenuToggle && navOverlay) {
        closeMenuToggle.addEventListener('click', () => {
            navOverlay.classList.remove('active');
        });
    }

    // --- INTERACTIVE SIZE SELECTOR FOR PDP FORM ---
    const sizeBtns = document.querySelectorAll('.size-btn');
    const selectedSizeInput = document.getElementById('selected-size');
    const addToCartBtn = document.getElementById('add-to-cart-btn');

    sizeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Highlight selected size, unhighlight others
            sizeBtns.forEach(b => {
                b.style.background = 'none';
                b.style.color = '#000';
            });
            btn.style.background = '#000';
            btn.style.color = '#fff';

            // Populate hidden form field
            if (selectedSizeInput) {
                selectedSizeInput.value = btn.getAttribute('data-size');
            }

            // Enable Add to Cart button
            if (addToCartBtn) {
                addToCartBtn.disabled = false;
                addToCartBtn.style.opacity = '1';
                addToCartBtn.style.cursor = 'pointer';
                addToCartBtn.textContent = 'ADD TO CART';
            }
        });
    });

    // Form submit check
    const cartForm = document.getElementById('add-cart-form');
    if (cartForm && addToCartBtn) {
        // Disable initially if sizes are present
        if (sizeBtns.length > 0) {
            addToCartBtn.disabled = true;
            addToCartBtn.style.opacity = '0.45';
            addToCartBtn.style.cursor = 'not-allowed';
            addToCartBtn.textContent = 'SELECT A SIZE';
        }

        cartForm.addEventListener('submit', (e) => {
            if (selectedSizeInput && selectedSizeInput.value === '') {
                e.preventDefault();
                const selector = document.getElementById('size-selector');
                if (selector) {
                    selector.style.outline = '1px solid red';
                    setTimeout(() => selector.style.outline = '', 1200);
                }
            }
        });
    }
});
