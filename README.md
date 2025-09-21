 # Manufacturing Management System

A full-stack application designed to streamline and automate the entire manufacturing process, from inventory and resource management to production order tracking and real-time analytics.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Tech Stack](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Tech Stack](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)
![Tech Stack](https://img.shields.io/badge/Firebase-ffca28?style=for-the-badge&logo=firebase&logoColor=black)
![Tech Stack](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tech Stack](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)

---

## ✨ Features

### Backend

-   **🔩 Core Manufacturing**: Full lifecycle management for Products, Bills of Materials (BOMs), and Manufacturing Orders (MOs).
-   **🤖 Automation**: Automatic creation of Work Orders from BOMs, and automated status progression. A background polling service simulates work center operations.
-   **📦 Inventory Control**: A real-time Stock Ledger tracks all inventory movements, including component consumption and finished good production.
-   **🔐 Authentication & Authorization**: Secure role-based access control (Admin, Manager, Operator) using Firebase Authentication.
-   **📊 Analytics**: KPI dashboard providing insights on production status, throughput, and average cycle times.
-   **📡 WebSocket**: Real-time updates pushed to the frontend for live monitoring of manufacturing and work orders.
-   **📄 Exporting**: Download completed manufacturing order details in CSV or PDF format.
-   **⚙️ Extensible**: Modular architecture with services, repositories, and routes for easy maintenance and extension.

### Frontend (Inferred)

-   **🖥️ Interactive Dashboard**: A central hub to visualize all manufacturing operations and analytics KPIs.
-   **📝 Dynamic Forms**: Intuitive interfaces for creating and managing Products, BOMs, and Manufacturing Orders.
-   **🔒 Role-Based UI**: The user interface adapts to show only the relevant information and actions based on the logged-in user's role.
-   **🔔 Real-Time Notifications**: Live updates on order statuses and inventory changes using WebSockets and toast notifications.

---

## 🛠️ Tech Stack

-   **Backend**: Python, FastAPI, MongoDB (with PyMongo), Firebase Admin SDK, Uvicorn.
-   **Frontend**: React, TypeScript, React Router, Firebase Client SDK, Sonner.
-   **Database**: MongoDB.

---

## 🚀 Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

-   **Python 3.9+**
-   **Node.js v18+** and npm/yarn
-   **MongoDB**: Make sure you have a running MongoDB instance (local or cloud-based like MongoDB Atlas).
-   **Firebase Project**:
    1.  Create a new project on the [Firebase Console](https://console.firebase.google.com/).
    2.  Enable **Firebase Authentication** with the "Email/Password" sign-in provider.
    3.  Go to **Project settings** > **Service accounts**.
    4.  Click **"Generate new private key"** to download your service account JSON file.

---

### ⚙️ Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd OdooNMITHackathonRound2
    ```

2.  **Backend Setup:**
    ```bash
    cd backend
    ```
    -   **Create and activate a virtual environment:**
        ```bash
        # For macOS/Linux
        python3 -m venv venv
        source venv/bin/activate

        # For Windows
        python -m venv venv
        .\venv\Scripts\activate
        ```
    -   **Install dependencies:**
        Run `pip install -r requirements.txt`. The `requirements.txt` file is provided in the `backend` directory.
    -   **Set up Firebase:**
        -   Move the downloaded Firebase service account JSON file into the `backend/` directory.
    -   **Configure Environment Variables:**
        -   Create a file named `.env` in the `backend/` directory.
        -   Copy the contents from the example below and replace the placeholder values.

        **.env Example:**
        ```env
        # MongoDB Configuration
        MONGO_URI="mongodb://localhost:27017/"
        MONGO_DB_NAME="manufacturing_db"

        # JWT Secret Key (for internal tokens if needed)
        # Generate a strong key with: openssl rand -hex 32
        SECRET_KEY="your_super_secret_key_of_at_least_32_characters"
        ACCESS_TOKEN_EXPIRE_MINUTES=11520 # 8 days

        # Firebase Configuration
        # The name of your service account JSON file
        GOOGLE_APPLICATION_CREDENTIALS="your-firebase-service-account-file.json"
        ```

3.  **Frontend Setup:**
    ```bash
    cd frontend
    ```
    -   **Install dependencies:**
        ```bash
        npm install
        # or
        yarn install
        ```
    -   **Configure Environment Variables:**
        -   In the `frontend/` directory, create a file named `.env.local`.
        -   Go to your Firebase project settings, and under "Your apps", find your web app.
        -   Copy the Firebase configuration object and add it to `.env.local`.

        **.env.local Example:**
        ```env
        VITE_FIREBASE_API_KEY="your-api-key"
        VITE_FIREBASE_AUTH_DOMAIN="your-auth-domain"
        VITE_FIREBASE_PROJECT_ID="your-project-id"
        VITE_FIREBASE_STORAGE_BUCKET="your-storage-bucket"
        VITE_FIREBASE_MESSAGING_SENDER_ID="your-sender-id"
        VITE_FIREBASE_APP_ID="your-app-id"
        ```
        *Note: The `VITE_` prefix is standard for Vite projects. If you are using Create React App, the prefix should be `REACT_APP_`.*

---

### 🏃 Running the Application

1.  **Start the Backend Server:**
    -   Make sure you are in the `backend` directory with your virtual environment activated.
    -   Run the application:
        ```bash
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
        ```
    -   The API will be available at `http://localhost:8000`. You can access the interactive docs at `http://localhost:8000/docs`.

2.  **Start the Frontend Server:**
    -   Navigate to the `frontend` directory in a new terminal.
    -   Run the development server:
        ```bash
        npm run dev
        # or
        yarn dev
        ```
    -   Open your browser and go to `http://localhost:5173` (or the port specified in your terminal).

---

### 📂 Project Structure (High-Level)

```
.
├── backend/
│   ├── app/
│   │   ├── core/         # Core logic: DB connection, security, settings
│   │   ├── models/       # Pydantic data models
│   │   ├── repo/         # Repository layer (database interactions)
│   │   ├── routes/       # API endpoint definitions
│   │   ├── service/      # Business logic layer
│   │   ├── utils/        # Utility functions
│   │   └── main.py       # FastAPI app entry point
│   ├── .env              # Environment variables (you create this)
│   └── requirements.txt  # Python dependencies
│
└── frontend/
    ├── src/              # Frontend source code
    ├── public/           # Static assets
    ├── .env.local        # Environment variables (you create this)
    └── package.json      # Frontend dependencies
```