# Exam Management System Using Blockchain

A secure, full-stack web application designed to manage exam paper submissions using cryptographic hashing and blockchain technology. This system ensures the immutability and integrity of exam papers through a simulated IPFS storage layer and an Ethereum-based blockchain audit trail.

---

## 🎯 Key Features

- **Role-Based Access Control**: Separate dashboards for Teachers and the Controller of Examinations (COE).
- **Secure File Uploads**: Exam documents are securely uploaded and hashed.
- **Blockchain Audit Trail**: Integrates with an Ethereum Testnet via `web3.py` to record the hashes of the uploaded exam papers, ensuring their integrity cannot be compromised.
- **IPFS Storage Emulation**: Uses local filesystem mocking to emulate IPFS behavior, eliminating the need for a heavy local IPFS daemon while retaining the architectural benefits.
- **Lightweight Database**: Runs on a local SQLite database for effortless development setup.

---

## 🛠️ Technology Stack

- **Backend**: Python, Django (v4.2)
- **Blockchain Interaction**: `web3.py` (Ethereum Testnet)
- **Database**: SQLite3
- **Frontend**: HTML, CSS (Vanilla)

---

## 🚀 Development Journey: How This Project Was Built

Here are all the crucial steps and phases undertaken to develop, debug, and finalize this project:

### Phase 1: Environment & Architecture Refactoring
- **Dependency Upgrades**: Modernized the `requirements.txt` (e.g., locking Django to version 4.2.11) to ensure full compatibility with newer Python versions and resolve legacy dependency conflicts.
- **Database Migration to SQLite**: Removed the reliance on the PostgreSQL-exclusive `ArrayField`. The models were refactored to use standard, universally supported fields, allowing the system to run on a zero-config SQLite database.

### Phase 2: Blockchain & Storage Integration
- **Ethereum Blockchain Integration**: Leveraged the `web3.py` library to establish a connection with the Ethereum network (Testnet). The application securely submits transactions to the blockchain containing the cryptographic hashes of the uploaded exam papers.
- **IPFS Mocking Layer**: Bypassed the requirement for a live local IPFS daemon. Implemented a custom filesystem mocking solution that simulates IPFS hashing and file retrieval locally, drastically lowering the barrier to entry for setting up the project locally.

### Phase 3: Workflow Optimization & Bug Fixes
- **Exam Request Workflow Fixes**: Debugged the `teacher_dashboard` view to resolve a critical issue where the request submission process failed after the first successful execution.
- **State Management Validation**: Corrected the application state and view logic to ensure teachers can reliably upload and submit multiple exam requests sequentially without encountering blocking errors or state inconsistencies.

### Phase 4: Version Control & Deployment Prep
- **Repository Optimization**: Created a comprehensive `.gitignore` file to ensure sensitive keys (e.g., `.pem` files), local databases (`db.sqlite3`), and environment caches were not exposed.
- **GitHub Upload**: Successfully initialized the Git repository, staged the clean working directory, and pushed the repository to its final destination on GitHub.

---

## ⚙️ Local Setup Instructions

Follow these steps to get the project running on your local machine:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mentalShER/exam-management-system-using-blockchain-.git
   cd exam-management-system-using-blockchain-
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # On Windows
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
6. **Access the application:** Open your browser and go to `http://127.0.0.1:8000/`.

---

## 🤝 Contributors

- **Sneha** ([@snehahaaha](https://github.com/snehahaaha)) - sneha.17253@sakec.ac.in
