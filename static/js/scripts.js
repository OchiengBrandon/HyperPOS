// Theme Toggle T
const themeToggle = document.getElementById('themeToggle');
const themeIcon = themeToggle.querySelector('i');
const body = document.body;

// Check for saved theme preference or use device preference
const savedTheme = localStorage.getItem('theme') || 
                    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

// Apply the saved theme
if (savedTheme === 'dark') {
    body.setAttribute('data-theme', 'dark');
    themeIcon.classList.replace('fa-moon', 'fa-sun');
}

themeToggle.addEventListener('click', () => {
    if (body.getAttribute('data-theme') === 'dark') {
        body.removeAttribute('data-theme');
        themeIcon.classList.replace('fa-sun', 'fa-moon');
        localStorage.setItem('theme', 'light');
    } else {
        body.setAttribute('data-theme', 'dark');
        themeIcon.classList.replace('fa-moon', 'fa-sun');
        localStorage.setItem('theme', 'dark');
    }
});

// Mobile Menu
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const mobileMenu = document.getElementById('mobileMenu');
const menuIcon = mobileMenuBtn.querySelector('i');

mobileMenuBtn.addEventListener('click', () => {
    mobileMenu.classList.toggle('active');
    if (mobileMenu.classList.contains('active')) {
        menuIcon.classList.replace('fa-bars', 'fa-times');
    } else {
        menuIcon.classList.replace('fa-times', 'fa-bars');
    }
});

// Close mobile menu when clicking on a link
const mobileMenuLinks = mobileMenu.querySelectorAll('a');
mobileMenuLinks.forEach(link => {
    link.addEventListener('click', () => {
        mobileMenu.classList.remove('active');
        menuIcon.classList.replace('fa-times', 'fa-bars');
    });
});

// Testimonial Slider
const testimonialTrack = document.getElementById('testimonialTrack');
const testimonials = testimonialTrack.querySelectorAll('.testimonial');
const prevBtn = document.getElementById('prevTestimonial');
const nextBtn = document.getElementById('nextTestimonial');
const dots = document.getElementById('testimonialDots').querySelectorAll('.testimonial-dot');

let currentIndex = 0;
const slideWidth = 100; // 100%

function goToSlide(index) {
    if (index < 0) {
        index = testimonials.length - 1;
    } else if (index >= testimonials.length) {
        index = 0;
    }

    currentIndex = index;
    testimonialTrack.style.transform = `translateX(-${slideWidth * currentIndex}%)`;

    // Update dots
    dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === currentIndex);
    });
}

prevBtn.addEventListener('click', () => {
    goToSlide(currentIndex - 1);
});

nextBtn.addEventListener('click', () => {
    goToSlide(currentIndex + 1);
});

// Add click event to dots
dots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
        goToSlide(index);
    });
});

// Auto slide every 5 seconds
setInterval(() => {
    goToSlide(currentIndex + 1);
}, 5000);

// Hero Image 3D Effect
const heroImage = document.getElementById('heroImage');

document.addEventListener('mousemove', (e) => {
    const xAxis = (window.innerWidth / 2 - e.pageX) / 25;
    const yAxis = (window.innerHeight / 2 - e.pageY) / 25;

    heroImage.style.transform = `perspective(1000px) rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
});

// Reset transform when mouse leaves
document.addEventListener('mouseleave', () => {
    heroImage.style.transform = 'perspective(1000px) rotateY(0deg) rotateX(0deg)';
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();

        const targetId = this.getAttribute('href');
        if (targetId === '#') return;

        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 80,
                behavior: 'smooth'
            });
        }
    });
});

// Animation on scroll
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.feature-card, .pricing-card, .step, .section-header');

    elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;

        if (elementPosition < screenPosition) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
};

// Set initial state for animated elements
document.querySelectorAll('.feature-card, .pricing-card, .step, .section-header').forEach(element => {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
});

window.addEventListener('scroll', animateOnScroll);
window.addEventListener('load', animateOnScroll);