let currentPath = window.location.pathname;

setInterval(() => {
    fetch("/current_page")
        .then(r => r.json())
        .then(data => {
            if (data.page && data.page !== currentPath) {
                window.location.href = data.page;
            }
        });
}, 500);
