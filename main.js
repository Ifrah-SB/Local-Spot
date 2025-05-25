document.addEventListener("DOMContentLoaded", function () {
  // Get reference to DOM elements
  const categoryFilter = document.getElementById("category-filter");
  const searchInput = document.getElementById("search-input");
  const searchButton = document.getElementById("search-button");
  const businessesContainer = document.getElementById("businesses-container");

  // Load categories
  loadCategories();

  // Load all businesses initially
  loadBusinesses();

  // Event listeners
  categoryFilter.addEventListener("change", filterBusinesses);
  searchButton.addEventListener("click", filterBusinesses);
  searchInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      filterBusinesses();
    }
  });

  // Functions
  async function loadCategories() {
    try {
      const response = await fetch("/api/categories");
      const categories = await response.json();

      categories.forEach((category) => {
        const option = document.createElement("option");
        option.value = category.id;
        option.textContent = category.name;
        categoryFilter.appendChild(option);
      });
    } catch (error) {
      console.error("Error loading categories:", error);
    }
  }

  async function loadBusinesses(categoryId = "", searchQuery = "") {
    // Show loading indicator
    businessesContainer.innerHTML = `
            <div class="col-12 text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;

    try {
      // Build query parameters
      let url = "/api/businesses";
      const params = new URLSearchParams();

      if (categoryId) {
        params.append("category_id", categoryId);
      }

      if (searchQuery) {
        params.append("search", searchQuery);
      }

      if (params.toString()) {
        url += "?" + params.toString();
      }

      const response = await fetch(url);
      const businesses = await response.json();

      // Display businesses
      displayBusinesses(businesses);
    } catch (error) {
      console.error("Error loading businesses:", error);
      businessesContainer.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-danger">Failed to load businesses. Please try again later.</div>
                </div>
            `;
    }
  }

  function displayBusinesses(businesses) {
    // Clear previous content
    businessesContainer.innerHTML = "";

    if (businesses.length === 0) {
      businessesContainer.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-info">No businesses found matching your criteria.</div>
                </div>
            `;
      return;
    }

    businesses.forEach((business) => {
      // Default image if none provided
      let imagePath = "/static/images/placeholder.jpg";
      if (business.image_url) {
        imagePath = `/static/images/${business.image_url}`;
      }

      const businessCard = document.createElement("div");
      businessCard.className = "col-md-4 mb-4";
      businessCard.innerHTML = `
                <div class="card h-100">
                    <img src="${imagePath}" class="card-img-top" alt="${
        business.name
      }" style="height: 200px; object-fit: cover;">
                    <div class="card-body">
                        <h5 class="card-title">${business.name}</h5>
                        <span class="badge bg-primary mb-2">${
                          business.category_name
                        }</span>
                        <p class="card-text">${business.description.substring(
                          0,
                          100
                        )}${business.description.length > 100 ? "..." : ""}</p>
                    </div>
                    <div class="card-footer">
                        <a href="/business/${
                          business.id
                        }" class="btn btn-primary">View Details</a>
                    </div>
                </div>
            `;
      businessesContainer.appendChild(businessCard);
    });
  }

  function filterBusinesses() {
    const categoryId = categoryFilter.value;
    const searchQuery = searchInput.value.trim();
    loadBusinesses(categoryId, searchQuery);
  }
});
