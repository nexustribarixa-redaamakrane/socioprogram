/* ============================================================
   SOCIOPROGRAM — Auth Page Logic (jQuery)
   ============================================================ */

$(function () {
    'use strict';

    // ── Password Strength Indicator ──────────────────────
    var pwInput = $('#password');
    var strengthBar = $('#password-strength');

    if (pwInput.length && strengthBar.length) {
        pwInput.on('input', function () {
            var pw = $(this).val();
            var score = 0;
            if (pw.length >= 8) score++;
            if (pw.length >= 12) score++;
            if (/[0-9]/.test(pw)) score++;
            if (/[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;'`~]/.test(pw)) score++;
            if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;

            var width = (score / 5) * 100;
            var color;
            if (score <= 1) color = 'var(--accent-red)';
            else if (score <= 2) color = 'var(--accent-orange)';
            else if (score <= 3) color = 'var(--accent-orange)';
            else color = 'var(--accent-green)';

            strengthBar.css({
                width: width + '%',
                backgroundColor: color,
                height: '4px'
            });
        });
    }

    // ── 2FA Code Auto-Focus ──────────────────────────────
    var codeInput = $('.form-input--code');
    if (codeInput.length) {
        codeInput.focus();
        codeInput.on('input', function () {
            // Auto-submit when 6 digits entered
            if ($(this).val().length === 6) {
                $(this).closest('form').submit();
            }
        });
    }

    // ── Username Validation (live) ───────────────────────
    var usernameInput = $('#username');
    if (usernameInput.length) {
        usernameInput.on('input', function () {
            var val = $(this).val();
            // Force lowercase
            if (val !== val.toLowerCase()) {
                $(this).val(val.toLowerCase());
            }
        });
    }
});
