/* ============================================================
   METROPOLITAN UNIVERSITY — PLAIN JAVASCRIPT
   Converted from React (TSX) hooks and component logic
============================================================ */

// ============================================================
// 1. NAVIGATION — scroll state & mobile menu toggle
// ============================================================
(function () {
  const nav = document.getElementById('main-nav');
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  const iconMenu = document.getElementById('icon-menu');
  const iconX = document.getElementById('icon-x');
  let mobileOpen = false;

  if (nav && mobileMenuBtn && mobileMenu && iconMenu && iconX) {
    // Scroll: toggle .scrolled class after 90% of viewport height
    window.addEventListener('scroll', function () {
      if (window.scrollY > window.innerHeight * 0.9) {
        nav.classList.add('scrolled');
      } else {
        nav.classList.remove('scrolled');
      }
    }, { passive: true });

    // Hamburger toggle
    mobileMenuBtn.addEventListener('click', function () {
      mobileOpen = !mobileOpen;
      mobileMenu.classList.toggle('open', mobileOpen);
      iconMenu.style.display = mobileOpen ? 'none' : 'block';
      iconX.style.display = mobileOpen ? 'block' : 'none';
      mobileMenuBtn.setAttribute('aria-expanded', String(mobileOpen));
    });

    // Close mobile menu when any nav link is clicked
    document.querySelectorAll('.mobile-nav-link').forEach(function (link) {
      link.addEventListener('click', function () {
        mobileOpen = false;
        mobileMenu.classList.remove('open');
        iconMenu.style.display = 'block';
        iconX.style.display = 'none';
        mobileMenuBtn.setAttribute('aria-expanded', 'false');
      });
    });
  }
})();

// ============================================================
// 2. HERO — letter-by-letter entrance animation
// ============================================================
(function () {
  var heroTitle = document.getElementById('hero-title');
  var heroTagline = document.getElementById('hero-tagline');
  
  if (heroTitle && heroTagline) {
    var word = 'Metropolitan';

    // Build individual letter spans
    word.split('').forEach(function (char, i) {
      var span = document.createElement('span');
      span.className = 'letter';
      span.textContent = char === ' ' ? '\u00A0' : char;
      span.style.transitionDelay = (i * 80) + 'ms';
      heroTitle.appendChild(span);
    });

    // Trigger animation after a brief delay (mirrors React useEffect 100ms)
    setTimeout(function () {
      heroTitle.classList.add('loaded');
      heroTagline.classList.add('loaded');
    }, 100);
  }
})();

// ============================================================
// 3. SCROLL REVEAL — IntersectionObserver for .reveal elements
//    Mirrors the useScrollAnimation() React hook
// ============================================================
(function () {
  var revealObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });

  document.querySelectorAll('.reveal').forEach(function (el) {
    revealObserver.observe(el);
  });
})();

// ============================================================
// 4. ANIMATED COUNTERS — mirrors useCounter() React hook
//    Easing: cubic ease-out  (1 - (1-t)^3)
// ============================================================
(function () {
  function animateCounter(el) {
    var target = parseInt(el.getAttribute('data-target'), 10);
    var duration = 2000;
    var startTime = null;

    function step(timestamp) {
      if (!startTime) startTime = timestamp;
      var progress = Math.min((timestamp - startTime) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.floor(eased * target).toLocaleString();
      if (progress < 1) {
        requestAnimationFrame(step);
      }
    }

    requestAnimationFrame(step);
  }

  var counterObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        counterObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });

  document.querySelectorAll('.counter').forEach(function (el) {
    counterObserver.observe(el);
  });
})();
