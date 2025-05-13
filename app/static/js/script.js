console.log("script.js loaded");

function toggleContractorFields() {
    const roleSelect = document.getElementById("roleSelect");
    const contractorFields = document.getElementById("contractorFields");
  
    if (!roleSelect || !contractorFields) return;
  
    if (roleSelect.value === "CONTRACTOR") {
      contractorFields.style.display = "block";
    } else {
      contractorFields.style.display = "none";
    }
  }
  
  // Ensure the correct role is shown when the page loads (e.g., on form error resubmission)
  window.addEventListener("DOMContentLoaded", function () {
    toggleContractorFields();
  });
  