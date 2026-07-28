/* ============================================================
   SOCIOPROGRAM — Moderation UI Logic (jQuery)
   ============================================================ */

$(function () {
    'use strict';

    // ── Show/Hide Ban Duration Field ─────────────────────
    $(document).on('change', '.mod-action-form select[name="action"]', function () {
        var form = $(this).closest('.mod-action-form');
        var durationInput = form.find('input[name="duration_days"]');
        if ($(this).val() === 'temp_ban') {
            durationInput.prop('required', true).css('opacity', 1);
        } else {
            durationInput.prop('required', false).css('opacity', 0.4);
        }
    });

    // ── Confirm Destructive Actions ──────────────────────
    $(document).on('submit', '.mod-action-form', function (e) {
        var action = $(this).find('select[name="action"]').val();
        if (action === 'perm_ban') {
            if (!confirm('PERMANENT BAN — this action is severe. Are you sure?')) {
                e.preventDefault();
            }
        } else if (action === 'temp_ban') {
            if (!confirm('Issue temporary ban?')) {
                e.preventDefault();
            }
        }
    });
});
