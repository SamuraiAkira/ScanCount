(function() {
    const elements = {
        input: document.getElementById('input-data'),
        pasteBtn: document.getElementById('paste-btn'),
        clearInputBtn: document.getElementById('clear-input-btn'),
        processBtn: document.getElementById('process-btn'),
        clearLogBtn: document.getElementById('clear-log-btn'),
        logContainer: document.getElementById('log-container'),
        themeToggle: document.getElementById('theme-toggle'),
        themeLabel: document.getElementById('theme-label'),
        modal: document.getElementById('result-modal'),
        resultContent: document.getElementById('result-content'),
        closeModalBtn: document.getElementById('close-modal-btn')
    };

    function addLog(message) {
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.textContent = message;
        elements.logContainer.appendChild(entry);
        elements.logContainer.scrollTop = elements.logContainer.scrollHeight;
    }

    function clearLogs() {
        elements.logContainer.innerHTML = '';
    }

    async function processData() {
        const data = elements.input.value.trim();
        if (!data) {
            addLog('Ошибка: поле ввода пусто.');
            return;
        }

        addLog('Обработка начата...');
        try {
            const response = await eel.process_data(data)();
            if (response.logs) {
                response.logs.forEach(msg => addLog(msg));
            }
            if (response.result) {
                elements.resultContent.textContent = response.result;
                elements.modal.classList.add('show');
            }
        } catch (err) {
            addLog(`Ошибка: ${err.message}`);
        }
    }

    async function pasteFromClipboard() {
        try {
            const text = await eel.paste_from_clipboard()();
            if (text && typeof text === 'string') {
                elements.input.value = text;
                addLog('Данные вставлены из буфера обмена.');
            } else {
                addLog('Буфер обмена пуст или недоступен.');
            }
        } catch (err) {
            addLog('Не удалось вставить из буфера: нет доступа или буфер пуст.');
        }
    }

    function clearInput() {
        elements.input.value = '';
        addLog('Поле ввода очищено.');
    }

    function toggleTheme() {
        if (elements.themeToggle.checked) {
            document.body.classList.add('dark');
            elements.themeLabel.textContent = 'Тёмная тема';
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.classList.remove('dark');
            elements.themeLabel.textContent = 'Светлая тема';
            localStorage.setItem('theme', 'light');
        }
    }

    function loadThemePreference() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'light') {
            elements.themeToggle.checked = false;
            document.body.classList.remove('dark');
            elements.themeLabel.textContent = 'Светлая тема';
        } else {
            elements.themeToggle.checked = true;
            document.body.classList.add('dark');
            elements.themeLabel.textContent = 'Тёмная тема';
        }
    }

    function closeModal() {
        elements.modal.classList.remove('show');
    }

    window.addEventListener('click', (e) => {
        if (e.target === elements.modal) {
            closeModal();
        }
    });

    elements.pasteBtn.addEventListener('click', pasteFromClipboard);
    elements.clearInputBtn.addEventListener('click', clearInput);
    elements.processBtn.addEventListener('click', processData);
    elements.clearLogBtn.addEventListener('click', clearLogs);
    elements.themeToggle.addEventListener('change', toggleTheme);
    elements.closeModalBtn.addEventListener('click', closeModal);

    loadThemePreference();
    addLog('Интерфейс загружен.');
    addLog('Подсказка: используйте правую кнопку мыши для контекстного меню браузера.');
})();