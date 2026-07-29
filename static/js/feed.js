/* ============================================================
   SOCIOPROGRAM — Feed & Post Interactions (jQuery)
   ============================================================ */

$(function () {
    'use strict';

    // ── Star Toggle (Contribution Appreciation) ──────────
    $(document).on('click', '.star-btn', function (e) {
        e.preventDefault();
        var btn = $(this);
        var postId = btn.data('post-id');
        if (!postId) return;

        $.post('/api/posts/' + postId + '/star', function (data) {
            var svg = btn.find('svg');
            var countEl = btn.find('.star-count');

            if (data.starred) {
                btn.addClass('star-btn--active');
                svg.attr('fill', 'currentColor');
                // Star pulse animation
                btn.css('transform', 'scale(1.2)');
                setTimeout(function () { btn.css('transform', 'scale(1)'); }, 200);
            } else {
                btn.removeClass('star-btn--active');
                svg.attr('fill', 'none');
            }
            countEl.text(data.count);
        }).fail(function (xhr) {
            if (xhr.status === 401) {
                window.location.href = '/auth/login';
            }
        });
    });

    // ── Comment Submission via AJAX ──────────────────────
    $(document).on('submit', '#comment-form', function (e) {
        e.preventDefault();
        var form = $(this);
        var postId = form.data('post-id');
        var textarea = form.find('textarea[name="content"]');
        var content = textarea.val().trim();

        if (!content) return;

        $.post('/api/posts/' + postId + '/comment', {
            content: content
        }, function (data) {
            // Build new comment HTML
            var avatarInner = data.author_avatar
                ? '<img src="' + data.author_avatar + '" alt="">'
                : '<span>' + data.author.charAt(0).toUpperCase() + '</span>';

            var html = '<div class="comment" id="comment-' + data.id + '">' +
                '<div class="comment__avatar"><div class="avatar avatar--xs">' + avatarInner + '</div></div>' +
                '<div class="comment__body">' +
                    '<div class="comment__header">' +
                        '<a href="/profile/' + data.author + '" class="comment__author">' + data.display_name + '</a>' +
                        '<span class="comment__handle">@' + data.author + '</span>' +
                        '<span class="comment__time">' + data.time_ago + '</span>' +
                    '</div>' +
                    '<p class="comment__content">' + $('<span>').text(data.content).html() + '</p>' +
                '</div></div>';

            $('#comments-list').prepend(html);
            textarea.val('');
            window.showToast('Comment posted');

            // Update comment count on the page
            var title = $('.comments-section__title');
            var match = title.text().match(/\((\d+)\)/);
            if (match) {
                var newCount = parseInt(match[1], 10) + 1;
                title.text('Comments (' + newCount + ')');
            }
        }).fail(function (xhr) {
            if (xhr.status === 401) {
                window.location.href = '/auth/login';
            } else {
                var errMsg = xhr.responseJSON ? xhr.responseJSON.error : 'Failed to post comment.';
                window.showToast(errMsg);
            }
        });
    });

    // ── Comment Delete ──────────────────────────────────
    $(document).on('click', '.comment__delete', function () {
        var btn = $(this);
        var commentId = btn.data('comment-id');
        if (!confirm('Delete this comment?')) return;

        $.post('/api/comments/' + commentId + '/delete', function (data) {
            if (data.deleted) {
                $('#comment-' + commentId).fadeOut(300, function () { $(this).remove(); });
                window.showToast('Comment deleted');
            }
        });
    });

    // ── Report Modal (Inline) ───────────────────────────
    $(document).on('click', '.report-btn', function (e) {
        e.preventDefault();
        var postId = $(this).data('post-id');
        var commentId = $(this).data('comment-id');

        // Simple prompt-based report for now
        var reason = prompt(
            'Report this content.\n\n' +
            'Select reason:\n' +
            '1. Off-topic\n2. Spam\n3. Harassment\n4. AI spam\n5. Clickbait\n' +
            '6. Malicious code\n7. Impersonation\n8. Unconstructive\n9. NSFW\n10. License violation\n\n' +
            'Enter reason number or description:'
        );

        if (!reason) return;

        var reasons = {
            '1': 'Off-topic content', '2': 'Self-promotion/Spam', '3': 'Toxicity/Harassment',
            '4': 'AI-generated spam', '5': 'Clickbait', '6': 'Malicious code',
            '7': 'Impersonation', '8': 'Unconstructive behaviour', '9': 'NSFW',
            '10': 'License violation'
        };

        var mapped = reasons[reason] || reason;

        var payload = { reason: mapped, details: '' };
        if (postId) payload.post_id = postId;
        if (commentId) payload.comment_id = commentId;

        $.post('/api/report', payload, function (data) {
            window.showToast(data.message || 'Report submitted. Thank you.');
        }).fail(function () {
            window.showToast('Failed to submit report.');
        });
    });

    // ── Bookmark Toggle ──────────────────────────────────
    $(document).on('click', '.bookmark-btn', function (e) {
        e.preventDefault();
        var btn = $(this);
        var postId = btn.data('post-id');
        if (!postId) return;

        $.post('/api/posts/' + postId + '/bookmark', function (data) {
            var svg = btn.find('svg');
            var countEl = btn.find('.bookmark-count');
            if (data.bookmarked) {
                btn.addClass('bookmark-btn--active');
                svg.attr('fill', 'currentColor');
                window.showToast('Post bookmarked');
            } else {
                btn.removeClass('bookmark-btn--active');
                svg.attr('fill', 'none');
                window.showToast('Bookmark removed');
            }
            countEl.text(data.count);
        }).fail(function (xhr) {
            if (xhr.status === 401) {
                window.location.href = '/auth/login';
            }
        });
    });

    // ── Repost Handler ──────────────────────────────────
    $(document).on('click', '.repost-btn', function (e) {
        e.preventDefault();
        var btn = $(this);
        var postId = btn.data('post-id');
        if (!postId) return;

        var comment = prompt('Add an optional quote commentary for your repost:');
        if (comment === null) return;

        $.post('/api/posts/' + postId + '/repost', { comment: comment }, function (data) {
            var countEl = btn.find('.repost-count');
            if (data.reposted) {
                btn.addClass('repost-btn--active');
                window.showToast('Post reposted to your followers!');
            } else {
                btn.removeClass('repost-btn--active');
                window.showToast('Repost removed');
            }
            countEl.text(data.count);
        }).fail(function (xhr) {
            if (xhr.status === 401) {
                window.location.href = '/auth/login';
            }
        });
    });

    // ── Follow Toggle ───────────────────────────────────
    $(document).on('click', '.follow-btn', function () {
        var btn = $(this);
        var userId = btn.data('user-id');

        $.post('/api/users/' + userId + '/follow', function (data) {
            if (data.following) {
                btn.text('Following').removeClass('btn--primary').addClass('btn--ghost');
            } else {
                btn.text('Follow').removeClass('btn--ghost').addClass('btn--primary');
            }
        }).fail(function (xhr) {
            if (xhr.status === 401) {
                window.location.href = '/auth/login';
            }
        });
    });
});
