// Правка 5: XSS-защищенное создание элементов (вместо innerHTML)
function loadComponents(components) {
    const container = document.getElementById('components-list');
    container.innerHTML = ''; // Очищаем безопасно
    components.forEach(c => {
        const div = document.createElement('div');
        div.className = 'component-item';
        const badge = document.createElement('span');
        badge.className = 'component-badge';
        badge.textContent = c.type;
        const text = document.createElement('span');
        text.style.wordBreak = 'break-all';
        text.textContent = c.content; // textContent защищает от XSS!
        div.appendChild(badge);
        div.appendChild(text);
        container.appendChild(div);
    });
}
