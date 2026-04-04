const textarea = document.getElementById('productInput');
const pasteBtn = document.getElementById('pasteBtn');
const clearTextBtn = document.getElementById('clearTextBtn');
const processBtn = document.getElementById('processBtn');
const logContainer = document.getElementById('logContainer');
const clearLogsBtn = document.getElementById('clearLogsBtn');
const quickStatsSpan = document.getElementById('quickStats');

// --- Вспомогательные функции для логов ---
function addLog(message, type = 'info') {
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    // добавим временную метку
    const now = new Date();
    const timeStr = now.toLocaleTimeString('ru-RU', { hour: '2-digit', minute:'2-digit', second:'2-digit' });
    logEntry.innerHTML = `<span style="opacity:0.6; margin-right:8px;">[${timeStr}]</span> ${message}`;
    logContainer.appendChild(logEntry);
    // автоскролл вниз
    logContainer.scrollTop = logContainer.scrollHeight;
    // ограничим кол-во логов для производительности (но не принципиально)
    while (logContainer.children.length > 150) {
        logContainer.removeChild(logContainer.firstChild);
    }
}

function clearLogs() {
    while (logContainer.firstChild) {
        logContainer.removeChild(logContainer.firstChild);
    }
    addLog('🧹 Журнал очищен', 'info');
    addLog('✅ Готов к обработке новых данных', 'success');
}

// --- Функция парсинга строки с умным определением названия (поддержка нескольких слов)---
// Формат строки: "название_продукта(слова через пробел) цена количество"
// Принцип: разбиваем по пробелам, последний элемент -> количество, предпоследний -> цена, всё остальное -> название.
function parseProductLine(line) {
    line = line.trim();
    if (line === "") return null;
    const parts = line.trim().split(/\s+/);
    if (parts.length < 3) {
        return { valid: false, reason: `Недостаточно полей: нужно минимум "название цена количество" (получено ${parts.length})` };
    }
    // извлекаем количество (последний)
    const quantityRaw = parts[parts.length - 1];
    const priceRaw = parts[parts.length - 2];
    const nameParts = parts.slice(0, parts.length - 2);
    let productName = nameParts.join(' ');
    if (productName.length === 0) {
        return { valid: false, reason: `Название продукта отсутствует (перед ценой и количеством)` };
    }

    // парсим цену (число с плавающей точкой)
    let price = parseFloat(priceRaw.replace(',', '.')); // поддержка запятой
    if (isNaN(price)) {
        return { valid: false, reason: `Цена "${priceRaw}" не является числом` };
    }
    if (price < 0) {
        return { valid: false, reason: `Цена не может быть отрицательной (${price})` };
    }

    // парсим количество (целое или дробное, но для склада обычно целое, но сделаем поддержку float)
    let quantity = parseFloat(quantityRaw.replace(',', '.'));
    if (isNaN(quantity)) {
        return { valid: false, reason: `Количество "${quantityRaw}" не является числом` };
    }
    if (quantity < 0) {
        return { valid: false, reason: `Количество не может быть отрицательным (${quantity})` };
    }
    // округляем количество до 3 знаков (для красоты, но храним как есть)
    quantity = parseFloat(quantity.toFixed(3));
    price = parseFloat(price.toFixed(2));

    return {
        valid: true,
        name: productName,
        price: price,
        quantity: quantity,
        rawLine: line
    };
}

// Основная функция обработки всего текста из textarea
function processWarehouseData() {
    const rawText = textarea.value;
    if (!rawText.trim()) {
        addLog('⚠️ Поле ввода пустое. Нечего обрабатывать.', 'warning');
        updateStats(null, []);
        return;
    }

    const lines = rawText.split(/\r?\n/);
    let validItems = [];
    let errors = [];
    let lineNumber = 0;

    for (let line of lines) {
        lineNumber++;
        if (line.trim() === "") continue; // пропускаем пустые строки
        const parsed = parseProductLine(line);
        if (parsed && parsed.valid) {
            validItems.push({
                name: parsed.name,
                price: parsed.price,
                quantity: parsed.quantity,
                line: lineNumber,
                raw: line
            });
        } else {
            const reason = parsed ? parsed.reason : "Неизвестная ошибка";
            errors.push({ line: lineNumber, raw: line, reason });
        }
    }

    // Логирование результатов
    if (validItems.length === 0 && errors.length === 0) {
        addLog('ℹ️ Нет непустых строк для обработки', 'info');
        updateStats(null, []);
        return;
    }

    if (validItems.length > 0) {
        addLog(`✅ Успешно обработано позиций: ${validItems.length}`, 'success');
        // дополнительно выведем краткий перечень в лог (первые 3-5)
        const sample = validItems.slice(0, 4).map(it => `${it.name} (${it.price}₽ × ${it.quantity})`).join(', ');
        if (validItems.length > 4) {
            addLog(`📦 Примеры: ${sample} и ещё ${validItems.length - 4} позиций`, 'info');
        } else {
            addLog(`📦 Список: ${sample}`, 'info');
        }
        // Также выведем суммарную статистику и обновим нижнюю панель
        const totalSum = validItems.reduce((acc, item) => acc + (item.price * item.quantity), 0);
        const totalUnits = validItems.reduce((acc, item) => acc + item.quantity, 0);
        addLog(`💰 Общая стоимость запасов: ${totalSum.toFixed(2)} руб. | Общее количество единиц: ${totalUnits.toFixed(3)}`, 'success');
        updateStats(validItems, { totalSum, totalUnits });
    } else {
        updateStats(null, []);
    }

    if (errors.length > 0) {
        addLog(`⚠️ Обнаружено ошибок в строках: ${errors.length}`, 'warning');
        errors.forEach(err => {
            addLog(`Строка ${err.line}: "${err.raw.substring(0, 60)}" → ${err.reason}`, 'error');
        });
    }

    // Если нет ни валидных, ни ошибок (пустой текст) уже отловили
    if (validItems.length === 0 && errors.length === 0) {
        addLog('Нет данных для обработки', 'info');
    }
}

// Обновление мини-статистики под полем ввода (краткая сводка)
function updateStats(validItems, extra) {
    if (!validItems || validItems.length === 0) {
        quickStatsSpan.innerHTML = `<span>📊 Нет обработанных товаров</span><span>✨ нажмите "Обработать"</span>`;
        return;
    }
    const totalValue = extra?.totalSum || validItems.reduce((acc, it) => acc + (it.price * it.quantity), 0);
    const totalQty = extra?.totalUnits || validItems.reduce((acc, it) => acc + it.quantity, 0);
    const uniqueItems = validItems.length;
    quickStatsSpan.innerHTML = `<span>📦 Товаров: ${uniqueItems}</span><span>💰 Сумма: ${totalValue.toFixed(2)} ₽</span><span>📦 Единиц: ${totalQty.toFixed(2)}</span>`;
}

// --- Вставка из буфера обмена (с запросом разрешения)---
async function pasteFromClipboard() {
    try {
        // Проверяем поддержку clipboard read
        if (!navigator.clipboard || !navigator.clipboard.readText) {
            addLog('❌ Ваш браузер не поддерживает чтение буфера обмена. Вставьте вручную (Ctrl+V).', 'error');
            return;
        }
        const text = await navigator.clipboard.readText();
        if (text.trim() === "") {
            addLog('📭 Буфер обмена пуст. Нечего вставлять.', 'warning');
            return;
        }
        // Вставляем в textarea (заменяем текущий текст или добавляем? - по UX заменяем)
        const previousText = textarea.value;
        textarea.value = text;
        addLog(`📎 Вставлено из буфера обмена (${text.split(/\r?\n/).length} строк).`, 'success');
        // Небольшой подсветка что текст заменен
        if (previousText.trim() !== "" && previousText !== text) {
            addLog(`🔄 Предыдущее содержимое заменено новыми данными из буфера.`, 'info');
        }
    } catch (err) {
        console.error(err);
        addLog('🚫 Ошибка доступа к буферу обмена. Убедитесь, что сайт работает по HTTPS или разрешите доступ.', 'error');
    }
}

// --- Очистка текстового поля ---
function clearTextarea() {
    if (textarea.value.trim() !== "") {
        textarea.value = "";
        addLog('🧽 Поле ввода очищено.', 'info');
        // также можно сбросить быструю статистику, но оставим до след обработки
        quickStatsSpan.innerHTML = `<span>📊 Ожидание данных</span><span>✨ поле очищено</span>`;
    } else {
        addLog('Поле уже пустое', 'info');
    }
}

// --- События кнопок ---
pasteBtn.addEventListener('click', () => {
    pasteFromClipboard();
});
clearTextBtn.addEventListener('click', () => {
    clearTextarea();
});
processBtn.addEventListener('click', () => {
    processWarehouseData();
});
clearLogsBtn.addEventListener('click', () => {
    clearLogs();
});

// Дополнительно: при изменении текста не сбрасываем статистику полностью, но можно подсветить что данные изменены (необязательно)
// добавим live-подсказку при ручном вводе
let typingTimer;
textarea.addEventListener('input', () => {
    // не спамим, просто показываем "не обработано" через 1 секунду бездействия
    if (typingTimer) clearTimeout(typingTimer);
    typingTimer = setTimeout(() => {
        if (textarea.value.trim() !== "") {
            quickStatsSpan.innerHTML = `<span>✏️ Данные изменены</span><span>🔁 нажмите "Обработать"</span>`;
        } else {
            quickStatsSpan.innerHTML = `<span>📭 Пустое поле</span><span>✨ вставьте или введите данные</span>`;
        }
    }, 500);
});

// небольшая инициализация: если поле имеет стартовое содержимое, предложим обработать или подскажем
window.addEventListener('load', () => {
    if (textarea.value.trim() !== "") {
        addLog('📌 Обнаружен текст в редакторе. Нажмите "Обработать" для анализа', 'info');
        quickStatsSpan.innerHTML = `<span>📋 Данные готовы</span><span>⚡ нажмите "Обработать"</span>`;
    }
});