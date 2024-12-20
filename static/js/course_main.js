const button = document.getElementById('revealButton');
        const hiddenContent = document.getElementById('hiddenContent');

        // Add a click event listener to the button
        button.addEventListener('click', () => {
            // Toggle the visibility of the hidden content
            if (hiddenContent.style.display === 'none') {
                hiddenContent.style.display = 'block';
                button.textContent = "What you'll learn";
            } else {
                hiddenContent.style.display = 'none';
                button.textContent = "What you'll learn";
            }
        });
