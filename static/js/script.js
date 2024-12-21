document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', function (e) {
        if (this.hash) {
            e.preventDefault();
            const target = document.querySelector(this.hash);
            target.scrollIntoView({behavior: 'smooth', block: 'start'});
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const dropdownBtn = document.querySelector('.dropdown-btn');
    const dropdownContent = document.querySelector('.dropdown-content');

    dropdownBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
    });

    document.addEventListener('click', function () {
        dropdownContent.style.display = 'none';
    });
});
