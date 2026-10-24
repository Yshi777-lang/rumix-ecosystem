with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

fix_script = '''
<script>
// Перехватчик для кнопки "Диагностика" из меню (бэкенд)
document.addEventListener('click', function(e) {
    // Ищем элемент, который содержит текст "Диагностика"
    let btn = e.target.closest('.menu-item, .btn-action, div, button');
    if (btn && btn.innerText && btn.innerText.includes('Диагностика')) {
        e.preventDefault();
        e.stopPropagation();
        if (typeof openSelftest === 'function') {
            openSelftest();
        } else {
            console.error('openSelftest not found');
        }
        return false;
    }
}, true);
</script>
'''

if 'inject_diagnostic_fix' not in html:
    html = html.replace('</body>', fix_script + '\n</body>')
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('Перехватчик добавлен.')
else:
    print('Перехватчик уже есть.')
