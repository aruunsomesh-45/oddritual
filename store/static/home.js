function closeToast(button) {
    const toast = button.closest('.message-toast');
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-20px)';
    setTimeout(() => {
        toast.remove();
        const container = document.getElementById('messages-toast-container');
        if (container && container.children.length === 0) {
            container.remove();
        }
    }, 500);
}
document.addEventListener('DOMContentLoaded', () => {
    const toasts = document.querySelectorAll('.message-toast');
    toasts.forEach(toast => {
        if (toast.classList.contains('success')) {
            setTimeout(() => {
                const closeBtn = toast.querySelector('.toast-close');
                if (closeBtn) closeToast(closeBtn);
            }, 6000);
        }
    });
});
