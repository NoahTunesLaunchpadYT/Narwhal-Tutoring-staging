document.addEventListener('DOMContentLoaded', function () {
    // Function to handle subject filtering
    function filterTutors() {
        var selectedSubjects = [];

        // Iterate over checked checkboxes and collect selected subjects
        var checkboxes = document.querySelectorAll('input[name="subjects"]:checked');
        checkboxes.forEach(function (checkbox) {
            selectedSubjects.push(checkbox.value);
        });

        console.log('Selected Subjects:', selectedSubjects);

        // Show/hide tutors based on selected subjects
        var tutors = document.querySelectorAll('.tutor');
        tutors.forEach(function (tutor) {
            var tutorSubjects = tutor.getAttribute('data-subjects').split(',').map(function (subject) {
                return subject.trim();
            });

            console.log('Tutor Subjects:', tutorSubjects);

            // Check if the tutor has at least one selected subject
            var showTutor = selectedSubjects.every(function (subject) {
                return tutorSubjects.includes(subject);
            });

            console.log('Show Tutor:', showTutor);

            // Show/hide the tutor based on the filtering
            tutor.style.display = showTutor ? 'block' : 'none';
        });
    }

    // Attach change event listener to checkboxes
    var subjectCheckboxes = document.querySelectorAll('input[name="subjects"]');
    subjectCheckboxes.forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            console.log('Checkbox Changed');
            filterTutors();
        });
    });

    console.log('Filtering script loaded');
});
