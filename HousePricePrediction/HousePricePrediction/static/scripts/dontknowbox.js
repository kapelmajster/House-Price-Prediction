// Script to handle "Don't Know" checkboxes for disabling input fields
document.getElementById('floorAreaUnknown').addEventListener('change', function () {
    var floorAreaInput = document.getElementById('floorAreaInput');
    if (this.checked) {
        floorAreaInput.value = '';  // Clear the value if "Don't Know" is selected
    }
    floorAreaInput.disabled = this.checked;  // Disable or enable the input based on the checkbox
});

// Script to handle property age options
document.addEventListener('DOMContentLoaded', function () {
    // Function to handle property age options
    function handlePropertyAgeOptions() {
        var isSpecificAge = document.getElementById('specificAge').checked;
        var propertyAgeInput = document.getElementById('propertyAgeInput');

        // Enable or disable the property age input based on the selected option
        propertyAgeInput.disabled = !isSpecificAge;

        // If "New Building" or "Don't Know" is selected, clear the input
        if (!isSpecificAge) {
            propertyAgeInput.value = '';
        }
    }

    // Attach event listeners to the radio buttons
    document.querySelectorAll('input[name="property_age_option"]').forEach(radio => {
        radio.addEventListener('change', handlePropertyAgeOptions);
    });

    // Call the function on page load to ensure correct initial state
    handlePropertyAgeOptions();
});






