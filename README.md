
# 🚗 AI-Powered Car Marketplace

An AI-powered car marketplace web application built with **FastAPI, SQLite, Gemini, Skills and Model Context Protocol (MCP)**.

The platform allows users to browse, search, compare, recommend, and manage car listings. It also includes an AI assistant that understands natural-language requests and helps users find suitable cars.

---

## 📌 Project Overview

The Car Marketplace is a full-stack web application designed to simplify the process of buying and selling cars.

Users can:

- Browse available cars
- Search cars using filters
- View detailed car information
- Register and log in securely
- Add, update, and delete their own car listings
- Upload, replace, and delete car images
- Use an AI assistant to search for cars
- Compare cars using their names or features
- Get personalized car recommendations
- Retrieve detailed information about listings

The project also demonstrates the integration of **AI agents, skills, Gemini, and MCP tools**.

---

## ✨ Features

### 👤 User Authentication

- User registration
- User login
- JWT-based authentication
- Password hashing using bcrypt
- Protected API endpoints
- User profile information

### 🚘 Car Listings

- Add new car listings
- View all available cars
- View individual car details
- Update car information
- Delete car listings
- View personal listings
- Ownership-based access control

### 🔍 Search and Filtering

Users can search and filter cars using:

- Make and model
- City
- Fuel type
- Transmission
- Price range
- Manufacturing year
- Mileage
- Sorting and pagination

### 🖼️ Car Images

- Upload car images
- View car images
- Replace existing images
- Delete images
- Automatically remove associated images when a car is deleted

### 🤖 AI Car Assistant

The AI assistant uses Gemini to understand natural-language requests.

Example questions:

```text
Find a manual BMW in Lahore under 30 lakh.
```

```text
Recommend a car in Pindi under 50 lakh.
```

```text
Compare AUDI A5 and BMW M5
```

```text
Show me the details of Nissan 2023.
```

The assistant identifies the user's intent and connects the request to the appropriate functionality.

### 🔗 Model Context Protocol (MCP)

The project includes a custom MCP server built using FastMCP.

Available MCP tools:

- Search cars
- Get car details
- Compare cars
- Recommend cars

MCP provides a standardized interface for accessing application tools.

---

## 🏗️ System Architecture

The project contains the following main components:

```text
User
  │
  ▼
Frontend (HTML, CSS, JavaScript)
  │
  ▼
FastAPI Backend
  │
  ├── Authentication
  ├── Car Listing APIs
  ├── Image Management
  └── AI Agent
        │
        ▼
      Gemini
        │
        ▼
   Intent Detection
        │
        ▼
      Skills
        │
        ├── Search Skill
        ├── Comparison Skill
        └── Recommendation Skill
        │
        ▼
    SQLite Database
```

### AI Architecture

```text
User Request
     │
     ▼
AI Agent
     │
     ▼
Gemini understands the request
     │
     ▼
Intent Detection
     │
     ▼
Relevant Skill
     │
     ▼
Database Operation
     │
     ▼
Response to User
```

---

## 🧠 AI Agent, Skills, and MCP

| Component | Responsibility |
|---|---|
| AI Agent | Understands the user's request and decides what action is needed |
| Gemini | Processes natural-language input |
| Skills | Perform specific operations such as searching or comparing cars |
| MCP | Provides a standardized interface for application tools |
| FastAPI | Provides backend APIs |
| SQLite | Stores application data |

### Available Skills

#### 1. Search Skill

Finds cars based on search criteria such as city, price, fuel type, and transmission.

#### 2. Comparison Skill

Retrieves selected cars and prepares their information for comparison.

#### 3. Recommendation Skill

Finds cars matching the user's requirements and provides recommendations.

---

## 🛠️ Technologies Used

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- Pydantic

### Authentication and Security

- JWT authentication
- bcrypt password hashing
- Protected API endpoints
- User ownership validation

### Artificial Intelligence

- Google Gemini API
- AI intent detection
- AI-powered car search
- AI recommendations
- AI car comparison

### AI Tool Integration

- Model Context Protocol (MCP)
- FastMCP

### Frontend

- HTML5
- CSS3
- JavaScript

---

## 📂 Project Structure

```text
car-marketplace/
│
├── backend/
│   └── app/
│       ├── ai/
│       │   ├── agent.py
│       │   ├── server.py
│       │   └── skills/
│       │       ├── search/
│       │       │   └── skill.py
│       │       ├── comparison/
│       │       │   └── skill.py
│       │       └── recommendation/
│       │           └── skill.py
│       │
│       ├── api/
│       │   └── routes/
│       │       └── cars.py
│       │
│       ├── auth/
│       │   ├── routes.py
│       │   └── security.py
│       │
│       ├── database/
│       ├── models/
│       ├── schemas/
│       └── main.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── uploads/
│   └── cars/
│
├── .cursor/
│   └── mcp.json
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

> Update the structure if your actual folder names are different.

---

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/car-marketplace.git
```

Navigate to the project directory:

```bash
cd car-marketplace
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

#### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell activation is blocked, use:

```powershell
.\.venv\Scripts\activate.bat
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root.

Add the required environment variables:

```env
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key
```

> Never upload your real `.env` file or API keys to GitHub.

### 6. Run the Backend

From the project root, run:

```bash
uvicorn backend.app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

### 7. Open API Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## 🔐 Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | API key used to access Gemini |
| `SECRET_KEY` | Secret key used for authentication security |

Use `.env.example` to show required variables without exposing sensitive information.

---

## 🔌 API Overview

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Log in a user |
| GET | `/auth/me` | Get the current user's profile |

### Cars

| Method | Endpoint | Description |
|---|---|---|
| GET | `/cars/` | Get car listings |
| GET | `/cars/my-listings` | Get the current user's listings |
| GET | `/cars/{car_id}` | Get car details |
| POST | `/cars/` | Create a car listing |
| PUT | `/cars/{car_id}` | Update a car listing |
| DELETE | `/cars/{car_id}` | Delete a car listing |

> Check the Swagger documentation for the complete API details and request formats.

---

## 🤖 AI Assistant Examples

### Search Cars

```text
Find a manual Mini Copper in BWP under 30 lakh.
```

### Get Recommendations

```text
Recommend a petrol car in Dubai under 50 lakh.
```

### Compare Cars

```text
Compare AUDI A5 and BMW M4 CS.
```

The assistant resolves human-friendly car names and features before retrieving the relevant car records.

### Get Car Details

```text
Show the details of BMW M5 2023.
```

---

## 🔒 Security Considerations

The project includes:

- Password hashing using bcrypt
- JWT-based authentication
- Protected user-specific endpoints
- Ownership checks for updating and deleting listings
- Environment variables for sensitive configuration

For production deployment, additional security measures should be considered, including:

- HTTPS
- Strong secret keys
- Input validation
- Rate limiting
- Secure image validation
- Proper production database configuration
- Secure CORS configuration

---

## 🚀 Future Improvements

Possible future enhancements include:

- Advanced car recommendation algorithms
- Multiple image optimization
- Admin dashboard
- Car favorites and saved searches
- Messaging between buyers and sellers
- Email notifications
- Production deployment
- Automated tests
- Improved AI response accuracy
- Support for additional databases

---

## 🧪 Testing

Testing can be performed using:

- FastAPI Swagger UI
- Manual frontend testing
- API testing tools
- Python unit tests

Example backend import test:

```bash
python -c "import backend.app.main"
```

---

## 👨‍💻 Learning Objectives

This project demonstrates practical experience with:

- Backend development using FastAPI
- REST API development
- Database operations using SQLAlchemy
- JWT authentication
- Password hashing
- File and image management
- AI agents
- Gemini API integration
- Skills-based architecture
- Model Context Protocol (MCP)
- Frontend and backend integration

---

## 📄 License

This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for the complete license text.

---

## 👤 Author

**Rao Umar Farooq**

GitHub: `https://github.com/UmarRao1`

---

## ⭐ Acknowledgements

- FastAPI
- SQLAlchemy
- Google Gemini
- Model Context Protocol
- Python community
