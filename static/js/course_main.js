    // You can use JavaScript to toggle the visibility of the categories:

const showCategoriesButton = document.querySelector('.show-categories');
const categories = document.querySelector('.course-categories');

showCategoriesButton.addEventListener('click', () => {
    categories.classList.toggle('show');
});