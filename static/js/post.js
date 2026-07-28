/* ============================================================
   SOCIOPROGRAM — Post Creation Page Logic (jQuery)
   ============================================================ */

$(function () {
    'use strict';

    // ── Title Character Counter ──────────────────────────
    var titleInput = $('#title');
    var titleCount = $('#title-count');

    if (titleInput.length) {
        titleInput.on('input', function () {
            var len = $(this).val().length;
            titleCount.text(len + '/200');
            if (len > 190) {
                titleCount.css('color', 'var(--accent-red)');
            } else {
                titleCount.css('color', 'var(--text-muted)');
            }
        });
    }

    // ── Screenshot Upload Preview ────────────────────────
    var fileInput = $('#screenshot');
    var previewBox = $('#screenshot-preview');
    var previewImg = $('#screenshot-img');
    var promptBox = $('#upload-prompt');

    if (fileInput.length) {
        fileInput.on('change', function () {
            var file = this.files[0];
            if (file) {
                if (file.size > 5 * 1024 * 1024) {
                    window.showToast('File too large. Maximum 5MB.');
                    this.value = '';
                    return;
                }
                var reader = new FileReader();
                reader.onload = function (e) {
                    previewImg.attr('src', e.target.result);
                    previewBox.show();
                    promptBox.hide();
                };
                reader.readAsDataURL(file);
            }
        });

        $('#remove-screenshot').on('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            fileInput.val('');
            previewBox.hide();
            promptBox.show();
        });
    }

    // ── Code Editor Tab Support ──────────────────────────
    var codeArea = $('#code_snippet');
    if (codeArea.length) {
        codeArea.on('keydown', function (e) {
            if (e.key === 'Tab') {
                e.preventDefault();
                var start = this.selectionStart;
                var end = this.selectionEnd;
                var val = $(this).val();
                $(this).val(val.substring(0, start) + '    ' + val.substring(end));
                this.selectionStart = this.selectionEnd = start + 4;
            }
        });
    }
});
