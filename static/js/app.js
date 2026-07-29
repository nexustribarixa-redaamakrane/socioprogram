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
    $(document).on('click', '.copy-code-btn', function (e) {
        e.preventDefault();
        var code = $(this).data('code') || $(this).closest('.code-block-wrapper').find('code').text();
        var btn = $(this);
        if (navigator.clipboard && code) {
            navigator.clipboard.writeText(code).then(function () {
                btn.find('span').text('Copied!');
                window.showToast('Code snippet copied to clipboard');
                setTimeout(function () {
                    btn.find('span').text('Copy Code');
                }, 2000);
            });
        }
    });

    // ── Image Lightbox Handler ──────────────────────────
    $(document).on('click', '.lightbox-trigger', function () {
        var src = $(this).data('img-src') || $(this).find('img').attr('src');
        if (src) {
            $('#lightbox-img').attr('src', src);
            $('#lightbox-backdrop').removeClass('hidden');
        }
    });

    $(document).on('click', '#lightbox-backdrop, .lightbox-close', function (e) {
        if (e.target === this || $(e.target).hasClass('lightbox-close')) {
            $('#lightbox-backdrop').addClass('hidden');
        }
    });

    // ── Live Instant Search Handler ──────────────────────
    var searchTimer = null;
    $('#global-search-input').on('input', function () {
        var q = $(this).val().trim();
        clearTimeout(searchTimer);
        if (q.length < 2) {
            $('#search-dropdown').addClass('hidden').empty();
            return;
        }
        searchTimer = setTimeout(function () {
            $.getJSON('/api/search/live?q=' + encodeURIComponent(q), function (data) {
                var dropdown = $('#search-dropdown');
                dropdown.empty();
                var hasResults = false;

                if (data.users && data.users.length) {
                    hasResults = true;
                    dropdown.append('<div class="search-dropdown-title">Users</div>');
                    data.users.forEach(function (u) {
                        dropdown.append('<a href="/profile/' + u.username + '" class="search-item">👤 @' + u.username + ' (' + u.display_name + ')</a>');
                    });
                }
                if (data.tags && data.tags.length) {
                    hasResults = true;
                    dropdown.append('<div class="search-dropdown-title">Tags</div>');
                    data.tags.forEach(function (t) {
                        dropdown.append('<a href="/?tag=' + t.name + '" class="search-item">#️⃣ #' + t.name + '</a>');
                    });
                }
                if (data.posts && data.posts.length) {
                    hasResults = true;
                    dropdown.append('<div class="search-dropdown-title">Posts</div>');
                    data.posts.forEach(function (p) {
                        dropdown.append('<a href="/post/' + p.id + '" class="search-item">📄 ' + p.title + '</a>');
                    });
                }

                if (hasResults) {
                    dropdown.removeClass('hidden');
                } else {
                    dropdown.html('<div class="search-item" style="color:var(--text-muted);">No results found</div>').removeClass('hidden');
                }
            });
        }, 200);
    });

    $(document).on('click', function (e) {
        if (!$(e.target).closest('.search-box').length) {
            $('#search-dropdown').addClass('hidden');
        }
    });

    // ── Modals Manager ───────────────────────────────────
    function openModal(htmlContent) {
        $('#modal-body').html(htmlContent);
        $('#modal-backdrop').removeClass('hidden');
    }

    function closeModal() {
        $('#modal-backdrop').addClass('hidden');
        $('#modal-body').empty();
    }

    $(document).on('click', '#modal-close-btn, #modal-backdrop', function (e) {
        if (e.target === this || e.target.id === 'modal-close-btn') {
            closeModal();
        }
    });

    // Followers Modal Trigger
    $(document).on('click', '.modal-trigger-followers', function () {
        var userId = $(this).data('user-id');
        $.getJSON('/api/users/' + userId + '/followers', function (users) {
            var html = '<h3>Followers</h3><div class="user-list-modal" style="margin-top:1rem;display:flex;flex-direction:column;gap:0.75rem;">';
            if (!users.length) {
                html += '<p style="color:var(--text-muted)">No followers yet.</p>';
            } else {
                users.forEach(function (u) {
                    html += '<div style="display:flex;align-items:center;justify-content:space-between;"><a href="/profile/' + u.username + '" style="display:flex;align-items:center;gap:0.5rem;color:var(--text-primary);">👤 @' + u.username + '</a></div>';
                });
            }
            html += '</div>';
            openModal(html);
        });
    });

    // Following Modal Trigger
    $(document).on('click', '.modal-trigger-following', function () {
        var userId = $(this).data('user-id');
        $.getJSON('/api/users/' + userId + '/following', function (users) {
            var html = '<h3>Following</h3><div class="user-list-modal" style="margin-top:1rem;display:flex;flex-direction:column;gap:0.75rem;">';
            if (!users.length) {
                html += '<p style="color:var(--text-muted)">Not following anyone yet.</p>';
            } else {
                users.forEach(function (u) {
                    html += '<div style="display:flex;align-items:center;justify-content:space-between;"><a href="/profile/' + u.username + '" style="display:flex;align-items:center;gap:0.5rem;color:var(--text-primary);">👤 @' + u.username + '</a></div>';
                });
            }
            html += '</div>';
            openModal(html);
        });
    });
});
