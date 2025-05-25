console.log("script.js loaded");

function toggleContractorFields() {
    const roleSelect = document.getElementById("roleSelect");
    const contractorFields = document.getElementById("contractorFields");
  
    if (!roleSelect || !contractorFields) return;
  
    if (roleSelect.value === "Contractor") {
      contractorFields.style.display = "block";
    } else {
      contractorFields.style.display = "none";
    }
  }

  function filterContractorsByType() {
    const selectedType = document.getElementById('business_type').value;
    ['preferred_contractor_id', 'second_preferred_contractor_id'].forEach(selectId => {
      const dropdown = document.getElementById(selectId);
      Array.from(dropdown.options).forEach(opt => {
        if (!opt.value) return; // Skip the default "-- Select --"
        opt.style.display = (opt.dataset.type === selectedType) ? 'block' : 'none';
      });
      dropdown.selectedIndex = 0; // Clear existing selection
    });
  }
  
  
  // Ensure the correct role is shown when the page loads (e.g., on form error resubmission)
  window.addEventListener("DOMContentLoaded", function () {
    toggleContractorFields();
  });
  