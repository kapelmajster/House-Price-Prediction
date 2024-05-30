document.addEventListener('DOMContentLoaded', function () {
    var cityInput = document.getElementById('cityInput');
    var suggestionsDropdown = document.getElementById('citiesSuggestions');
    var validCities = []; // Array to hold valid city names for validation

    cityInput.addEventListener('keyup', function () {
        var query = this.value;

        if (query.length < 3) {
            suggestionsDropdown.style.display = 'none';
            return;
        }

        fetch('/autocomplete?query=' + query)
            .then(response => response.json())
            .then(data => {
                // Clear any previous suggestions and reset valid cities
                suggestionsDropdown.innerHTML = "";
                validCities = [];
                suggestionsDropdown.style.display = 'block'; // Show the suggestions

                data.forEach(function (item) {
                    // Add item to valid cities
                    validCities.push(item);

                    var suggestionDiv = document.createElement('div');
                    suggestionDiv.innerText = item;
                    suggestionDiv.className = 'suggestion-item';
                    suggestionDiv.onclick = function () {
                        cityInput.value = item;
                        suggestionsDropdown.style.display = 'none';
                        // Reset custom validation message
                        cityInput.setCustomValidity('');
                    };
                    suggestionsDropdown.appendChild(suggestionDiv);
                });
            })
            .catch(error => console.log(error));
    });

    // Custom validation for city input
    cityInput.addEventListener('input', function () {
        if (this.value && !validCities.includes(this.value)) {
            this.setCustomValidity('Please select a valid city from the list.');
        } else {
            this.setCustomValidity('');
        }
    });

    // Form submission validation logic
    document.getElementById('predictionForm').addEventListener('submit', function (event) {
        if (!validCities.includes(cityInput.value)) {
            event.preventDefault(); // Prevent form submission
            // Create a custom validation message
            cityInput.setCustomValidity('Please select a city from the list.');
            cityInput.reportValidity(); // Show validation message
        } else {
            cityInput.setCustomValidity(''); // Clear custom validation message
        }
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', function (e) {
        if (e.target.id !== 'cityInput') {
            suggestionsDropdown.style.display = 'none';
        }
    });
});
