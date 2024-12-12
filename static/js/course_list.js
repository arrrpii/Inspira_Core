// document.addEventListener('DOMContentLoaded', function() {
//     const allButton = document.getElementById('all');
//     const categoryButton = document.querySelector('.dropdown button');
//     const dropdownMenu = document.querySelector('.dropdown-menu');
//
//     // Toggle dropdown menu visibility
//     categoryButton.addEventListener('click', () => {
//         dropdownMenu.classList.toggle('show');
//     });
//
//     // Close dropdown when clicking outside
//     window.addEventListener('click', (e) => {
//         if (!e.target.matches('.dropdown button')) {
//             dropdownMenu.classList.remove('show');
//         }
//     });
//
//     // Button functionality for all button
//     allButton.addEventListener('click', () => {
//         alert('All courses clicked');
//     });
//
//     // Button functionality for join course button
//     const joinButtons = document.querySelectorAll('.join-btn');
//     joinButtons.forEach(button => {
//         button.addEventListener('click', () => {
//             alert('Joining the course...');
//         });
//
// <button id="join-course-btn" class="join-course-btn">Join Course</button>
//
// document.getElementById("startButton").addEventListener("click", function () {
//     window.location.href = "course_list.html";
// });
//
//     // script.js
// function joinCourse(courseId) {
//     // Replace 'course_details.html' with the actual URL of the target page
//     window.location.href = 'course_main.html';
//     window.location.href = `courses.html?courseId=${courseId}`;
// }
// const joinButtons = document.querySelectorAll('.join-btn');
//
// joinButtons.forEach(button => {
//     button.addEventListener('click', () => {
//         const courseId = button.getAttribute('data-course-id');
//         joinCourse(courseId);
//     });
// });



