const API_BASE_URL = "http://127.0.0.1:8000";

let currentUser = null;
let currentEditCarId = null;


// =====================================================
// BASIC HELPERS
// =====================================================

function getToken() {
    return localStorage.getItem("access_token");
}

function isLoggedIn() {
    return !!getToken();
}

function openModal(id) {
    const modal = document.getElementById(id);

    if (modal) {
        modal.classList.remove("hidden");
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);

    if (modal) {
        modal.classList.add("hidden");
    }
}

function scrollToSection(id) {
    const element = document.getElementById(id);

    if (element) {
        element.scrollIntoView({
            behavior: "smooth"
        });
    }
}

function formatPrice(price) {
    return "Rs " + Number(price).toLocaleString("en-PK");
}

function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getInitials(name) {
    if (!name) {
        return "G";
    }

    const parts = name.trim().split(/\s+/);

    if (parts.length === 1) {
        return parts[0].charAt(0).toUpperCase();
    }

    return (
        parts[0].charAt(0) +
        parts[parts.length - 1].charAt(0)
    ).toUpperCase();
}


// =====================================================
// PROFILE
// =====================================================

async function loadCurrentUser() {
    if (!getToken()) {
        currentUser = null;
        updateProfileUI();
        return;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/auth/me`,
            {
                headers: {
                    "Authorization":
                        `Bearer ${getToken()}`
                }
            }
        );

        const data = await response.json();

        if (!response.ok) {
            localStorage.removeItem(
                "access_token"
            );

            currentUser = null;

            updateProfileUI();

            return;
        }

        currentUser = data;

        updateProfileUI();

    } catch (error) {
        console.error(
            "Profile loading error:",
            error
        );
    }
}

function updateProfileUI() {
    const profileName =
        document.getElementById("profileName");

    const profileAvatar =
        document.getElementById("profileAvatar");

    const profileAvatarLarge =
        document.getElementById("profileAvatarLarge");

    const profileMenuName =
        document.getElementById("profileMenuName");

    const profileMenuEmail =
        document.getElementById("profileMenuEmail");

    const loginItem =
        document.getElementById("profileLoginBtn");

    const logoutItem =
        document.getElementById("profileLogoutBtn");

    if (!currentUser) {

        profileName.textContent = "Guest";

        profileAvatar.textContent = "G";

        profileAvatarLarge.textContent = "G";

        profileMenuName.textContent =
            "Guest";

        profileMenuEmail.textContent =
            "Not logged in";

        loginItem.classList.remove("hidden");
        logoutItem.classList.add("hidden");

        return;
    }

    const initials =
        getInitials(
            currentUser.name
        );

    profileName.textContent =
        currentUser.name;

    profileAvatar.textContent =
        initials;

    profileAvatarLarge.textContent =
        initials;

    profileMenuName.textContent =
        currentUser.name;

    profileMenuEmail.textContent =
        currentUser.email;

    loginItem.classList.add("hidden");
    logoutItem.classList.remove("hidden");
}

function toggleProfileMenu() {
    const menu =
        document.getElementById("profileMenu");

    menu.classList.toggle("hidden");
}

function closeProfileMenu() {
    document
        .getElementById("profileMenu")
        .classList.add("hidden");
}


// =====================================================
// AUTH
// =====================================================

function showLogin() {
    document.getElementById("authTitle").textContent =
        "Welcome back";

    document.getElementById("authSubtitle").textContent =
        "Login to continue.";

    document
        .getElementById("loginForm")
        .classList.remove("hidden");

    document
        .getElementById("registerForm")
        .classList.add("hidden");

    document
        .getElementById("loginTab")
        .classList.add("active");

    document
        .getElementById("registerTab")
        .classList.remove("active");

    document.getElementById(
        "authMessage"
    ).textContent = "";

    openModal("authModal");
}

function showRegister() {
    document.getElementById(
        "authTitle"
    ).textContent =
        "Create your account";

    document.getElementById(
        "authSubtitle"
    ).textContent =
        "Create an account to sell cars.";

    document
        .getElementById("loginForm")
        .classList.add("hidden");

    document
        .getElementById("registerForm")
        .classList.remove("hidden");

    document
        .getElementById("loginTab")
        .classList.remove("active");

    document
        .getElementById("registerTab")
        .classList.add("active");

    document.getElementById(
        "authMessage"
    ).textContent = "";

    openModal("authModal");
}

async function loginUser(event) {
    event.preventDefault();

    const email =
        document
            .getElementById("loginEmail")
            .value
            .trim();

    const password =
        document.getElementById(
            "loginPassword"
        ).value;

    const message =
        document.getElementById(
            "authMessage"
        );

    message.textContent =
        "Logging in...";

    const formData =
        new URLSearchParams();

    formData.append(
        "username",
        email
    );

    formData.append(
        "password",
        password
    );

    try {
        const response = await fetch(
            `${API_BASE_URL}/auth/login`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/x-www-form-urlencoded"
                },

                body: formData
            }
        );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "Login failed"
            );
        }

        localStorage.setItem(
            "access_token",
            data.access_token
        );

        await loadCurrentUser();

        message.textContent =
            "Login successful.";

        await loadMyListings();

        setTimeout(() => {
            closeModal("authModal");
        }, 500);

    } catch (error) {
        message.textContent =
            error.message;
    }
}

async function registerUser(event) {
    event.preventDefault();

    const name =
        document
            .getElementById("registerName")
            .value
            .trim();

    const email =
        document
            .getElementById("registerEmail")
            .value
            .trim();

    const password =
        document.getElementById(
            "registerPassword"
        ).value;

    const message =
        document.getElementById(
            "authMessage"
        );

    message.textContent =
        "Creating account...";

    try {
        const response = await fetch(
            `${API_BASE_URL}/auth/register`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    name,
                    email,
                    password
                })
            }
        );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "Registration failed"
            );
        }

        message.textContent =
            "Account created. You can now login.";

        document
            .getElementById(
                "registerForm"
            )
            .reset();

        setTimeout(() => {
            showLogin();
        }, 800);

    } catch (error) {
        message.textContent =
            error.message;
    }
}

function logoutUser() {
    localStorage.removeItem(
        "access_token"
    );

    currentUser = null;

    updateProfileUI();

    closeProfileMenu();

    document.getElementById(
        "listingCount"
    ).textContent =
        "0 Listings";

    loadMyListings();
}


// =====================================================
// LOAD CARS
// =====================================================

async function loadCars() {

    const container =
        document.getElementById(
            "carsContainer"
        );

    container.innerHTML = `
        <div class="my-listings-empty">
            <p>Loading cars...</p>
        </div>
    `;

    try {
        const response = await fetch(
            `${API_BASE_URL}/cars/?page=1&limit=100&sort_by=id&order=desc`
        );

        const cars =
            await response.json();

        if (!response.ok) {
            throw new Error(
                cars.detail ||
                "Failed to load cars"
            );
        }

        // Load details/images for the cards
        const detailedCars =
            await Promise.all(
                cars.map(async car => {

                    try {
                        const detailResponse =
                            await fetch(
                                `${API_BASE_URL}/cars/${car.id}`
                            );

                        if (detailResponse.ok) {
                            return await detailResponse.json();
                        }
                    } catch (error) {
                        console.log(
                            "Image/details load failed",
                            error
                        );
                    }

                    return car;
                })
            );

        renderCars(
            detailedCars,
            container
        );

    } catch (error) {

        container.innerHTML = `
            <div class="my-listings-empty">
                <h3>Unable to load cars</h3>

                <p>
                    ${escapeHtml(
                        error.message
                    )}
                </p>
            </div>
        `;
    }
}


// =====================================================
// RENDER BROWSE CARDS
// =====================================================

function renderCars(
    cars,
    container
) {
    if (!cars || cars.length === 0) {

        container.innerHTML = `
            <div class="my-listings-empty">

                <h3>No cars found</h3>

                <p>
                    Try different search filters.
                </p>

            </div>
        `;

        return;
    }

    container.innerHTML =
        cars.map(car => {

            let imageHtml = `
                <div class="no-image">
                    ${escapeHtml(
                        car.make
                    )}
                </div>
            `;

            if (
                car.images &&
                car.images.length > 0
            ) {
                imageHtml = `
                    <img
                        src="${escapeHtml(
                            car.images[0].image_url
                        )}"
                        alt="${escapeHtml(
                            car.make
                        )} ${escapeHtml(
                            car.model
                        )}"
                    >
                `;
            }

            return `
                <article class="car-card">

                    <div class="car-image">
                        ${imageHtml}
                    </div>

                    <div class="car-content">

                        <div class="car-top">

                            <div>

                                <div class="car-title">
                                    ${escapeHtml(
                                        car.make
                                    )}
                                    ${escapeHtml(
                                        car.model
                                    )}
                                </div>

                                <div class="car-year">
                                    ${escapeHtml(
                                        car.year
                                    )}
                                </div>

                            </div>

                            <div class="car-location">
                                ${escapeHtml(
                                    car.city
                                )}
                            </div>

                        </div>

                        <div class="car-price">
                            ${formatPrice(
                                car.price
                            )}
                        </div>

                        <div class="car-specs">

                            <span class="car-spec">
                                ${Number(
                                    car.mileage
                                ).toLocaleString()} km
                            </span>

                            <span class="car-spec">
                                ${escapeHtml(
                                    car.fuel_type
                                )}
                            </span>

                            <span class="car-spec">
                                ${escapeHtml(
                                    car.transmission
                                )}
                            </span>

                        </div>

                        <div class="car-actions">

                            <button
                                class="primary-btn"
                                onclick="showCarDetails(${car.id})"
                            >
                                View Details
                            </button>

                        </div>

                    </div>

                </article>
            `;

        }).join("");
}


// =====================================================
// SEARCH
// =====================================================

async function searchCars() {

    const params =
        new URLSearchParams();

    const search =
        document
            .getElementById(
                "searchInput"
            )
            .value
            .trim();

    const city =
        document
            .getElementById(
                "cityFilter"
            )
            .value
            .trim();

    const fuel =
        document
            .getElementById(
                "fuelFilter"
            )
            .value;

    const transmission =
        document
            .getElementById(
                "transmissionFilter"
            )
            .value;

    const minPrice =
        document
            .getElementById(
                "minPrice"
            )
            .value;

    const maxPrice =
        document
            .getElementById(
                "maxPrice"
            )
            .value;

    const minYear =
        document
            .getElementById(
                "minYear"
            )
            .value;

    const maxYear =
        document
            .getElementById(
                "maxYear"
            )
            .value;

    const minMileage =
        document
            .getElementById(
                "minMileage"
            )
            .value;

    const maxMileage =
        document
            .getElementById(
                "maxMileage"
            )
            .value;

    const sortBy =
        document
            .getElementById(
                "sortBy"
            )
            .value;

    const sortOrder =
        document
            .getElementById(
                "sortOrder"
            )
            .value;


    if (search) {
        params.append(
            "search",
            search
        );
    }

    if (city) {
        params.append(
            "city",
            city
        );
    }

    if (fuel) {
        params.append(
            "fuel_type",
            fuel
        );
    }

    if (transmission) {
        params.append(
            "transmission",
            transmission
        );
    }

    if (minPrice) {
        params.append(
            "min_price",
            minPrice
        );
    }

    if (maxPrice) {
        params.append(
            "max_price",
            maxPrice
        );
    }

    if (minYear) {
        params.append(
            "min_year",
            minYear
        );
    }

    if (maxYear) {
        params.append(
            "max_year",
            maxYear
        );
    }

    if (minMileage) {
        params.append(
            "min_mileage",
            minMileage
        );
    }

    if (maxMileage) {
        params.append(
            "max_mileage",
            maxMileage
        );
    }

    params.append(
        "sort_by",
        sortBy
    );

    params.append(
        "order",
        sortOrder
    );

    params.append(
        "page",
        "1"
    );

    params.append(
        "limit",
        "100"
    );

    const container =
        document.getElementById(
            "carsContainer"
        );

    const status =
        document.getElementById(
            "searchStatus"
        );

    container.innerHTML = `
        <div class="my-listings-empty">
            <p>Searching cars...</p>
        </div>
    `;

    status.textContent =
        "Searching...";

    try {
        const response =
            await fetch(
                `${API_BASE_URL}/cars/?${params.toString()}`
            );

        const cars =
            await response.json();

        if (!response.ok) {
            throw new Error(
                cars.detail ||
                "Search failed"
            );
        }

        const detailedCars =
            await Promise.all(
                cars.map(async car => {

                    try {
                        const detailResponse =
                            await fetch(
                                `${API_BASE_URL}/cars/${car.id}`
                            );

                        if (
                            detailResponse.ok
                        ) {
                            return await detailResponse.json();
                        }

                    } catch (error) {
                        console.log(error);
                    }

                    return car;
                })
            );

        renderCars(
            detailedCars,
            container
        );

        status.textContent =
            `${cars.length} car${
                cars.length === 1
                    ? ""
                    : "s"
            } found`;

        scrollToSection(
            "browse"
        );

    } catch (error) {

        status.textContent =
            "Search failed";

        container.innerHTML = `
            <div class="my-listings-empty">

                <h3>
                    Search failed
                </h3>

                <p>
                    ${escapeHtml(
                        error.message
                    )}
                </p>

            </div>
        `;
    }
}

function clearFilters() {

    document.getElementById(
        "searchInput"
    ).value = "";

    document.getElementById(
        "cityFilter"
    ).value = "";

    document.getElementById(
        "fuelFilter"
    ).value = "";

    document.getElementById(
        "transmissionFilter"
    ).value = "";

    document.getElementById(
        "minPrice"
    ).value = "";

    document.getElementById(
        "maxPrice"
    ).value = "";

    document.getElementById(
        "minYear"
    ).value = "";

    document.getElementById(
        "maxYear"
    ).value = "";

    document.getElementById(
        "minMileage"
    ).value = "";

    document.getElementById(
        "maxMileage"
    ).value = "";

    document.getElementById(
        "sortBy"
    ).value = "id";

    document.getElementById(
        "sortOrder"
    ).value = "desc";

    document.getElementById(
        "searchStatus"
    ).textContent = "";

    loadCars();
}


// =====================================================
// CAR DETAILS
// =====================================================

async function showCarDetails(
    carId
) {

    const content =
        document.getElementById(
            "detailsContent"
        );

    content.innerHTML = `
        <div class="my-listings-empty">
            <p>Loading details...</p>
        </div>
    `;

    openModal(
        "detailsModal"
    );

    try {
        const response =
            await fetch(
                `${API_BASE_URL}/cars/${carId}`
            );

        const car =
            await response.json();

        if (!response.ok) {
            throw new Error(
                car.detail ||
                "Unable to load details"
            );
        }

        let imageHtml = `
            <div class="details-no-image">
                No image available
            </div>
        `;

        if (
            car.images &&
            car.images.length > 0
        ) {
            imageHtml = `
                <div class="details-gallery">

                    ${car.images.map(
                        image => `
                            <img
                                class="details-image"
                                src="${escapeHtml(
                                    image.image_url
                                )}"
                                alt="${escapeHtml(
                                    car.make
                                )} ${escapeHtml(
                                    car.model
                                )}"
                            >
                        `
                    ).join("")}

                </div>
            `;
        }

        content.innerHTML = `

            ${imageHtml}

            <div class="details-badge">
                LISTING #${car.id}
            </div>

            <h2 class="details-title">
                ${escapeHtml(
                    car.make
                )}
                ${escapeHtml(
                    car.model
                )}
                ${escapeHtml(
                    car.year
                )}
            </h2>

            <div class="details-price">
                ${formatPrice(
                    car.price
                )}
            </div>

            <div class="details-grid">

                <div class="detail-item">
                    <span>Mileage</span>

                    <strong>
                        ${Number(
                            car.mileage
                        ).toLocaleString()} km
                    </strong>
                </div>

                <div class="detail-item">
                    <span>Fuel</span>

                    <strong>
                        ${escapeHtml(
                            car.fuel_type
                        )}
                    </strong>
                </div>

                <div class="detail-item">
                    <span>Fuel Average</span>

                    <strong>
                        ${escapeHtml(
                            car.fuel_average
                        )} km/l
                    </strong>
                </div>

                <div class="detail-item">
                    <span>Transmission</span>

                    <strong>
                        ${escapeHtml(
                            car.transmission
                        )}
                    </strong>
                </div>

                <div class="detail-item">
                    <span>City</span>

                    <strong>
                        ${escapeHtml(
                            car.city
                        )}
                    </strong>
                </div>

                <div class="detail-item">
                    <span>Seller</span>

                    <strong>
                        ${escapeHtml(
                            car.seller_name ||
                            "Unknown Seller"
                        )}
                    </strong>
                </div>

                <div class="detail-item">
                    <span>Contact</span>

                    <strong>
                        ${escapeHtml(
                            car.contact_number
                        )}
                    </strong>
                </div>

            </div>

            <div class="details-description">

                <strong>
                    Description
                </strong>

                <p>
                    ${escapeHtml(
                        car.description ||
                        "No description provided."
                    )}
                </p>

            </div>
        `;

    } catch (error) {

        content.innerHTML = `
            <div class="my-listings-empty">

                <h3>
                    Unable to load details
                </h3>

                <p>
                    ${escapeHtml(
                        error.message
                    )}
                </p>

            </div>
        `;
    }
}


// =====================================================
// MY LISTINGS
// =====================================================

async function loadMyListings() {

    const container =
        document.getElementById(
            "myListingsContainer"
        );

    const count =
        document.getElementById(
            "listingCount"
        );

    if (!isLoggedIn()) {

        count.textContent =
            "0 Listings";

        container.innerHTML = `
            <div class="my-listings-empty">

                <h3>
                    Login to see your listings
                </h3>

                <p>
                    Cars you post will appear here.
                </p>

                <button
                    class="primary-btn"
                    onclick="showLogin()"
                >
                    Login
                </button>

            </div>
        `;

        return;
    }

    container.innerHTML = `
        <div class="my-listings-empty">
            <p>
                Loading your listings...
            </p>
        </div>
    `;

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/cars/my-listings`,
                {
                    headers: {
                        "Authorization":
                            `Bearer ${getToken()}`
                    }
                }
            );

        const cars =
            await response.json();

        if (!response.ok) {

            if (
                response.status === 401
            ) {
                logoutUser();

                throw new Error(
                    "Your session has expired."
                );
            }

            throw new Error(
                cars.detail ||
                "Unable to load listings"
            );
        }

        count.textContent =
            `${cars.length} ${
                cars.length === 1
                    ? "Listing"
                    : "Listings"
            }`;

        if (!cars.length) {

            container.innerHTML = `
                <div class="my-listings-empty">

                    <h3>
                        You haven't posted a car yet
                    </h3>

                    <p>
                        Sell your first car on AutoMarket.
                    </p>

                    <button
                        class="primary-btn"
                        onclick="openSellCar()"
                    >
                        + Post Your First Car
                    </button>

                </div>
            `;

            return;
        }

        const detailedCars =
            await Promise.all(
                cars.map(
                    async car => {

                        try {

                            const response =
                                await fetch(
                                    `${API_BASE_URL}/cars/${car.id}`
                                );

                            if (
                                response.ok
                            ) {
                                return await response.json();
                            }

                        } catch (error) {
                            console.log(error);
                        }

                        return car;
                    }
                )
            );

        renderMyListings(
            detailedCars,
            container
        );

    } catch (error) {

        count.textContent =
            "0 Listings";

        container.innerHTML = `
            <div class="my-listings-empty">

                <h3>
                    Unable to load listings
                </h3>

                <p>
                    ${escapeHtml(
                        error.message
                    )}
                </p>

                <button
                    class="outline-btn"
                    onclick="loadMyListings()"
                >
                    Try Again
                </button>

            </div>
        `;
    }
}

function renderMyListings(
    cars,
    container
) {

    container.innerHTML =
        cars.map(car => {

            let imageHtml = `
                <div class="no-image">
                    ${escapeHtml(
                        car.make
                    )}
                </div>
            `;

            if (
                car.images &&
                car.images.length > 0
            ) {
                imageHtml = `
                    <img
                        src="${escapeHtml(
                            car.images[0].image_url
                        )}"
                        alt="${escapeHtml(
                            car.make
                        )} ${escapeHtml(
                            car.model
                        )}"
                    >
                `;
            }

            return `
                <article class="car-card">

                    <div class="car-image">
                        ${imageHtml}
                    </div>

                    <div class="car-content">

                        <div class="car-top">

                            <div>

                                <div class="car-title">
                                    ${escapeHtml(
                                        car.make
                                    )}
                                    ${escapeHtml(
                                        car.model
                                    )}
                                </div>

                                <div class="car-year">
                                    ${escapeHtml(
                                        car.year
                                    )}
                                </div>

                            </div>

                            <div class="car-location">
                                ${escapeHtml(
                                    car.city
                                )}
                            </div>

                        </div>

                        <div class="car-price">
                            ${formatPrice(
                                car.price
                            )}
                        </div>

                        <div class="car-specs">

                            <span class="car-spec">
                                ${Number(
                                    car.mileage
                                ).toLocaleString()} km
                            </span>

                            <span class="car-spec">
                                ${escapeHtml(
                                    car.fuel_type
                                )}
                            </span>

                            <span class="car-spec">
                                ${escapeHtml(
                                    car.transmission
                                )}
                            </span>

                        </div>

                        <div class="car-actions">

                            <button
                                class="primary-btn"
                                onclick="showCarDetails(${car.id})"
                            >
                                View Details
                            </button>

                            <button
                                class="outline-btn"
                                onclick="openEditCar(${car.id})"
                            >
                                Edit
                            </button>

                            <button
                                class="delete-btn"
                                onclick="deleteMyCar(${car.id})"
                            >
                                Delete
                            </button>

                        </div>

                    </div>

                </article>
            `;

        }).join("");
}


// =====================================================
// OPEN EDIT MODAL
// =====================================================

async function openEditCar(
    carId
) {

    if (!isLoggedIn()) {
        showLogin();
        return;
    }

    currentEditCarId =
        carId;

    const message =
        document.getElementById(
            "editCarMessage"
        );

    message.textContent =
        "Loading listing...";

    openModal(
        "editCarModal"
    );

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/cars/${carId}`
            );

        const car =
            await response.json();

        if (!response.ok) {
            throw new Error(
                car.detail ||
                "Unable to load listing"
            );
        }

        document.getElementById(
            "editCarId"
        ).value = car.id;

        document.getElementById(
            "editMake"
        ).value = car.make || "";

        document.getElementById(
            "editModel"
        ).value = car.model || "";

        document.getElementById(
            "editYear"
        ).value = car.year || "";

        document.getElementById(
            "editPrice"
        ).value = car.price || "";

        document.getElementById(
            "editMileage"
        ).value = car.mileage || "";

        document.getElementById(
            "editFuelAverage"
        ).value =
            car.fuel_average || "";

        document.getElementById(
            "editFuelType"
        ).value =
            car.fuel_type || "";

        document.getElementById(
            "editTransmission"
        ).value =
            car.transmission || "";

        document.getElementById(
            "editCity"
        ).value =
            car.city || "";

        document.getElementById(
            "editContactNumber"
        ).value =
            car.contact_number || "";

        document.getElementById(
            "editDescription"
        ).value =
            car.description || "";

        document.getElementById(
            "editImageMessage"
        ).textContent = "";

        await loadEditImages(
            car.id
        );

        message.textContent = "";

    } catch (error) {

        message.textContent =
            error.message;
    }
}


// =====================================================
// LOAD EDIT IMAGES
// =====================================================

async function loadEditImages(
    carId
) {

    const container =
        document.getElementById(
            "editImagesContainer"
        );

    container.innerHTML = `
        <div class="image-management-empty">
            Loading pictures...
        </div>
    `;

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/cars/${carId}/images`
            );

        const images =
            await response.json();

        if (!response.ok) {
            throw new Error(
                images.detail ||
                "Unable to load images"
            );
        }

        if (!images.length) {

            container.innerHTML = `
                <div class="image-management-empty">
                    No pictures uploaded yet.
                </div>
            `;

            return;
        }

        container.innerHTML =
            images.map(image => `
                <div class="edit-image-card">

                    <img
                        src="${escapeHtml(
                            image.image_url
                        )}"
                        alt="Car picture"
                    >

                    <div class="edit-image-actions">

                        <input
                            type="file"
                            accept="image/*"
                            id="replaceImageInput-${image.id}"
                            class="hidden"
                            onchange="replaceCarImage(${carId}, ${image.id}, this.files[0])"
                        >

                        <button
                            type="button"
                            class="outline-btn"
                            onclick="document.getElementById('replaceImageInput-${image.id}').click()"
                        >
                            Replace
                        </button>

                        <button
                            type="button"
                            class="delete-btn"
                            onclick="deleteCarImage(${carId}, ${image.id})"
                        >
                            Delete
                        </button>

                    </div>

                </div>
            `).join("");

    } catch (error) {

        container.innerHTML = `
            <div class="image-management-empty">
                ${escapeHtml(
                    error.message
                )}
            </div>
        `;
    }
}


// =====================================================
// ADD NEW IMAGE
// =====================================================

async function uploadNewEditImage() {

    const input =
        document.getElementById(
            "editNewImage"
        );

    const message =
        document.getElementById(
            "editImageMessage"
        );

    if (
        !input.files ||
        input.files.length === 0
    ) {
        message.textContent =
            "Please choose an image first.";

        return;
    }

    if (!currentEditCarId) {
        return;
    }

    const formData =
        new FormData();

    formData.append(
        "file",
        input.files[0]
    );

    message.textContent =
        "Uploading picture...";

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/cars/${currentEditCarId}/images`,
                {
                    method: "POST",

                    headers: {
                        "Authorization":
                            `Bearer ${getToken()}`
                    },

                    body: formData
                }
            );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "Image upload failed"
            );
        }

        input.value = "";

        message.textContent =
            "Picture uploaded successfully.";

        await loadEditImages(
            currentEditCarId
        );

        await loadCars();
        await loadMyListings();

    } catch (error) {

        message.textContent =
            error.message;
    }
}


// =====================================================
// REPLACE IMAGE
// =====================================================

async function replaceCarImage(
    carId,
    imageId,
    file
) {

    const message =
        document.getElementById(
            "editImageMessage"
        );

    if (!file) {
        return;
    }

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );

    message.textContent =
        "Replacing picture...";

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/cars/images/${carId}/${imageId}`,
                {
                    method: "PATCH",

                    headers: {
                        "Authorization":
                            `Bearer ${getToken()}`
                    },

                    body: formData
                }
            );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "Image replacement failed"
            );
        }

        message.textContent =
            "Picture replaced successfully.";

        await loadEditImages(
            carId
        );

        await loadCars();
        await loadMyListings();

    } catch (error) {

        message.textContent =
            error.message;
    }
}


// =====================================================
// DELETE IMAGE
// =====================================================

async function deleteCarImage(
    carId,
    imageId
) {

    const confirmed =
        confirm(
            "Delete this car picture?"
        );

    if (!confirmed) {
        return;
    }

    const message =
        document.getElementById(
            "editImageMessage"
        );

    message.textContent =
        "Deleting picture...";

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/cars/images/${carId}/${imageId}`,
                {
                    method: "DELETE",

                    headers: {
                        "Authorization":
                            `Bearer ${getToken()}`
                    }
                }
            );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "Image deletion failed"
            );
        }

        message.textContent =
            "Picture deleted successfully.";

        await loadEditImages(
            carId
        );

        await loadCars();
        await loadMyListings();

    } catch (error) {

        message.textContent =
            error.message;
    }
}


// =====================================================
// UPDATE CAR DETAILS
// =====================================================

async function updateCar(
    event
) {

    event.preventDefault();

    const carId =
        document.getElementById(
            "editCarId"
        ).value;

    const message =
        document.getElementById(
            "editCarMessage"
        );

    const updatedCar = {

        make:
            document.getElementById(
                "editMake"
            ).value.trim(),

        model:
            document.getElementById(
                "editModel"
            ).value.trim(),

        year:
            Number(
                document.getElementById(
                    "editYear"
                ).value
            ),

        price:
            Number(
                document.getElementById(
                    "editPrice"
                ).value
            ),

        mileage:
            Number(
                document.getElementById(
                    "editMileage"
                ).value
            ),

        fuel_type:
            document.getElementById(
                "editFuelType"
            ).value,

        fuel_average:
            Number(
                document.getElementById(
                    "editFuelAverage"
                ).value
            ),

        transmission:
            document.getElementById(
                "editTransmission"
            ).value,

        city:
            document.getElementById(
                "editCity"
            ).value.trim(),

        contact_number:
            document.getElementById(
                "editContactNumber"
            ).value.trim(),

        description:
            document.getElementById(
                "editDescription"
            ).value.trim()
    };

    message.textContent =
        "Saving changes...";

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/cars/${carId}`,
                {
                    method: "PUT",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Authorization":
                            `Bearer ${getToken()}`
                    },

                    body:
                        JSON.stringify(
                            updatedCar
                        )
                }
            );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "Unable to update car."
            );
        }

        message.textContent =
            "Car details updated successfully.";

        await loadCars();
        await loadMyListings();

        setTimeout(() => {
            closeModal(
                "editCarModal"
            );
        }, 600);

    } catch (error) {

        message.textContent =
            error.message;
    }
}


// =====================================================
// DELETE CAR
// =====================================================

async function deleteMyCar(
    carId
) {

    const confirmed =
        confirm(
            "Are you sure you want to delete this car listing and its pictures?"
        );

    if (!confirmed) {
        return;
    }

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/cars/${carId}`,
                {
                    method: "DELETE",

                    headers: {
                        "Authorization":
                            `Bearer ${getToken()}`
                    }
                }
            );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "Unable to delete car."
            );
        }

        alert(
            "Car listing deleted successfully."
        );

        await loadCars();
        await loadMyListings();

    } catch (error) {

        alert(
            error.message
        );
    }
}


// =====================================================
// SELL CAR
// =====================================================

function openSellCar() {

    if (!isLoggedIn()) {
        showLogin();
        return;
    }

    document.getElementById(
        "sellMessage"
    ).textContent = "";

    openModal(
        "sellModal"
    );
}

async function publishCar(
    event
) {

    event.preventDefault();

    if (!isLoggedIn()) {
        showLogin();
        return;
    }

    const message =
        document.getElementById(
            "sellMessage"
        );

    message.textContent =
        "Publishing your car...";

    const carData = {

        make:
            document.getElementById(
                "carMake"
            ).value.trim(),

        model:
            document.getElementById(
                "carModel"
            ).value.trim(),

        year:
            Number(
                document.getElementById(
                    "carYear"
                ).value
            ),

        price:
            Number(
                document.getElementById(
                    "carPrice"
                ).value
            ),

        mileage:
            Number(
                document.getElementById(
                    "carMileage"
                ).value
            ),

        fuel_type:
            document.getElementById(
                "carFuelType"
            ).value,

        fuel_average:
            Number(
                document.getElementById(
                    "carFuelAverage"
                ).value
            ),

        transmission:
            document.getElementById(
                "carTransmission"
            ).value,

        city:
            document.getElementById(
                "carCity"
            ).value.trim(),

        contact_number:
            document.getElementById(
                "carContact"
            ).value.trim(),

        description:
            document.getElementById(
                "carDescription"
            ).value.trim()
    };

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/cars/`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Authorization":
                            `Bearer ${getToken()}`
                    },

                    body:
                        JSON.stringify(
                            carData
                        )
                }
            );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "Failed to publish car"
            );
        }

        const carId =
            data.id;

        const imageInput =
            document.getElementById(
                "carImage"
            );

        if (
            imageInput.files &&
            imageInput.files.length > 0
        ) {

            const formData =
                new FormData();

            formData.append(
                "file",
                imageInput.files[0]
            );

            const imageResponse =
                await fetch(
                    `${API_BASE_URL}/cars/${carId}/images`,
                    {
                        method: "POST",

                        headers: {
                            "Authorization":
                                `Bearer ${getToken()}`
                        },

                        body: formData
                    }
                );

            if (!imageResponse.ok) {

                message.textContent =
                    "Car posted, but image upload failed.";

            }
        }

        message.textContent =
            "Car published successfully.";

        document
            .getElementById(
                "sellForm"
            )
            .reset();

        document.getElementById(
            "imagePreview"
        ).innerHTML = "";

        await loadCars();
        await loadMyListings();

        setTimeout(() => {

            closeModal(
                "sellModal"
            );

            scrollToSection(
                "my-listings"
            );

        }, 600);

    } catch (error) {

        message.textContent =
            error.message;
    }
}


// =====================================================
// IMAGE PREVIEW
// =====================================================

function previewImage() {

    const input =
        document.getElementById(
            "carImage"
        );

    const preview =
        document.getElementById(
            "imagePreview"
        );

    preview.innerHTML = "";

    if (
        !input.files ||
        input.files.length === 0
    ) {
        return;
    }

    const reader =
        new FileReader();

    reader.onload = function(event) {

        preview.innerHTML = `
            <img
                src="${event.target.result}"
                alt="Car preview"
            >
        `;
    };

    reader.readAsDataURL(
        input.files[0]
    );
}


// =====================================================
// AI AGENT
// =====================================================

function renderAgentListings(
    listings
) {

    if (
        !listings ||
        !listings.length
    ) {
        return "";
    }

    return `
        <div class="ai-listings">

            <div class="ai-listings-heading">
                Matching Listings
            </div>

            ${listings.map(
                car => {

                    let imageHtml = `
                        <div class="ai-card-no-image">
                            No Image
                        </div>
                    `;

                    if (
                        car.images &&
                        car.images.length > 0
                    ) {
                        imageHtml = `
                            <img
                                src="${escapeHtml(
                                    car.images[0].image_url
                                )}"
                                alt="${escapeHtml(
                                    car.make
                                )} ${escapeHtml(
                                    car.model
                                )}"
                            >
                        `;
                    }

                    return `
                        <article class="ai-car-card">

                            <div class="ai-car-image">
                                ${imageHtml}
                            </div>

                            <div class="ai-car-content">

                                <div class="ai-car-top">

                                    <div>

                                        <h3>
                                            ${escapeHtml(
                                                car.make
                                            )}
                                            ${escapeHtml(
                                                car.model
                                            )}
                                        </h3>

                                        <span>
                                            ${escapeHtml(
                                                car.year
                                            )}
                                        </span>

                                    </div>

                                    <strong>
                                        ${formatPrice(
                                            car.price
                                        )}
                                    </strong>

                                </div>

                                <div class="ai-car-specs">

                                    <span>
                                        ${Number(
                                            car.mileage
                                        ).toLocaleString()} km
                                    </span>

                                    <span>
                                        ${escapeHtml(
                                            car.fuel_type
                                        )}
                                    </span>

                                    <span>
                                        ${escapeHtml(
                                            car.transmission
                                        )}
                                    </span>

                                    <span>
                                        ${escapeHtml(
                                            car.city
                                        )}
                                    </span>

                                </div>

                                <div class="ai-car-extra">

                                    <p>
                                        <strong>
                                            Seller:
                                        </strong>

                                        ${escapeHtml(
                                            car.seller_name ||
                                            "Unknown Seller"
                                        )}
                                    </p>

                                    <p>
                                        <strong>
                                            Contact:
                                        </strong>

                                        ${escapeHtml(
                                            car.contact_number
                                        )}
                                    </p>

                                    <p>
                                        <strong>
                                            Fuel Average:
                                        </strong>

                                        ${escapeHtml(
                                            car.fuel_average
                                        )} km/l
                                    </p>

                                </div>

                                <div class="ai-car-description">

                                    ${escapeHtml(
                                        car.description ||
                                        "No description provided."
                                    )}

                                </div>

                                <button
                                    class="primary-btn"
                                    onclick="showCarDetails(${car.id})"
                                >
                                    View Full Listing
                                </button>

                            </div>

                        </article>
                    `;
                }
            ).join("")}

        </div>
    `;
}

function renderAiText(
    text
) {
    return escapeHtml(
        text || ""
    ).replace(
        /\n/g,
        "<br>"
    );
}

async function sendAgentMessage() {

    const input =
        document.getElementById(
            "agentInput"
        );

    const messages =
        document.getElementById(
            "chatMessages"
        );

    const message =
        input.value.trim();

    if (!message) {
        return;
    }

    messages.innerHTML += `
        <div class="message user-message">

            <div>
                ${escapeHtml(
                    message
                )}
            </div>

        </div>
    `;

    input.value = "";

    messages.innerHTML += `
        <div
            class="message assistant-message"
            id="agentLoading"
        >

            <div class="message-icon">
                AI
            </div>

            <div>
                Thinking...
            </div>

        </div>
    `;

    messages.scrollTop =
        messages.scrollHeight;

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/agent`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            message
                        })
                }
            );

        const data =
            await response.json();

        const loading =
            document.getElementById(
                "agentLoading"
            );

        if (loading) {
            loading.remove();
        }

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "AI request failed"
            );
        }

        const answer =
            data.message ||
            "I couldn't find an answer.";

        const listingsHtml =
            renderAgentListings(
                data.listings
            );

        messages.innerHTML += `
            <div class="message assistant-message">

                <div class="message-icon">
                    AI
                </div>

                <div class="assistant-response">

                    <div class="assistant-text">
                        ${renderAiText(
                            answer
                        )}
                    </div>

                    ${listingsHtml}

                </div>

            </div>
        `;

        messages.scrollTop =
            messages.scrollHeight;

    } catch (error) {

        const loading =
            document.getElementById(
                "agentLoading"
            );

        if (loading) {
            loading.remove();
        }

        messages.innerHTML += `
            <div
                class="message assistant-message"
            >

                <div class="message-icon">
                    AI
                </div>

                <div>
                    ${escapeHtml(
                        error.message
                    )}
                </div>

            </div>
        `;
    }
}


// =====================================================
// EVENTS
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        await loadCurrentUser();

        loadCars();

        loadMyListings();


        // Profile
        document
            .getElementById(
                "profileBtn"
            )
            .addEventListener(
                "click",
                () => {

                    if (!isLoggedIn()) {
                        showLogin();
                        return;
                    }

                    toggleProfileMenu();
                }
            );

        document
            .getElementById(
                "profileLoginBtn"
            )
            .addEventListener(
                "click",
                () => {

                    closeProfileMenu();
                    showLogin();

                }
            );

        document
            .getElementById(
                "profileLogoutBtn"
            )
            .addEventListener(
                "click",
                logoutUser
            );

        document
            .getElementById(
                "profileMyListings"
            )
            .addEventListener(
                "click",
                () => {

                    closeProfileMenu();

                    scrollToSection(
                        "my-listings"
                    );

                }
            );


        // Login / Register
        document
            .getElementById(
                "loginTab"
            )
            .addEventListener(
                "click",
                showLogin
            );

        document
            .getElementById(
                "registerTab"
            )
            .addEventListener(
                "click",
                showRegister
            );

        document
            .getElementById(
                "loginForm"
            )
            .addEventListener(
                "submit",
                loginUser
            );

        document
            .getElementById(
                "registerForm"
            )
            .addEventListener(
                "submit",
                registerUser
            );


        // Sell
        document
            .getElementById(
                "navSellBtn"
            )
            .addEventListener(
                "click",
                openSellCar
            );

        document
            .getElementById(
                "heroSellBtn"
            )
            .addEventListener(
                "click",
                openSellCar
            );

        document
            .getElementById(
                "myListingsSellBtn"
            )
            .addEventListener(
                "click",
                openSellCar
            );

        document
            .getElementById(
                "sellForm"
            )
            .addEventListener(
                "submit",
                publishCar
            );

        document
            .getElementById(
                "carImage"
            )
            .addEventListener(
                "change",
                previewImage
            );


        // My Listings
        document
            .getElementById(
                "refreshMyListingsBtn"
            )
            .addEventListener(
                "click",
                loadMyListings
            );


        // Edit
        document
            .getElementById(
                "editCarForm"
            )
            .addEventListener(
                "submit",
                updateCar
            );

        document
            .getElementById(
                "closeEditCarModal"
            )
            .addEventListener(
                "click",
                () => closeModal(
                    "editCarModal"
                )
            );

        document
            .getElementById(
                "uploadNewEditImageBtn"
            )
            .addEventListener(
                "click",
                uploadNewEditImage
            );


        // Search
        document
            .getElementById(
                "searchBtn"
            )
            .addEventListener(
                "click",
                searchCars
            );

        document
            .getElementById(
                "applyFiltersBtn"
            )
            .addEventListener(
                "click",
                searchCars
            );

        document
            .getElementById(
                "clearFiltersBtn"
            )
            .addEventListener(
                "click",
                clearFilters
            );

        document
            .getElementById(
                "searchInput"
            )
            .addEventListener(
                "keydown",
                event => {

                    if (
                        event.key === "Enter"
                    ) {
                        searchCars();
                    }

                }
            );


        // AI
        document
            .getElementById(
                "agentSendBtn"
            )
            .addEventListener(
                "click",
                sendAgentMessage
            );

        document
            .getElementById(
                "agentInput"
            )
            .addEventListener(
                "keydown",
                event => {

                    if (
                        event.key === "Enter"
                    ) {
                        sendAgentMessage();
                    }

                }
            );


        // Close modal backgrounds
        document
            .querySelectorAll(
                ".modal"
            )
            .forEach(modal => {

                modal.addEventListener(
                    "click",
                    event => {

                        if (
                            event.target === modal
                        ) {

                            modal.classList.add(
                                "hidden"
                            );

                        }

                    }
                );

            });


        // Close profile menu outside click
        document.addEventListener(
            "click",
            event => {

                const wrapper =
                    document.querySelector(
                        ".profile-wrapper"
                    );

                if (
                    wrapper &&
                    !wrapper.contains(
                        event.target
                    )
                ) {
                    closeProfileMenu();
                }

            }
        );

    }
);