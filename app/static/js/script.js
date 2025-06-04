console.log("script.js loaded");

function toggleContractorFields() {
  const roleDropdown = document.getElementById('roleSelect');
  const selectedOption = roleDropdown.options[roleDropdown.selectedIndex];
  const roleName = selectedOption.dataset.name;
  const contractorFields = document.getElementById('contractorFields');

  if (roleName === 'Contractor') {
    contractorFields.style.display = 'block';
  } else {
    contractorFields.style.display = 'none';
  }
}


function filterContractorsByType() {
  const selectedType = document.getElementById('business_type').value;
  ['preferred_contractor_id', 'second_preferred_contractor_id'].forEach(selectId => {
    const dropdown = document.getElementById(selectId);
    Array.from(dropdown.options).forEach(opt => {
      if (!opt.value) return;
      opt.style.display = (opt.dataset.type === selectedType) ? 'block' : 'none';
    });
    dropdown.selectedIndex = 0;
  });
}

window.addEventListener("DOMContentLoaded", function () {
  toggleContractorFields();

  // ✅ Add this line to enable toggle on role change
  document.getElementById('roleSelect')?.addEventListener('change', toggleContractorFields);

  // Auto-dismiss alerts after 4 seconds
  setTimeout(function () {
    document.querySelectorAll('.alert').forEach(function(alert) {
      alert.classList.add('fade');
      setTimeout(() => alert.remove(), 500);
    });
  }, 4000);
});

async function fetchAddressFromEircode(eircode) {
  if (!eircode) return;

  const apiKey = 'dXKkNR7OtA4jkRBKE5RoKLHSIKwx4twN88jFCZNe-Cc';
  const url = `https://geocode.search.hereapi.com/v1/geocode?q=${encodeURIComponent(eircode)}&apiKey=${apiKey}`;

  try {
    const response = await fetch(url);
    const data = await response.json();

    if (data.items && data.items.length > 0) {
      const result = data.items[0].address;
      document.getElementById("street").value = result.street || '';
      document.getElementById("city").value = result.city || '';
      document.getElementById("county").value = result.county || '';

      if (document.getElementById("country") && !document.getElementById("country").value) {
        document.getElementById("country").value = result.countryName || '';
      }
    } else {
      alert("Address not found for this Eircode.");
    }
  } catch (error) {
    console.error("Address fetch error:", error);
    alert("Error fetching address. Please enter it manually.");
  }
}
