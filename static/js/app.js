/* ============================================================
   SOCIOPROGRAM — Core jQuery Application Logic
   ============================================================ */

$(function () {
    'use strict';

    // ── CSRF Token Setup for all AJAX ────────────────────
    var csrfToken = $('meta[name="csrf-token"]').attr('content');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', csrfToken);
            }
        }
    });

    // ── Syntax Highlighting ──────────────────────────────
    if (typeof hljs !== 'undefined') {
        hljs.highlightAll();
    }

    // ── Flash Message Auto-Dismiss ───────────────────────
    setTimeout(function () {
        $('.flash').each(function (i) {
            var el = $(this);
            setTimeout(function () {
                el.fadeOut(300, function () { el.remove(); });
            }, i * 200);
        });
    }, 5000);

    // ── Notification Badge Polling (60s, anti-bloat) ─────
    function pollNotifications() {
        $.getJSON('/api/notifications/count', function (data) {
            var count = data.count || 0;
            $('.notif-badge').text(count).toggle(count > 0);
        });
    }

    if ($('.notif-badge').length) {
        setInterval(pollNotifications, 60000);
    }

    // ── Toast System ─────────────────────────────────────
    window.showToast = function (message, duration) {
        duration = duration || 3000;
        var toast = $('<div class="toast"></div>').text(message);
        $('#toast-container').append(toast);
        setTimeout(function () {
            toast.fadeOut(300, function () { toast.remove(); });
        }, duration);
    };

    // ── Share Button (Copy Link) ─────────────────────────
    $(document).on('click', '.share-btn', function (e) {
        e.preventDefault();
        var url = $(this).data('url');
        if (navigator.clipboard && url) {
            navigator.clipboard.writeText(url).then(function () {
                window.showToast('Link copied to clipboard');
            });
        }
    });

    // ── Code Copy Button ─────────────────────────────────
    $(document).on('click', '.code-copy', function () {
        var codeId = $(this).data('code');
        var codeEl = document.getElementById(codeId);
        if (codeEl && navigator.clipboard) {
            navigator.clipboard.writeText(codeEl.textContent).then(function () {
                window.showToast('Code copied');
            });
        }
    });
});
