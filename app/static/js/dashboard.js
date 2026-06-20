document.addEventListener('DOMContentLoaded', function () {
    const toggleButton = document.querySelector('.theme-toggle');
    if (!toggleButton) return;
    toggleButton.addEventListener('click', function () {
        document.body.classList.toggle('dark-mode');
        const theme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
        localStorage.setItem('frontend-theme', theme);
    });

    const savedTheme = localStorage.getItem('frontend-theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
    }
});
