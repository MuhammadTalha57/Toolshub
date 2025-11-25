# ToolsHub 🛠️

> A C2C marketplace platform for software tool sharing built on Odoo 18

[![Odoo](https://img.shields.io/badge/Odoo-18.0-714B67?style=flat&logo=odoo)](https://www.odoo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-336791?style=flat&logo=postgresql&logoColor=white)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📖 Overview

ToolsHub is a peer-to-peer marketplace that enables users to rent out and rent software licenses easily, securely, and affordably. The platform addresses the problem of expensive software subscriptions and underutilized premium licenses by creating a structured ecosystem for software tool sharing.

### Key Features

- 🔐 **User Authentication** - Secure registration and login system
- 🔍 **Smart Browsing** - Search and filter tools by name, price range, and ownership
- 💼 **Rental Listings** - Create and manage tool rental listings
- 📊 **Dual Dashboards** - Separate views for rented tools and tools rented out
- 💳 **Secure Payments** - Stripe integration with Checkout Sessions and Connect accounts
- 🎯 **Access Management** - Credential sharing between lenders and renters
- 🔄 **Active Status Toggle** - Enable/disable listings as needed

## 🏗️ Architecture

ToolsHub follows the **MVC (Model-View-Controller)** architecture:

- **Model**: PostgreSQL database managed through Odoo ORM
- **View**: Frontend UI built with Odoo's OWL (Owl Web Library) Framework
- **Controller**: Python-based backend handling business logic and data operations

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (OWL)                      │
│              QWeb Templates + JavaScript                │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Controllers (Python)                       │
│          Routes, APIs, Business Logic                   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│               Models (Odoo ORM)                         │
│              PostgreSQL Database                        │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 12.0 or higher
- Node.js (for rtlcss)
- Git
- Build Tools for Visual Studio (Windows)

### Step-by-Step Setup

#### 1. Clone Odoo Repository

```bash
git clone https://github.com/odoo/odoo.git
cd odoo
```

#### 2. Install Python

Download Python 3.10+ from [python.org](https://www.python.org/downloads/)

During installation:
- ✅ Check "Add Python 3 to PATH"
- ✅ Check "pip" in Customize Installation

Verify installation:
```bash
python3 --version
pip --version
```

#### 3. Install PostgreSQL

Download PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)

Create a new PostgreSQL user (Odoo cannot use the default `postgres` user):

1. Add PostgreSQL's bin directory to PATH:
   ```
   C:\Program Files\PostgreSQL\<version>\bin
   ```

2. Create user via pgAdmin:
   - Open pgAdmin
   - Double-click server to connect
   - Navigate to: Object → Create → Login/Group Role
   - Set username (e.g., `odoo`)
   - In Definition tab, set password (e.g., `odoo`)
   - In Privileges tab, set:
     - Can login? → **Yes**
     - Create database? → **Yes**

#### 4. Install Dependencies

Install Build Tools for Visual Studio with C++ build tools.

Navigate to Odoo directory and install Python dependencies:

```bash
cd \path\to\odoo
pip install setuptools wheel
pip install -r requirements.txt
```

#### 5. Install rtlcss (Optional)

For right-to-left language support:

```bash
npm install -g rtlcss
```

Add rtlcss.cmd location to PATH (typically: `C:\Users\<user>\AppData\Roaming\npm\`)

#### 6. Install wkhtmltopdf

Download and install [wkhtmltopdf 0.12.6](https://wkhtmltopdf.org/) for PDF generation support.

#### 7. Clone ToolsHub Module

```bash
git clone https://github.com/MuhammadTalha57/Toolshub.git
```

#### 8. Configure Odoo

Create `odoo.conf` file:

```ini
[options]
addons_path = addons,path/to/Toolshub
db_user = odoo
db_password = odoo
db_host = localhost
db_port = 5432
```

Copy the ToolsHub module to your Odoo addons directory or add its path to `addons_path`.

#### 9. Run Odoo

```bash
python odoo-bin -c odoo.conf
```

Or with inline parameters:

```bash
python odoo-bin -r odoo -w odoo --addons-path=addons,path/to/Toolshub -d mydb
```

#### 10. Install ToolsHub Module

1. Open browser and navigate to `http://localhost:8069`
2. Login with default credentials:
   - Email: `admin`
   - Password: `admin`
3. Enable Developer Mode: Settings → Activate Developer Mode
4. Go to Apps menu
5. Search for "ToolsHub"
6. Click **Install**

## 📁 Project Structure

```
toolshub/
├── models/              # Database models and business logic
│   ├── tool.py
│   ├── tool_plan.py
│   ├── rent_listing.py
│   └── rented_tool.py
├── views/               # Odoo backend views and QWeb templates
│   ├── tool_views.xml
│   ├── rent_listing_views.xml
│   └── templates.xml
├── controllers/         # HTTP routes and API endpoints
│   └── main.py
├── security/            # Access rights and record rules
│   └── ir.model.access.csv
├── static/              # Frontend assets
│   ├── src/
│   │   ├── js/         # JavaScript/OWL components
│   │   ├── xml/        # OWL templates
│   │   └── scss/       # Stylesheets
│   └── description/
├── __manifest__.py      # Module metadata
└── __init__.py
```

## 💻 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python 3.10+ | Business logic and models |
| | Odoo ORM | Database operations |
| | XML | Views and templates |
| **Frontend** | OWL Framework | Component-based UI |
| | QWeb | Template engine |
| | JavaScript | Client-side interactivity |
| | Bootstrap/SCSS | Styling |
| **Database** | PostgreSQL 12+ | Data persistence |
| **Payment** | Stripe API | Payment processing |

## 🎯 Functional Requirements

### User Management
- FR 1.1: User registration and authentication
- FR 1.2: Email verification

### Tool Management
- FR 2.1: Browse and search tools
- FR 2.2: View tool plans
- FR 2.3: View plan features

### Rental System
- FR 3.1: Create rental listing
- FR 3.2: Rent a tool
- FR 3.3: Toggle active status of listing
- FR 3.4: Validate available users

### Payment System
- FR 4.1: Process payments
- FR 4.2: Manage Stripe Connect IDs
- FR 4.3: Create and redirect to Stripe checkout session
- FR 4.4: Validate payment

### Backend Views
- FR 5.1: Manage tools
- FR 5.2: Manage plans
- FR 5.3: Manage plan features
- FR 5.4: Manage rent listings

## 📸 Screenshots

### Login Page
![Login Screen](docs/images/loginScreen.jpg)

### Rent Listings
![Rent Listings](docs/images/RentListings1.jpg)
![Rent Listings Filtered](docs/images/RentListings2.jpg)

### Rented Out Tools Dashboard
![Rented Out](docs/images/RentedOut1.jpg)
![Rented Out Details](docs/images/RentedOut2.jpg)

## 🔮 Future Enhancements

- 📱 Mobile application (Android/iOS)
- 🤖 AI-based tool recommendations
- ⚡ Automated credential delivery system
- ⭐ Review and rating system
- 👥 Group-buy feature
- 📊 Admin analytics dashboard
- 💬 In-app messaging between users

