// Handle the "Load More" button click
document.getElementById('load-more-btn').addEventListener('click', function() {
    let offset = document.querySelectorAll('.course-card').length; // Get the current number of displayed courses
    fetch(`/api/courses?offset=${offset}&limit=6`)
        .then(response => response.json())
        .then(data => {
            // Add the courses to the page
            let coursesContainer = document.querySelector('.courses-grid');

            data.courses.forEach(course => {
                let courseCard = document.createElement('div');
                courseCard.classList.add('course-card');

                // Create the course card content
                let courseHTML = `
                    <img src="/static/${course.image_url}" alt="${course.name}">
                    <h2>${course.name}</h2>
                    <p>
                        <span>${course.duration}</span> |
                        <span>${course.num_courses} Courses</span> |
                        <span>${course.participants} Participants</span>
                    </p>
                `;

                // Add the button based on the user's role
                if (isAdmin) {
                    // For admins: Show "Edit" and "Delete"
                    courseHTML += `
                        <div class="admin-buttons">
                            <a href="/edit_course/${course.id}" class="edit-course-btn">Edit</a>
                            <form action="/delete_course/${course.id}" method="POST" style="display:inline;">
                                <button type="submit" class="delete-course-btn" onclick="return confirm('Are you sure you want to delete this course?')">Delete</button>
                            </form>
                        </div>
                    `;
                } else {
                    // For users: Show "Join Course"
                    courseHTML += `
                        <a href="/course_main/${course.id}" class="join-btn">
                            <button class="join-course-btn">Join Course</button>
                        </a>
                    `;
                }

                // Add the content to the course card
                courseCard.innerHTML = courseHTML;
                coursesContainer.appendChild(courseCard);
            });

            // Check if there are more courses to load
            if (!data.has_more) {
                // Hide "Load More" and "View All" buttons when no more courses are available
                document.getElementById('load-more-btn').style.display = 'none';
                document.getElementById('view-all-btn').style.display = 'none';
            }

            // Scroll down a little after loading more courses
            window.scrollBy(0, 300); // Scroll down 300px, adjust this value as needed
        })
        .catch(error => {
            console.error('Error loading more courses:', error);
        });
});

// Handle the "View All" button click
document.getElementById('view-all-btn').addEventListener('click', function() {
    // Make an AJAX request to the server to get all courses
    fetch('/api/courses?offset=0&limit=999999')  // Set a very large limit to get all courses
        .then(response => response.json())
        .then(data => {
            // Add the courses to the page
            let coursesContainer = document.querySelector('.courses-grid');

            // Clear existing courses
            coursesContainer.innerHTML = '';

            // Append all the courses returned by the server
            data.courses.forEach(course => {
                let courseCard = document.createElement('div');
                courseCard.classList.add('course-card');

                // Create the course card content
                let courseHTML = `
                    <img src="/static/${course.image_url}" alt="${course.name}">
                    <h2>${course.name}</h2>
                    <p>
                        <span>${course.duration}</span> |
                        <span>${course.num_courses} Courses</span> |
                        <span>${course.participants} Participants</span>
                    </p>
                `;

                // Add the button based on the user's role
                if (isAdmin) {
                    // For admins: Show "Edit" and "Delete"
                    courseHTML += `
                        <div class="admin-buttons">
                            <a href="/edit_course/${course.id}" class="edit-course-btn">Edit</a>
                            <form action="/delete_course/${course.id}" method="POST" style="display:inline;">
                                <button type="submit" class="delete-course-btn" onclick="return confirm('Are you sure you want to delete this course?')">Delete</button>
                            </form>
                        </div>
                    `;
                } else {
                    // For users: Show "Join Course"
                    courseHTML += `
                        <a href="/course_main/${course.id}" class="join-btn">
                            <button class="join-course-btn">Join Course</button>
                        </a>
                    `;
                }

                // Add the content to the course card
                courseCard.innerHTML = courseHTML;
                coursesContainer.appendChild(courseCard);
            });

            // Hide the "View All" and "Load More" buttons after loading all courses
            document.getElementById('load-more-btn').style.display = 'none';
            document.getElementById('view-all-btn').style.display = 'none';
        })
        .catch(error => {
            console.error('Error loading all courses:', error);
        });
});


