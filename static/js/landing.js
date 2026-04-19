document.addEventListener('DOMContentLoaded', function() {
    // ============================================
    // Navigation Scroll Effect
    // ============================================
    const navbar = document.getElementById('navbar');

    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // ============================================
    // Scroll-Triggered Animations (Intersection Observer)
    // ============================================
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const animateOnScroll = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    // Observe journey cards
    document.querySelectorAll('.journey-card').forEach(card => {
        animateOnScroll.observe(card);
    });

    // Observe testimonial cards
    document.querySelectorAll('.testimonial-card').forEach(card => {
        animateOnScroll.observe(card);
    });

    // Observe feature badges
    document.querySelectorAll('.feature-badge').forEach(badge => {
        animateOnScroll.observe(badge);
    });

    // ============================================
    // Smooth Scroll for Anchor Links
    // ============================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // ============================================
    // Parallax Effect for Floating Shapes
    // ============================================
    const shapes = document.querySelectorAll('.floating-shape');

    window.addEventListener('scroll', function() {
        const scrolled = window.scrollY;
        shapes.forEach((shape, index) => {
            const speed = 0.1 + (index * 0.05);
            shape.style.transform = `translateY(${scrolled * speed}px)`;
        });
    });

    console.log('Landing page animations initialized');
});

// ============================================
// AI Resume Rewrite
// ============================================
(function() {
    var toolbar = document.getElementById('ai-toolbar');
    var rewriteBtn = document.getElementById('ai-rewrite-btn');
    var modal = document.getElementById('ai-rewrite-modal');
    var modalBackdrop = document.getElementById('ai-modal-backdrop');
    var modalClose = document.getElementById('ai-modal-close');
    var upgradeModal = document.getElementById('upgrade-modal');
    var upgradeBackdrop = document.getElementById('upgrade-modal-backdrop');
    var upgradeCloseBtn = document.getElementById('upgrade-close-btn');
    var loadingDiv = document.getElementById('ai-rewrite-loading');
    var optionsDiv = document.getElementById('ai-rewrite-options');
    var errorDiv = document.getElementById('ai-rewrite-error');
    var errorMsg = document.getElementById('ai-error-message');
    var originalText = document.getElementById('ai-original-text');
    var originalToggle = document.getElementById('ai-original-toggle');
    var regenerateBtn = document.getElementById('ai-regenerate-btn');
    var retryBtn = document.getElementById('ai-retry-btn');
    var remainingText = document.getElementById('ai-remaining-text');
    var resumeId = document.getElementById('resume-id');

    if (!toolbar || !rewriteBtn) return;

    var selectedText = '';
    var alternatives = [];
    var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ?
        document.querySelector('[name=csrfmiddlewaretoken]').value : '';

    // Show floating toolbar on text selection within form fields
    document.addEventListener('mouseup', function(e) {
        // Only activate in builder form
        var form = document.getElementById('resume-form');
        if (!form || !form.contains(e.target)) return;

        var sel = window.getSelection().toString().trim();
        if (sel.length > 10) {
            selectedText = sel;
            var range = window.getSelection().getRangeAt(0);
            var rect = range.getBoundingClientRect();
            toolbar.style.left = (rect.left + window.scrollX) + 'px';
            toolbar.style.top = (rect.top + window.scrollY - 50) + 'px';
            toolbar.classList.remove('hidden');
        } else {
            toolbar.classList.add('hidden');
        }
    });

    rewriteBtn.addEventListener('click', function() {
        if (!resumeId) return;
        var rid = resumeId.value;
        fetch('/api/resumes/' + rid + '/rewrite/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken || getCookie('csrftoken'),
            },
            body: JSON.stringify({selected_text: selectedText})
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.error === 'upgrade_required') {
                upgradeModal.classList.remove('hidden');
                return;
            }
            if (data.error === 'rate_limit') {
                showError(data.message);
                return;
            }
            if (data.error) {
                showError(data.error);
                return;
            }
            alternatives = data.alternatives;
            showAlternatives(alternatives, data.remaining, data.limit);
        })
        .catch(function() {
            showError('AI rewrite failed. Please check your connection and try again.');
        });
    });

    function showAlternatives(alts, remaining, limit) {
        loadingDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        optionsDiv.classList.remove('hidden');
        modal.classList.remove('hidden');
        toolbar.classList.add('hidden');

        originalText.textContent = selectedText;
        remainingText.textContent = remaining + ' rewrites remaining today';

        optionsDiv.innerHTML = '';
        alts.forEach(function(alt, idx) {
            var card = document.createElement('div');
            card.className = 'rewrite-card';
            card.innerHTML =
                '<p class="text-gray-800 text-sm leading-relaxed mb-3">' + escapeHtml(alt) + '</p>' +
                '<div class="flex gap-2">' +
                '<button type="button" class="use-this-btn flex-1 px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"' +
                ' data-text="' + escapeAttr(alt) + '">Use This</button>' +
                '<button type="button" class="edit-btn px-3 py-1.5 border border-gray-300 text-gray-700 text-sm rounded-md hover:bg-gray-50"' +
                ' data-text="' + escapeAttr(alt) + '">Edit</button>' +
                '</div>';
            optionsDiv.appendChild(card);
        });

        // Use This
        optionsDiv.querySelectorAll('.use-this-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                applyRewrite(btn.dataset.text);
                closeModal();
            });
        });

        // Edit
        optionsDiv.querySelectorAll('.edit-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var textarea = document.createElement('textarea');
                textarea.className = 'w-full p-2 border rounded-lg text-sm mb-2';
                textarea.value = btn.dataset.text;
                textarea.rows = 3;
                var card = btn.closest('.rewrite-card');
                card.querySelector('p').replaceWith(textarea);
                card.querySelector('.flex').innerHTML =
                    '<button type="button" class="apply-edit-btn flex-1 px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700">' +
                    'Use This</button>';
                card.querySelector('.apply-edit-btn').addEventListener('click', function() {
                    applyRewrite(textarea.value);
                    closeModal();
                });
            });
        });
    }

    function showError(msg) {
        loadingDiv.classList.add('hidden');
        optionsDiv.classList.add('hidden');
        errorDiv.classList.remove('hidden');
        errorMsg.textContent = msg;
        modal.classList.remove('hidden');
    }

    function closeModal() {
        modal.classList.add('hidden');
        toolbar.classList.add('hidden');
        window.getSelection().removeAllRanges();
    }

    function applyRewrite(text) {
        // Find the active form field and replace selection
        var sel = window.getSelection();
        if (sel.rangeCount > 0) {
            var range = sel.getRangeAt(0);
            range.deleteContents();
            range.insertNode(document.createTextNode(text));
            sel.removeAllRanges();
        }
    }

    function escapeHtml(str) {
        return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }
    function escapeAttr(str) {
        return str.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    // getCookie helper (inline copy from resume_builder.html)
    function getCookie(name) {
        var value = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    value = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return value;
    }

    // Close handlers
    modalBackdrop && modalBackdrop.addEventListener('click', closeModal);
    modalClose && modalClose.addEventListener('click', closeModal);
    regenerateBtn && regenerateBtn.addEventListener('click', function() {
        optionsDiv.classList.add('hidden');
        loadingDiv.classList.remove('hidden');
        rewriteBtn.click();
    });
    retryBtn && retryBtn.addEventListener('click', function() {
        errorDiv.classList.add('hidden');
        loadingDiv.classList.remove('hidden');
        rewriteBtn.click();
    });

    // Upgrade modal
    upgradeBackdrop && upgradeBackdrop.addEventListener('click', function() {
        upgradeModal.classList.add('hidden');
    });
    upgradeCloseBtn && upgradeCloseBtn.addEventListener('click', function() {
        upgradeModal.classList.add('hidden');
    });

    // Original text toggle
    originalToggle && originalToggle.addEventListener('click', function() {
        originalText.classList.toggle('hidden');
    });
})();
