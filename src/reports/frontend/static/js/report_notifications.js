(function () {
    if (window.__reportNotificationsInitialized) {
        return;
    }
    window.__reportNotificationsInitialized = true;

    function initButtonsState() {
        const cards = document.querySelectorAll('[data-report-id]');
        cards.forEach(card => {
            const buttons = card.querySelectorAll('.card__side a.card__button');
            buttons.forEach(button => {
                const obj = button.dataset.objectName || '';
                if (!obj) {
                    button.classList.add('is-disabled');
                } else {
                    button.classList.remove('is-disabled');
                }
            });
        });
    }

    document.addEventListener('click', function (e) {
        const el = e.target.closest('.card__side a.card__button');
        if (!el) return;
        if (el.classList.contains('is-disabled') || el.getAttribute('aria-disabled') === 'true') {
            e.preventDefault();
            return false;
        }
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initButtonsState);
    } else {
        initButtonsState();
    }

    function updateButtonForFile(fileName, fileType, downloadUrl) {
        const reportId = fileName.replace(/\.[^/.]+$/, '');
        const card = document.querySelector('[data-report-id="' + reportId + '"]');
        if (!card) return false;

        const button = card.querySelector('.card__side a.card__button[data-file-type="' + fileType + '"]');
        if (!button) return false;

        if (downloadUrl) {
            button.href = downloadUrl;
        } else {
            button.href = '/download-file/' + encodeURIComponent(fileName);
        }
        button.dataset.objectName = fileName;
        button.classList.remove('is-disabled');
        
        var fileTypeLabels = {
            'pdf': 'Скачать PDF',
            'docx': 'Скачать DOCX',
            'geojson': 'Скачать GEOJSON'
        };
        var label = fileTypeLabels[fileType] || ('Скачать ' + fileType.toUpperCase());
        button.textContent = label;
        console.log('[reports] Updated button for', fileType, 'in report', reportId);
        return true;
    }

    var sseConnected = false;
    try {
        const src = new EventSource('/events/report-ready');

        src.addEventListener('open', function () {
            sseConnected = true;
            console.log('[reports] SSE connected');
        });

        src.addEventListener('report_ready', function (e) {
            try {
                const payload = JSON.parse(e.data);
                const fileName = payload.file_name || '';
                const fileType = payload.file_type || '';
                const downloadUrl = payload.download_url || '';

                console.log('[reports] SSE event received:', fileType, fileName);

                if (updateButtonForFile(fileName, fileType, downloadUrl)) {
                    return; 
                }

                console.log('[reports] Card not found, reloading list...');
                fetch('/documents')
                    .then(response => response.text())
                    .then(html => {
                        const parser = new DOMParser();
                        const newDoc = parser.parseFromString(html, 'text/html');
                        const newList = newDoc.querySelector('.list');
                        const oldList = document.querySelector('.list');
                        if (newList && oldList) {
                            oldList.innerHTML = newList.innerHTML;
                            initButtonsState();
                            setTimeout(() => {
                                if (updateButtonForFile(fileName, fileType, downloadUrl)) {
                                    console.log('[reports] Button updated after list refresh');
                                }
                            }, 50);
                        }
                    })
                    .catch(err => console.error('[reports] Failed to refresh reports list', err));
            } catch (err) {
                console.error('[reports] SSE handler error', err);
            }
        });

        src.onerror = function () {
            sseConnected = false;
            console.warn('[reports] SSE connection lost');
        };
    } catch (err) {
        console.warn('[reports] SSE not available', err);
    }

    var pollInterval = null;
    
    function startPolling() {
        if (pollInterval) return; 
        
        pollInterval = setInterval(function () {
            if (document.hidden) return; 
            
            const disabledButtons = document.querySelectorAll('.card__button.is-disabled');
            if (disabledButtons.length === 0) {
                clearInterval(pollInterval);
                pollInterval = null;
                console.log('[reports] All buttons enabled, stopped polling');
                return;
            }
            
            fetch('/documents')
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const newDoc = parser.parseFromString(html, 'text/html');
                    const newList = newDoc.querySelector('.list');
                    const oldList = document.querySelector('.list');
                    if (newList && oldList) {
                        oldList.innerHTML = newList.innerHTML;
                        initButtonsState();
                        console.log('[reports] Polling: refreshed reports list');
                    }
                })
                .catch(err => console.error('[reports] Polling failed:', err));
        }, 2000);
        
        console.log('[reports] Started polling for file updates');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            if (document.querySelectorAll('.card__button.is-disabled').length > 0) {
                startPolling();
            }
        });
    } else {
        if (document.querySelectorAll('.card__button.is-disabled').length > 0) {
            startPolling();
        }
    }

})();
