// Main JavaScript file for YouTube Slide Extractor

// Show tooltips
$(function () {
    $('[data-toggle="tooltip"]').tooltip();
});

// Form validation enhancement
function validateYoutubeUrl(url) {
    var regExp = /^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})$/;
    return regExp.test(url);
}

// Add custom form validation when script loads
document.addEventListener('DOMContentLoaded', function() {
    const urlInput = document.getElementById('youtube_url');
    if (urlInput) {
        urlInput.addEventListener('blur', function() {
            if (this.value && !validateYoutubeUrl(this.value)) {
                this.classList.add('is-invalid');
                if (!this.nextElementSibling || !this.nextElementSibling.classList.contains('invalid-feedback')) {
                    const feedback = document.createElement('div');
                    feedback.classList.add('invalid-feedback');
                    feedback.textContent = 'Please enter a valid YouTube URL';
                    this.after(feedback);
                }
            } else {
                this.classList.remove('is-invalid');
                if (this.nextElementSibling && this.nextElementSibling.classList.contains('invalid-feedback')) {
                    this.nextElementSibling.remove();
                }
            }
        });
    }
});

// Animate elements when they come into view
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.card, .feature-icon');
    
    elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;
        
        if (elementPosition < windowHeight - 50) {
            element.classList.add('fade-in');
        }
    });
};

window.addEventListener('scroll', animateOnScroll);
window.addEventListener('load', animateOnScroll);
