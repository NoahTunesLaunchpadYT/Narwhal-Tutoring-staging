document.addEventListener('DOMContentLoaded', function() {
    if (userTutor == "True"){
        console.log("I am a tutor");

        // Availability switch
        var btnAvailable = document.getElementById('btnAvailable');
        var btnUnavailable = document.getElementById('btnUnavailable');
    
        // Change color of availability switch
        function updateButtonStyles(clickedButton, otherButton) { 
            clickedButton.classList.remove('btn-secondary');
            clickedButton.classList.add('btn-primary');
            otherButton.classList.remove('btn-primary');
            otherButton.classList.add('btn-secondary');
        }

        // Save availability boolean to database
        function updateAvailability(available) {
            // Perform asynchronous update here
            var csrfToken = getCSRFToken();  // Implement getCSRFToken function
    
            fetch('/update_availability/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    available: available,
                }),
            })
            .then(response => response.json())
            .then(data => {
                console.log('Availability updated:', data);
                // Update button states or perform additional actions as needed
                btnAvailable.disabled = available;
                btnUnavailable.disabled = !available;
            })
            .catch(error => {
                console.error('Error updating availability:', error);
            });
        }
        
        // Detect availabilty button
        btnAvailable.addEventListener('click', function () {
            console.log(`${btnAvailable} clicked`);
            updateAvailability(true);
            updateButtonStyles(btnAvailable, btnUnavailable);
        });
    
        btnUnavailable.addEventListener('click', function () {
            console.log(`${btnUnavailable} clicked`);
            updateAvailability(false);
            updateButtonStyles(btnUnavailable, btnAvailable);
        });
    } else {
        console.log("I am a client");
    }

    // Bookings Calendar
    var calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        if (userTutor == "True"){
            // Call events where you're the tutor
            console.log("Creating tutor's calendar");
            var calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: 'timeGridWeek',
                timeZone: 'Asia/Singapore',
                locale: 'en-AU',
                slotMinTime: '08:00:00',
                slotMaxTime: '22:00:00',
                events: {
                    url: `/get_availability_and_lessons/${tutorId}`,
                    headers: {
                        'X-CSRFToken': getCSRFToken()
                    },
                },
            });
        } else{
            // Get events where you're the client
            var calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: 'timeGridWeek',
                timeZone: 'Asia/Singapore',
                locale: 'en-AU',
                slotMinTime: '08:00:00',
                slotMaxTime: '22:00:00',
                events: {
                    url: `/get_client_calendar`,
                    headers: {
                        'X-CSRFToken': getCSRFToken()
                    },
                },
            });
        }
        calendar.render();
        // Render list of booked times after calendar renders. 
        setTimeout(function() {
            updateBookedTimesList();
        }, 700);
    }

    // Creates HTML list of booked times for the user
    function updateBookedTimesList() {
        allEvents = calendar.getEvents();

        allEvents.sort(function (a, b) {
            return a.start - b.start;
        });
    
        // Clear the current list
        var timesBookedDiv = document.querySelector('#times-booked');
        timesBookedDiv.innerHTML = '';

        var currentTime = new Date();
        
        if (allEvents){
            console.log("Adding events to list.")
            // Create a new list based on the bookedTimes array
            let selectedMessage = document.createElement('p');
            selectedMessage.textContent = "Booked times: "
            timesBookedDiv.appendChild(selectedMessage);
        
            allEvents.forEach((event) => {
                if(event.title != "Availability") {
                    var eventStart = new Date(event.start);
                    var listItem = document.createElement('li');
                    var date = event.start;
    
                    // Compare event start time with current time
                    if (eventStart < currentTime) {
                        // Time has already happened, color it grey
                        listItem.style.color = 'lightgrey';
                    } else {
                        // It is the next one to happen, color it red
                        listItem.style.color = 'green';
                    }
                    
                    // Extract components from the date
                    var year = date.getUTCFullYear();
                    var month = (date.getUTCMonth() + 1).toString().padStart(2, '0'); // Months are zero-based
                    var day = date.getUTCDate().toString().padStart(2, '0');
                    var hours = date.getUTCHours().toString().padStart(2, '0');
                    var minutes = date.getUTCMinutes().toString().padStart(2, '0');
    
                    // Format the date string manually
                    var formattedTime = `${day}/${month}/${year} ${hours}:${minutes}`;
                    listItem.textContent = formattedTime;
                    timesBookedDiv.appendChild(listItem);
                }
            })
        } else {
            timesBookedDiv.innerHTML = 'You have no lessons booked.';
        }
    }

    // AvailabilityCalendar
    var availabilityCalendarEl = document.getElementById('availability-calendar');
    if (availabilityCalendarEl) {
        var availabilityCalendar = new FullCalendar.Calendar(availabilityCalendarEl, {
            initialView: 'timeGridWeek',
            timeZone: 'Asia/Singapore',
            locale: 'en-AU',
            slotMinTime: '08:00:00',
            slotMaxTime: '22:00:00',
            selectable: true,
            selectMirror: true,
            eventOverlap: false,
            events: {
                url: `/get_availability/${tutorId}`,
                headers: {
                    'X-CSRFToken': getCSRFToken()
                },
                rendering: 'auto',
            },
            eventClick: handleEventClick,
            select: handleSelect,
            longPressDelay: 100,
        });
        availabilityCalendar.render();
    }

    // Rerender both calendars for funsies
    setTimeout(function() {
        calendar.render();
        if (availabilityCalendarEl){
            availabilityCalendar.render();
        }
    });

    // Prevent overlapping and multi-day events. Visually adds event to calendar and saves to db. 
    function handleSelect(arg) {
        // Check if the selected time range overlaps with existing events
        var isOverlapping = availabilityCalendar.getEvents().some(function (existingEvent) {
            return (
                arg.start < existingEvent.end && arg.end > existingEvent.start &&
                existingEvent.groupId === 'availabilityGroup'
            );
        });
    
        if (!isOverlapping && arg.start.getUTCDay() == arg.end.getUTCDay()) {
            // Create a new FullCalendar event with a default title and the selected time range
            var uniqueId = new Date().getTime();
            var newEvent = {
                title: 'Availability',
                groupId: 'availabilityGroup', // Set a common groupId for all availability events
                id: uniqueId,
                daysOfWeek: [arg.start.getUTCDay()],
                startTime: arg.start.toISOString().substring(11, 19),
                endTime: arg.end.toISOString().substring(11, 19)
            };

            console.log(`arg.start: ${arg.start}`)
            console.log(`startTime: ${newEvent.startTime}`);
            console.log(`End: ${newEvent.endTime}`);
            console.log(`Day: ${newEvent.daysOfWeek[0]}`);
            // Add the event to the calendar
            var tempEvent = {
                title: 'Availability',
                groupId: 'availabilityGroup', // Set a common groupId for all availability events
                id: uniqueId,
                start: arg.start,
                end: arg.end
            };

            availabilityCalendar.addEvent(tempEvent);

             // Save the event to the database (you need to implement this part)
            saveEventToDatabase(newEvent);
    
            // Unselect the currently selected time range
            availabilityCalendar.unselect();
        } else {
            alert('Events cant overlap nor span multiple days.');
            availabilityCalendar.unselect();
        }
    }
    
    // Ask user if they want to delete availability
    function handleEventClick(arg) {
        if (confirm('Do you want to delete this availability?')) {
            // Remove the event from the calendar
            arg.event.remove();

            deleteEventFromDatabase(arg.event);
        }
    }

    // Saves availability to database as an Availabiltiy instance.
    function saveEventToDatabase(event) {
        fetch('/save_availability/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify(event),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Event saved to the database:', data);
        })
        .catch(error => {
            console.error('Error saving event to the database:', error);
        });
        console.log('Event ID:', event.id);
    }
    
    // Remove event from database 
    function deleteEventFromDatabase(event) {
        // Check if event.id is defined before making the DELETE request
        if (event.id !== undefined) {
            console.log('Event ID:', event.id);
            fetch(`/delete_availability/${event.id}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                },
            })
            .then(response => response.json())
            .then(data => {
                console.log('Event deleted from the database:', data);
            })
            .catch(error => {
                console.error('Error deleting event from the database:', error);
            });
        } else {
            console.error('Event ID is undefined.');
        }
    }
    
    //Security
    function getCSRFToken() {
        // Retrieve CSRF token from the HTML DOM or any other method you use
        return document.getElementsByName('csrfmiddlewaretoken')[0].value;
    }

    // Navbar
    var tabLinks = document.querySelectorAll('.list-group-item');

    // Url History
    tabLinks.forEach(function (link) {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            var targetTab = this.getAttribute('href').substr(1);
            history.pushState({ tab: targetTab }, null, this.getAttribute('href'));

            setTimeout(function() {
                calendar.render();
                if (availabilityCalendarEl){
                    availabilityCalendar.render();
                }
            }, 200);
        });
    });

    // I think this is for url history
    window.onpopstate = function(event) {
        console.log(event.state.tab)
        showTab(event.state.tab);
    };

    // Shows tab based on url
    var initialTab = window.location.hash.substr(1);
    if (initialTab) {
        showTab(initialTab);
    }

    // Hides all tabs and shows one. 
    function showTab(tabId) {

        tabLinks.forEach(function (link) {
            link.classList.remove('active');
        });

        var tabContent = document.querySelector('.tab-pane');
        tabContent.classList.remove('show', 'active');

        var activeLink = document.querySelector(`.list-group-item[href="#${tabId}"]`);
        var activeTab = document.querySelector(`#${tabId}`);

        activeLink.classList.add('active');
        activeTab.classList.add('show', 'active');
    }
});
