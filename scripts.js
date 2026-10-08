document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('#navMenu');
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('main section[id]');
    const header = document.querySelector('.site-header');

    if (!menuToggle || !navMenu) {
        return;
    }

    const closeMenu = () => {
        menuToggle.setAttribute('aria-expanded', 'false');
        menuToggle.setAttribute('aria-label', 'Mở menu');
        navMenu.classList.remove('open');
    };

    menuToggle.addEventListener('click', () => {
        const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true';
        menuToggle.setAttribute('aria-expanded', String(!isExpanded));
        menuToggle.setAttribute('aria-label', isExpanded ? 'Mở menu' : 'Đóng menu');
        navMenu.classList.toggle('open', !isExpanded);
    });

    navLinks.forEach((link) => {
        link.addEventListener('click', () => {
            closeMenu();
            navLinks.forEach((navLink) => navLink.classList.remove('active'));
            link.classList.add('active');
        });
    });

    const updateActiveLink = () => {
        const scrollPosition = window.scrollY + (header?.offsetHeight ?? 0) + 40;
        let activeSection = sections[0];

        sections.forEach((section) => {
            if (section.offsetTop <= scrollPosition) {
                activeSection = section;
            }
        });

        if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2) {
            activeSection = sections[sections.length - 1];
        }

        navLinks.forEach((link) => {
            link.classList.toggle('active', link.hash === `#${activeSection?.id}`);
        });
    };

    window.addEventListener('scroll', updateActiveLink, { passive: true });
    updateActiveLink();

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeMenu();
        }
    });
});
