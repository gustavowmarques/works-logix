document.addEventListener("DOMContentLoaded", function () {
  const roleSelect = document.getElementById("roleSelect");
  const contractorFields = document.getElementById("contractorFields");
  const pmFields = document.getElementById("pmFields");

  function toggleFields() {
    const selectedRole = roleSelect.options[roleSelect.selectedIndex].text.toLowerCase();
    contractorFields.style.display = selectedRole.includes("contractor") ? "block" : "none";
    pmFields.style.display = selectedRole.includes("property manager") ? "block" : "none";
  }

  if (roleSelect) {
    roleSelect.addEventListener("change", toggleFields);
    toggleFields(); // Run once on page load
  }

  // Auto-dismiss alerts after 4 seconds
  setTimeout(function () {
    document.querySelectorAll('.alert').forEach(function(alert) {
      alert.classList.add('fade');
      setTimeout(() => alert.remove(), 500);
    });
  }, 4000);
});

// Filters contractor dropdowns by selected business type
function filterContractorsByType() {
  const selectedType = document.getElementById('business_type').value;
  ['preferred_contractor_id', 'second_preferred_contractor_id'].forEach(selectId => {
    const dropdown = document.getElementById(selectId);
    Array.from(dropdown.options).forEach(opt => {
      if (!opt.value) return; // Skip the default "-- Select --"
      opt.style.display = opt.getAttribute('data-type') === selectedType ? 'block' : 'none';
    });
  });
}

// Fetch address based on Eircode
function fetchAddressFromEircode() {
  const eircode = document.getElementById("eircode").value;
  const addressField = document.getElementById("address");

  fetch(`https://api.eircode.ie/address/${eircode}`)
    .then(response => response.json())
    .then(data => {
      addressField.value = data.address || '';
    })
    .catch(error => {
      console.error("Failed to fetch address:", error);
    });
}
