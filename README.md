# Quiporder - Occupational Therapy Management System

**Live Site:** [View Deployed Site](https://quiptorder-f48affb2ee2c.herokuapp.com) 
---

## Table of Contents

1. [Project Overview](#project-overview)
### System Design Diagrams
2. [Design](#design)
3. [Features](#features)
4. [User Stories](#user-stories)
5. [Technologies Used](#technologies-used)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Security & Data Protection](#security--data-protection)
9. [Future Features](#future-features)
10. [Credits & Acknowledgments](#acknowledgement)

---

## Project Overview

### Quiporder

Quiporder is a Full-Stack Django application for occupational therapists in NHS and private practice **and their patients** to manage and track equipment orders.

Staff users (admin) configure the system by creating user accounts, adding therapist and patient profiles, and assigning patients to therapists in the Django Admin.
Therapists then work through a dedicated dashboard to manage their caseload and equipment orders, while patients use a separate dashboard to follow their own orders in a read-only view.

Therapists can register patients, manage their caseload, and create or update equipment orders as part of their clinical workflow, while patients can log in to view the orders assigned to them and follow each order’s status (for example: Pending → Approved → In Transit → Delivered) in a read-only view.

Therapist-facing features use **PatientProfile.status** (ACTIVE / DISCHARGED) to represent the patient’s clinical status, and patient-facing views focus on **EquipmentOrder.status** (PENDING / APPROVED / IN_TRANSIT / DELIVERED / CANCELLED) so patients can clearly see where their equipment is in the logistics journey.

---

### Key Functionality

- Equipment ordering and inventory tracking.
- Role-based access control (Staff/Admin, Therapists, Patients).

  - Staff Django Admin screens (restricted to staff users and superusers via Django’s built-in permissions) for:
  - Creating and managing CustomUser accounts.
  - Creating and updating TherapistProfile and PatientProfile.
  - Assigning therapists to patients so they appear correctly in front-end therapist dashboards.
  - Managing equipment and equipment orders with full CRUD capability.
  - Reviewing audit trails via **Status Histories** (e.g. `/admin/equipment/equipmentorderstatushistory/`), showing when order statuses changed and by whom.

- Therapist dashboards for day-to-day CRUD on equipment orders and caseload, using patients that staff have already set up and assigned.
- Patient dashboards for secure, read-only tracking of their own orders and statuses.

---

### Project Purpose

**The system is designed to:**

- Provide centralized management of staff, therapists, patients, and equipment orders, with staff/admin configuring users, profiles, and therapist–patient relationships in Django Admin.
- Support request, approval, and fulfilment workflows for equipment, including clear order statuses visible to both therapists and patients.
- Give therapists real-time visibility of their caseload and order status via a dedicated therapist dashboard.
- Provide patients with a simple, secure view of their own orders only, including the logistics status for each order, without exposing any other patients or internal admin data.

---

### System Design Diagrams


<details>
  <summary><strong>View Entity Relationship Diagram (ERD)</strong></summary>

  <p>Source file: <code>docs/software_architecture_diagrams/erd.md</code></p>

```mermaid
erDiagram
    CUSTOMUSER ||--o| THERAPISTPROFILE : is_optional
    CUSTOMUSER ||--o| PATIENTPROFILE : is_optional
    THERAPISTPROFILE ||--o{ PATIENTPROFILE : manages
    PATIENTPROFILE ||--o{ EQUIPMENT_ORDER : has
    EQUIPMENT_ORDER }|--|| EQUIPMENT : references

    CUSTOMUSER {
        int id PK
        string username UK
        string email UK
        string first_name "Inherited from AbstractUser"
        string last_name "Inherited from AbstractUser"
        date date_of_birth 
        string password
        string user_type "THERAPIST or PATIENT"
        bool is_active
        bool is_staff
        datetime date_joined
    }

    THERAPISTPROFILE {
        int id PK
        int user_id FK "Gets name/email/dob from CustomUser"
        string license_number UK
        int max_caseload
        string status "ACTIVE, INACTIVE, ON_LEAVE"
    }

    PATIENTPROFILE {
        int id PK
        int user_id FK "Gets name/email/dob from CustomUser"
        int assigned_therapist_id FK "Gets therapist name via FK"
        string medical_record_number UK
        date admission_date
        string status "ACTIVE or DISCHARGED"
        text notes
    }

    EQUIPMENT_ORDER {
        int id PK
        int patient_id FK "Gets patient name/MRN via FK"
        int equipment_id FK
        int quantity
        datetime ordered_at
        string status "PENDING/APPROVED/IN_TRANSIT/DELIVERED/CANCELLED"
    }

    EQUIPMENT {
        int id PK
        string name UK
        string category "MOBILITY/ADL/SENSORY"
        string size "S/M/L/Custom"
        total_quantity
        available_quantity
        text description
    }
```
</details>

The ERD shows CustomUser, PatientProfile, TherapistProfile, Equipment, and EquipmentOrder relationships. 


<details> <summary><strong>View Application Flow & Role-based Workflows</strong></summary> <p>Source file: <code>docs/software_architecture_diagrams/flow-horizontal-view.md</code></p>

```mermaid
flowchart TD
    %% QuipOrder MVP - CRUD Flow (Layered for VS Code readability)

    %% LOGIN LAYER
    subgraph LOGIN
        A[User Login]
        A --> B{User Type?}
    end

    %% DASHBOARD LAYER
    subgraph DASHBOARD
        B -->|Therapist| C[Therapist Dashboard]
        B -->|Patient| D[Patient Dashboard]
    end

    %% THERAPIST CRUD LAYER
    subgraph PATIENT_MANAGEMENT
        C --> E[Manage Patients CRUD]
        E --> E1[Create Patient]
        E --> E2[Read/View Patients List & Details]
        E --> E3[Update Patient Details]
        E --> E4[Delete Patient]
    end

    subgraph EQUIPMENT_MANAGEMENT
        C --> F[Manage Equipment CRUD]
        F --> F1[Create Equipment]
        F --> F2[Read/View Equipment List]
        F --> F3[Update Equipment Stock/Info]
        F --> F4[Delete Equipment]
    end

    subgraph ORDER_MANAGEMENT
        C --> G[Manage Orders CRUD]
        G --> G1[Create Order for Patient]
        G --> G2[Read/View Orders]
        G --> G3[Update Order Status/Quantity]
        G --> G4[Delete/Cancel Order]
    end

    %% PATIENT LAYER
    subgraph PATIENT_VIEW
        D --> H[View My Orders Only Read-Only]
        H --> H1[See Order Status: Pending → Approved → In Transit → Delivered]
    end

    %% COLOR STYLING
    style C fill:#78C7A6,stroke:#333,stroke-width:2px
    style D fill:#56CFE1,stroke:#333,stroke-width:2px
    style E fill:#2A9D8F,stroke:#333
    style F fill:#2A9D8F,stroke:#333
    style G fill:#2A9D8F,stroke:#333
    style H fill:#56CFE1,stroke:#333
```
</details

The flow diagram documents therapist vs patient journeys, including dashboards and CRUD vs read-only behaviour.

---

### Role-Based Access and Dashboards

This project implements role-based login and separated access as required in LO3.

- **Staff / Admin**
  - Use Django Admin with staff/superuser permissions.
  - Create and manage all user accounts (therapists and patients), including:
    - Creating CustomUser records.
    - Creating and updating TherapistProfile and PatientProfile.
    - Assigning patients to therapists.
  - Perform full CRUD on equipment and equipment orders (including correcting data and bulk administration).
  - View audit trails such as **EquipmentOrderStatusHistory** in the admin (e.g. `/admin/equipment/equipmentorderstatushistory/`) to see when order statuses changed and by whom.
  - Can grant or remove staff permissions for other users.
  - If staff users do not create users, profiles, and therapist assignments, those patients and therapists will not appear in the therapist dashboard dropdowns or other front-end views.

- **Therapists**
  - Log in via Django Allauth.
  - Access the **Therapist Dashboard** (`/equipment/dashboard/`) which shows:
    - Top-level metrics (Equipment Items, Total Orders, Pending Orders, Active Patients).
    - Navigation links to:
      - Dashboard: `/equipment/dashboard/`
      - Equipment list: `/equipment/list/`
      - Create order: `/equipment/order/create/`
    - A “Recent Orders” table with quick **Edit** and **Delete** actions for the therapist’s last 10 orders.
  - Can:
    - View equipment inventory summary in the front end.
    - Create new orders for any patient that has been set up and assigned by staff.
    - Edit or delete their existing equipment orders.
  - For detailed equipment CRUD (add/edit/delete equipment definitions) they are directed to the Django Admin via the “Go to Admin Panel” link, which only works for staff users.

- **Patients**
  - Log in via Django Allauth.
  - Access the **Patient Dashboard** (`/equipment/patient/dashboard/`), which shows:
    - Navigation: “Quiporder” home and “My Orders”.
    - A “My Equipment Orders” table listing:
      - Equipment name.
      - Quantity.
      - Current status (e.g. Pending, Approved, In Transit, Delivered, Cancelled).
      - Notes (e.g. “Changed quantity to 3 on 3rd @ 19:20”).
      - Ordered date.
  - Can only **view** their own orders; they cannot create, edit, or delete any equipment or orders.


---

### User Stories:

The user stories used for planning and development of Quiporder are documented below. All user stories were tracked and managed using GitHub Projects.

User stories were tested as part of manual testing and can be matched to test cases by their keys. See TESTING.md

### Authentication & Access

* **US1:** As a site admin, I can create user accounts so that therapists and patients can access the system with appropriate permissions.

* **US2:** As a therapist, I can log in to the system so that I can access the therapist dashboard and manage equipment orders.

* **US3:** As a patient, I can log in to the system so that I can view my equipment orders on a read-only dashboard.

* **US4:** As a site admin, I can assign user roles (therapist/patient) so that users have appropriate access levels.

* **US5:** As a non-authenticated user, I cannot access protected pages so that patient data remains secure.

### Therapist Features

* **US6:** As a therapist, I can view the dashboard so that I can see statistics on equipment, orders, and patients.

* **US7:** As a therapist, I can create equipment orders for patients so that they receive the equipment they need.

* **US8:** As a therapist, I can edit my orders within 3 weeks so that I can correct any mistakes.

* **US9:** As a therapist, I can delete my orders within 3 weeks so that incorrect orders can be removed.

* **US10:** As a therapist, I can view a list of recent orders so that I can track order status and history.

* **US11:** As a therapist, I can see order status badges so that I can quickly identify pending, approved, or delivered orders.

* **US12:** As a therapist, I can access the admin panel (if staff) so that I can manage system data.

### Patient Features

* **US13:** As a patient, I can view my orders on my dashboard so that I can see what equipment has been ordered for me.

* **US14:** As a patient, I cannot edit or delete orders so that order integrity is maintained.

* **US15:** As a patient, I can see order status so that I know if my equipment is pending, approved, or delivered.

### Equipment Management

* **US16:** As a therapist, I can view available equipment so that I know what can be ordered.

* **US17:** As a therapist, I can see equipment quantities so that I know current stock levels.

* **US18:** As a site admin, I can add new equipment so that it becomes available for ordering.

* **US19:** As a site admin, I can edit equipment details so that information stays accurate.

* **US20:** As a site admin, I can manage equipment inventory so that stock levels are maintained.

### Patient Management

* **US21:** As a site admin, I can create patient profiles so that therapists can order equipment for them.

* **US22:** As a site admin, I can assign patients to therapists so that care relationships are tracked.

* **US23:** As a site admin, I can set patient status (active/discharged) so that only active patients appear in order forms.

### Security & Data Protection

* **US24:** As a site admin, I cannot grant staff privileges to patient accounts so that security is maintained.

* **US25:** As a user, I see custom error pages (403, 404, 500) so that errors are handled gracefully.

* **US26:** As a site admin, I can soft delete orders so that audit trails are preserved.

### Accessibility & UX

* **US27:** As a user, I can navigate using keyboard only so that the site is accessible.

* **US28:** As a user, I can use the site on mobile devices so that I can access it anywhere.

* **US29:** As a user, I receive clear feedback messages so that I know when actions succeed or fail.


**[View](https://github.com/users/Alumsdesigns/projects/4/views/1) GitHub Projects board:** 

GitHub Projects was utilized for planning this website.
I created and track User Stories.
One week was spent on project planning, including the first mentor meeting where we planned the project timeline. The initial "sprint" took two and I ran each milestone two weeks at a time.

**This board was used to:**

- Capture Epics, User Stories, and Tasks aligned to the project goals.
- Track work across columns such as Backlog, In Progress, In Review, and Done.
- Document iteration rounds, including observational usability testing feedback and subsequent improvements (e.g. admin superuser visibility, clearer dropdown labels, and dashboard refinements) and unexpected bugs and improvements that were identified during testing.

<details>
<summary><strong>Click to view image of Github project board in action</strong></summary>

<img src="docs/agile_project_management_image/quiporder_github_kanban_board.png" alt="GitHub Projects Kanban board" width="100%">

</details>

---
## Features

### Implemented Features

#### Authentication & Access Control

| Feature | Description | User Type |
|---------|-------------|-----------|
| Role-based login | Users redirected to appropriate dashboard based on role | All |
| Session management | Secure login/logout with Django Allauth | All |
| Signup restriction | Admin-only account creation for security | Staff |
| Login state display | Username shown in navbar when logged in | All |
| Remember me | Optional persistent login checkbox | All |

#### Staff / Admin Features

| Feature | Description |
|---------|-------------|
| User management | Create, edit, delete user accounts |
| Profile management | Create TherapistProfile and PatientProfile |
| Patient assignment | Assign patients to therapists |
| Equipment CRUD | Full create, read, update, delete for equipment |
| Order management | View and update all orders |
| Status updates | Change order status (Pending → Approved → Delivered) |
| Audit trail | View status change history in EquipmentOrderStatusHistory |
| Security enforcement | Patients automatically blocked from staff privileges |

#### Therapist Features

| Feature | Description |
|---------|-------------|
| Dashboard | View statistics (equipment count, orders, patients) |
| Create orders | Order equipment for any active patient |
| Edit orders | Modify own orders within 21 days |
| Delete orders | Soft-delete own orders within 21 days |
| View equipment | See available equipment and stock levels |
| Recent orders | Table showing last 10 orders with Edit/Delete actions |
| Stock validation | Cannot order more than available quantity |

#### Patient Features

| Feature | Description |
|---------|-------------|
| Dashboard | Read-only view of personal orders |
| Order tracking | See status (Pending → Approved → In Transit → Delivered) |
| Order history | View all orders assigned to them |
| Status badges | Color-coded visual status indicators |

#### UX & Accessibility Features

| Feature | Description |
|---------|-------------|
| Responsive design | Mobile-first CSS, works on all devices |
| Status badges | Color-coded order status indicators |
| Success/error messages | Django messages for user feedback |
| Custom error pages | Branded 403, 404, 405, 500 pages |
| Form validation | Client-side (JS) and server-side (Django) |
| Keyboard navigation | Full accessibility without mouse |
| High contrast support | `prefers-contrast: high` CSS media query |
| Reduced motion | `prefers-reduced-motion: reduce` support |

#### Data Integrity & Security

| Feature | Description |
|---------|-------------|
| Soft delete | Orders marked deleted, not removed from database |
| Audit trail | Every status change logged with user and timestamp |
| Inventory validation | Cannot order more than available stock |
| Ownership enforcement | Users can only edit/delete their own orders |
| CSRF protection | All forms protected against cross-site forgery |
| Role-based access | `@login_required` and view-level permission checks |

---

### Features Screenshots

<details>
<summary>Home Page</summary>

![Home Page](docs/screenshots/home-page.png)
</details>

<details>
<summary>Login Page</summary>

![Login Page](docs/screenshots/login-page.png)
</details>

<details>
<summary>Therapist Dashboard</summary>

![Therapist Dashboard](docs/screenshots/therapist-dashboard.png)
</details>

<details>
<summary>Patient Dashboard</summary>

![Patient Dashboard](docs/screenshots/patient-dashboard.png)
</details>

<details>
<summary>Create Order Form</summary>

![Create Order](docs/screenshots/create-order.png)
</details>

<details>
<summary>Edit Order Form</summary>

![Edit Order](docs/screenshots/edit-order.png)
</details>

<details>
<summary>Delete Confirmation</summary>

![Delete Order](docs/screenshots/delete-order.png)
</details>

<details>
<summary>Equipment List</summary>

![Equipment List](docs/screenshots/equipment-list.png)
</details>

<details>
<summary> Admin Panel</summary>

![Admin Panel](docs/screenshots/admin-panel.png)
</details>

<details>
<summary>Success Message</summary>

![Success Message](docs/screenshots/success-message.png)
</details>

<details>
<summary> Error Message</summary>

![Error Message](docs/screenshots/error-message.png)
</details>

<details>
<summary> 403 Forbidden Page</summary>

![403 Error](docs/screenshots/403-error.png)
</details>

<details>
<summary> 404 Not Found Page</summary>

![404 Error](docs/screenshots/404-error.png)
</details>

<details>
<summary> Mobile Responsive View</summary>

![Mobile View](docs/screenshots/mobile-view.png)
</details>


<details>
<summary>Home Page</summary>

![Home Page](docs/screenshots/home-page.png)
</details>

<details>
<summary>Login Page</summary>

![Login Page](docs/screenshots/login-page.png)
</details>

<details>
<summary>Therapist Dashboard</summary>

![Therapist Dashboard](docs/screenshots/therapist-dashboard.png)
</details>

<details>
<summary>Patient Dashboard</summary>

![Patient Dashboard](docs/screenshots/patient-dashboard.png)
</details>

<details>
<summary>Create Order Form</summary>

![Create Order](docs/screenshots/create-order.png)
</details>

<details>
<summary>Equipment List</summary>

![Equipment List](docs/screenshots/equipment-list.png)
</details>

<details>
<summary>Admin Panel</summary>

![Admin Panel](docs/screenshots/admin-panel.png)
</details>

---

## Design

### Wireframes

Low-fidelity wireframes were created to plan the layout and user flow before development.

| Page | URL | Result |
|------|-----|--------|
| Home | `/` | Pass |
| Login | `/accounts/login/` | Pass |
| Logout | `/accounts/logout/` | Pass |
| Signup Info | `/accounts/signup/` | Pass |
| Therapist Dashboard | `/equipment/dashboard/` | Pass |
| Patient Dashboard | `/equipment/patient/dashboard/` | Pass |
| Equipment List | `/equipment/list/` | Pass |
| Create Order | `/equipment/order/create/` | Pass |
| Edit Order | `/equipment/order/edit/1/` | Pass |
| Delete Confirmation | `/equipment/order/delete/1/` | Pass |
| Admin Panel | `/admin/` | Pass |
| 403 Error | Trigger by accessing restricted page | Pass |
| 404 Error | `/this-page-does-not-exist/` | Pass |
| 500 Error | Server error (test with DEBUG=False) | Pass |

<details>
<summary>Login Page</summary>

![Login Wireframe](docs/wireframes/login-wireframe.png)
</details>

<details>
<summary>Therapist Dashboard</summary>

![Dashboard Wireframe](docs/wireframes/therapist-dashboard-wireframe.png)
</details>

<details>
<summary>Patient Dashboard</summary>

![Patient Dashboard Wireframe](docs/wireframes/patient-dashboard-wireframe.png)
</details>

<details>
<summary>Order Form</summary>

![Order Form Wireframe](docs/wireframes/order-form-wireframe.png)
</details>

*Note: Final implementation evolved from wireframes based on user testing feedback and accessibility requirements.*

---

### Color Scheme

The color palette was chosen to convey trust, professionalism, and calm — essential for a healthcare application.

![Quiporder Color Palette](docs/color_branding/quiporder-colors.png)

*Color palette generated with [Coolors](https://coolors.co/)*

| Role | Color | Hex Code | Usage |
|------|-------|----------|-------|
| Primary | Teal | `#2A9D8F` | Navbar, buttons, headings, links |
| Primary Dark | Dark Teal | `#21867A` | Hover states |
| Success | Green | `#2ECC71` | Success messages, available stock |
| Info | Blue | `#4D96FF` | Information alerts, approved status |
| Warning | Amber | `#F4A261` | Warning alerts, pending status |
| Error | Coral | `#E76F51` | Error messages, delete buttons |
| Background | Off-White | `#F8F9FA` | Page backgrounds |
| Cards | White | `#FFFFFF` | Cards, forms |
| Border | Light Gray | `#E0E0E0` | Form borders, dividers |
| Text | Dark Gray | `#333333` | Headings, body text |
| Text Muted | Slate Gray | `#6C757D` | Help text, labels |

**Color Psychology:**
- **Teal (#2A9D8F):** Conveys trust, calm, and medical professionalism
- **Green (#2ECC71):** Success, positive actions, available
- **Blue (#4D96FF):** Information, approved, professional
- **Amber (#F4A261):** Attention, warnings, pending actions
- **Coral (#E76F51):** Errors, deletions, urgent

**Accessibility:**
- All color combinations meet WCAG 2.1 AA contrast requirements
- High contrast mode supported via `@media (prefers-contrast: high)`
- Reduced motion supported via `@media (prefers-reduced-motion: reduce)`

---

### Typography

| Font | Usage | Reason |
|------|-------|--------|
| **Inter** | Body text, forms | Highly readable, modern, accessible |
| **Roboto** | Headings, titles | Professional, familiar, medical-appropriate |
| System fonts | Fallback | Performance, cross-platform compatibility |

**Font Stack:**
```css
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-heading: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

**Accessibility:**
- Base font size: 16px (1rem)
- Line height: 1.5 for readability
- High contrast ratios (WCAG 2.1 AA compliant)

---

## Technologies Used

### Tech Stack

- **Backend:** Python 3.13+, Django 5.2.8
- **Database:** PostgreSQL 14+
- **Frontend:** HTML5, CSS3, JavaScript
- **Authentication:** Django Allauth with OAuth2 and role-based access control
- **Config & Secrets:** python-decouple + `.env`
- **Deployment targets:** Render / Heroku
- **Version control:** Git (conventional commits)

</br>

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.13 | Backend programming language |
| Django | 5.2.8 | Web framework (MVT architecture) |
| PostgreSQL | 14+ | Relational database |
| HTML5 | - | Page structure and semantics |
| CSS3 | - | Styling and responsive design |
| JavaScript | ES6 | Client-side validation and UX |

### Django Packages & Extensions

| Package | Purpose |
|---------|---------|
| django-allauth | Authentication, login, OAuth2 support |
| django-crispy-forms | Form rendering with Bootstrap 5 |
| crispy-bootstrap5 | Bootstrap 5 template pack for crispy |
| python-decouple | Environment variable management |
| dj-database-url | Database URL parsing for Heroku |
| whitenoise | Static file serving in production |
| gunicorn | Production WSGI HTTP server |
| psycopg2-binary | PostgreSQL database adapter |

### Development Tools

| Tool | Purpose |
|------|---------|
| Git | Version control |
| GitHub | Repository hosting, project management |
| GitHub Projects | Agile kanban board |
| VS Code | Code editor |
| Chrome DevTools | Testing, debugging, responsive design |
| flake8 | Python PEP8 linting |
| W3C Validator | HTML validation |
| Jigsaw | CSS validation |
| JSHint | JavaScript linting |

### Deployment & Hosting

| Service | Purpose |
|---------|---------|
| Heroku | Cloud platform deployment |
| Heroku Postgres | Production database |
| GitHub | Source code repository |

---

### Project Structure

```
quiporder/
│     
└── docs/            
|
└── equipment/  
│   ├── __pycache__
│   ├──  migrations/  
│   ├── __init__.py         
|   ├── admin.py
|   |── apps.py
│   ├── models.py            
│   ├── tests.py             
│   ├── urls.py            
│   └── views.py            
│
└── quiporder/            
│   ├──  __pycache__/       
│   ├── __init__.py        
│   ├── asgi.py            
│   ├── settings.py        
│   ├── urls.py            
│   └── wsgi.py            
│
└──static/                 
|   ├── css/
|   ├── images/
|   └── js/
│
└── templates/  
│   ├── account/
|   |     ├── login.html
|   |     └── signup_closed.html
|   ├── equipment/
|   |     ├── equipment_list.html
|   |     ├── order_confirm_delete.html
|   |     ├── order_form.html
|   |     ├── patient_dashboard.html
|   |     └── therapist_dashboard.html
|   |    
│   ├──  base.html  
│   └──  home.html        
│
└──users/                  
|  ├──  __pycache__/ 
|  ├──  migrations/        
|  ├── __init__.py          
|  ├── admin.py             
|  ├── apps.py              
|  ├── models.py            
|  ├── tests.py             
|  └── views.py             
│
├── .gitignore               
├── manage.py               
├── README.md              
├── requirements.txt      
└── .env                     
```

---

## Testing

Testing documentation is available in a separate file in the root of the repo called TESTING.md

**[View Full Testing Documentation](https://github.com/Alumsdesigns/quiporder/blob/main/TESTING.md)**

### Summary of whats covered in the TESTING document

- HTML validated (W3C)
- CSS validated (W3C Jigsaw)
- JavaScript validated (JSHint)
- Python PEP8 compliant (flake8)
- Lighthouse scores 92-100
- Manual testing completed
- All user stories tested
- Responsive design verified
- Cross-browser tested

### Manual Testing, Admin CRUD Validation

This checklist validates that each core data model can be read, created, edited, and deleted using the Django admin interface, confirming that the data layer is wired correctly before any API or UI work begins

### Local dev Admin Access

Open terminal in root of your project and run 
```python manage.py runserver```

Open the admin panel at:
http://127.0.0.1:8000/admin/

Log in using a staff user account details provided by admin.



### This checklist ensures all models are testable via Django admin

| Step | Model / Action | Data Example | Status  | Notes |
|------|----------------|-------------|----------------|-------|
| 1 | Equipments click Add | Name: Wheelchair, Total: 10, Available: 10 | Tested works as expect | Manual entry |
| 2 | Go to User and Add Occupational Therapist | Username: therapist1, Email: therapist1@example.com, Password: <set>, User type: Occupational Therapist, Is Staff | Tested works as expect | Must be staff tologin to admin |
| 3 | Go to TherapistProfile click Add | User: therapist1, License number: L12345, Max caseload: 20 | Tested works as expect | Optional extra fields |
| 4 | click Add Patient | Username: patient1, Email: patient1@example.com, Password: <set>, User type: PATIENT | Tested works as expect | |
| 5 | PatientProfile click Add | User: patient1, Assigned therapist: therapist1, Medical record: MR001, Status: Active | Tested works as expect | |
| 6 | EquipmentOrder click Add | Equipment: Wheelchair, Patient: patient1, Quantity: 1, Status: Requested |Tested works as expect | Check list, save and verify |
| 7 | Edit Equipment | Change available_quantity from 10 too 9 | Tested works as expect | Confirm persistence to ensure save works |
| 8 | Edit EquipmentOrder | Change quantity and status | Tested works as expect | Confirm persistence to ensure save works |
| 9 | Delete EquipmentOrder | Remove order | Tested works as expect | Check removal reflects |
| 10 | Delete CustomUser / Profiles | Remove test users | Tested works as expect | Ensure deletion works |

> All saves, edits, and deletions completed without error, this means CRUD functionality is validated. See screenshots verification below

---

### Manual testing above Verification in screenshots below

 **Visual evidence** of manual testing completed via the Django Admin interface.  
All screenshots are stored in `docs/screenshots_verify_tests_admin_updates/` and demonstrate successful CRUD operations for users, patients, therapists, and equipment.

---

### 1. User Creation (Therapist & Patient)

#### 1.1 Therapist User Created
Confirms a therapist user was successfully created in Django Admin.

![Therapist User Added](docs/screenshots_verify_tests_admin_updates/user_therapist_added.png)

---

#### 1.2 Multiple Users Created
Confirms multiple users (therapist + patient) exist and were saved correctly.

![Users Created](docs/screenshots_verify_tests_admin_updates/users_created.png)

---

### 2. Therapist Setup

#### 2.1 Therapist Added
Confirms therapist profile creation and association with a user account.

![Add Therapist](docs/screenshots_verify_tests_admin_updates/add_terapist.png)

---

### 3. Patient Setupjshint static/js/forms.js

#### 3.1 Patient Added
Confirms patient user creation.

![Patient Added](docs/screenshots_verify_tests_admin_updates/patient_added.png)

---

#### 3.2 Patient Profile Linked
Confirms patient profile creation and linkage to assigned therapist.

![Patient 1 Added](docs/screenshots_verify_tests_admin_updates/patient1_added.png)

---

### 4. Equipment Management

#### 4.1 Equipment Updated
Confirms equipment quantities can be edited and saved correctly.

![Change Equipment](docs/screenshots_verify_tests_admin_updates/change_eqip.png)

---

#### 4.2 Equipment Deleted
Confirms equipment deletion works as expected.

![Deleted Equipment](docs/screenshots_verify_tests_admin_updates/deleted_eqipment.png)

---

### Summary of Manual testing

All screenshots confirm that:
- Records can be **created**
- Records can be **edited**
- Records can be **deleted**
- Relationships between users, therapists, patients, and equipment function correctly

This validates **manual CRUD testing via Django Admin** for the current implementation.

---

### Manual Database Verification - Django Admin -> PostgreSQL
**Purpose**

This section documents how to verify that data created via the Django Admin UI is persisted correctly in PostgreSQL, and that foreign key relationships are functioning as designed.
To verify that the data created via Django Admin UI exists in PostgreSQL

<details>

This validation confirms that:

- Admin UI inputs are saved to the database

- Migrations are correctly applied

- Relationships between users, profiles, and equipment are intact

- The system behaves correctly beyond the UI abstraction

1. Prerequisites:

- PostgreSQL running

- Django migrations applied

- Test data created via Django Admin UI

- Open terminal in VS Code 

2. Connect to PostgreSQL run below command in the terminal:

```psql -d quiporder```

3. List the tables to inspect existing tables:

```\dt```

Expected tables include:

- users_customuser

- users_patientprofile

- users_therapistprofile

- equipment_equipment

- equipment_equipmentorder


4. Verify the table contents:

```
SELECT * FROM users_patientprofile;
SELECT * FROM users_therapistprofile;
SELECT * FROM equipment_equipment;
SELECT * FROM equipment_equipmentorder;
```

5. Filtering Records Safely
 *Incorrect Assumption, Common Pitfal:*
```SELECT * FROM users_patientprofile WHERE user_id = 1;```


This may return 0 rows, even though the patient exists.

*Why?*

Django Admin does not display database primary keys

id = 1 is typically the first created user, often a superuser or admin

The patient user likely has a different id


 Filter for specific records (example for patient1):

Tip: The id column is usually the primary key; use it to reference specific records for further queries.


6. Filter by ID or name

By ID:
```
SELECT * 
FROM users_patientprofile
WHERE id = 1;
```

**To filter by username see 7 & 8 below**


7. Check the table columnsand inspect the table structure

Always inspect the schema before querying:

Run:
```\d users_patientprofile```

Key insight:

user_id is a foreign key referencing users_customuser(id)

Human-readable fields (username, email) are not stored here

The important thing: there’s a user_id column, which references the CustomUser table

8. Authoritative Verification Using JOINs to view the username

You can join users_patientprofile with users_customuser to see patient1:

Correct Way to Verify a Patient Profile:

```
SELECT p.id AS patient_id,
       u.username,
       p.medical_record_number,
       p.status,
       p.admission_date
FROM users_patientprofile p
JOIN users_customuser u ON p.user_id = u.id
WHERE u.username = 'patient1';
```

Why this works:

Filters using a human identifier

PostgreSQL resolves the correct user_id internally

Confirms both persistence and FK integrity

9. Verify Therapist Profiles

```
SELECT t.id AS therapist_profile_id,
       u.username,
       t.license_number
FROM users_therapistprofile t
JOIN users_customuser u ON t.user_id = u.id;

```

10. Verify Equipment Records

```
SELECT id, name, total_quantity, available_quantity
FROM equipment_equipment;
```

next look at updating with size so will be

```
SELECT id, name, category, size, total_quantity, available_quantity
FROM equipment_equipment;
```

11. Verify Equipment Orders

```
SELECT eo.id,
       e.name AS equipment,
       u.username AS patient,
       eo.quantity,
       eo.status
FROM equipment_equipmentorder eo
JOIN equipment_equipment e ON eo.equipment_id = e.id
JOIN users_customuser u ON eo.patient_id = u.id;
```

**Learnings**

When I tried to verify by ID, I assumed if I knew the user_id (from the UI), I could also filter:

```SELECT * FROM users_patientprofile WHERE user_id = 1;```

I initially assumed should return the patient profile for patient1. However it returned :
0 rows. This is because user_id = 1 is not the user ID for patient1.
In Django the admin UI does NOT show the database primary key

The first user created is often a superuser or a staff/admin account

So id = 1 is very commonly the admin user, not the patient1 user I created for example.

That means:

users_customuser.id = 1  → admin
users_customuser.id = X  → patient1 (X is some other number)


My users_patientprofile row correctly exists, but it is linked to:

users_patientprofile.user_id = X


not 1.

**Why the JOIN query worked to find my users_patientprofile.user_id**

However when I ran the below json query to filter by username:
```
SELECT p.id AS patient_id,
       u.username,
       p.medical_record_number,
       p.status,
       p.admission_date
FROM users_patientprofile p
JOIN users_customuser u ON p.user_id = u.id
WHERE u.username = 'patient1';
```

This query is correct and authoritative. 

It worked because:

I filtered by a real human identifier (username).

PostgreSQL then resolved the correct user_id internally.

This confirms:

- The admin UI entry is persisted.

- The foreign key relationship is correct.

- The table data is real and queryable.

- So the system is working as designed.

**How to reliably find the correct user_id**

Always do this first

```
SELECT id, username, email, user_type
FROM users_customuser
ORDER BY id;
```
You will see something like:

 id |  username  |         email          | user_type 
----+------------+------------------------+-----------
  1 | Damaris    |                        | THERAPIST
  4 | therapist1 | therapist1@example.com | THERAPIST
  5 | patient1   | patient1@example.com   | PATIENT
(3 rows)

Now you know:

```patient1.user_id = 5```

Then this will work:
```SELECT * FROM users_patientprofile WHERE user_id = 5;```

The 
```SELECT p.id AS patient_profile_id,
       u.username,
       p.medical_record_number,
       p.status,
       p.admission_date
FROM users_patientprofile p
JOIN users_customuser u ON p.user_id = u.id;
```

</details>


</br> 

**Key Takeaways**

<details>

Django Admin often stores user info in CustomUser. Related models (like PatientProfile) reference it via foreign key.

Don’t assume the username is a column in the profile table.

Use ```\d table_name``` example ```\d users_patientprofile``` to inspect columns anytime.

Joins are necessary to see human-readable fields like username or email.


Django Admin UI does not display database primary keys.

Profile tables reference users_customuser via foreign keys.

Always join profile tables to users_customuser to verify human-readable fields.

If a direct WHERE user_id = X query returns no rows, verify the correct user ID first.

</details>

</br>

**See screenshots of commands executed:**
The screenshots below demonstrate direct PostgreSQL verification of data created via the Django Admin interface. They show successful execution of psql commands to inspect schemas, query tables, and validate foreign key relationships between CustomUser, profile, and equipment-related models. This confirms that Admin UI actions are correctly persisted to PostgreSQL, migrations are applied as intended, and relational integrity is enforced at the database level.
![PostgreSQL table inspection and schema verification](docs/screenshots_verify_tests_admin_updates/psql_test_1.png)
![Joined queries validating user, profile, and foreign key relationships](docs/screenshots_verify_tests_admin_updates/psql_test_2.png)
![Equipment and equipment order queries confirming persisted admin data](docs/screenshots_verify_tests_admin_updates/psql_test_3.png)


**Summary**

What screenshots proves:

- Admin UI input is being written to PostgreSQL

- Migrations are applied correctly

- Foreign key relationships are intact

- Your CRUD setup is working end-to-end


### Iteration improvements from round 1 Observational User Testing of the admin panel

#### Testing Context

Three anonymous users (two occupational therapists and one patient) were asked to complete the manual UI testing flow using a pre-configured system.
Users were observed interacting with:

1. Patient profiles

2. Therapist profiles

3. Equipment ordering workflows

Post-session feedback was collected through guided questions, focusing on usability, clarity, and workflow efficiency.

#### Key Observations & Improvements

**1. Enhanced Human-Readable Data in ERD:**

Previous issue: Some tables (e.g., EquipmentOrder) lacked direct references to patient or therapist information, which required multiple lookups and could introduce inconsistencies if names or MRNs changed.

**Improvement:**

- All CustomUser data (first_name, last_name, DOB, email) is stored once in the CustomUser table.

- PatientProfile and TherapistProfile reference CustomUser via foreign keys.

- Names, DOB, and email are derived via FK rather than stored redundantly.

**Reasoning:**

This follows DRY principles (Don’t Repeat Yourself), avoids duplicated facts, and ensures consistency.

Any updates to a user’s name or email automatically propagate across all related profiles and orders.

**2. Equipment & Order Normalization:**
Previous issue: Equipment attributes like size and category were unclear or conflated.

**Improvement:**

- Added size field to Equipment (Small / Medium / Large / Custom) separate from category (Mobility / ADL / Sensory).

- EquipmentOrder references PatientProfile via FK instead of storing patient names or MRNs.

**Reasoning:**

Keeps single source of truth for patient details.

Supports reporting and analytics without risk of inconsistent or outdated data.

**3. Status Fields Clarified:**

PatientProfile.status: ACTIVE / DISCHARGED, reflects clinical workflow.

EquipmentOrder.status: PENDING / APPROVED / IN_TRANSIT / DELIVERED / CANCELLED, reflects logistics workflow.

**Reasoning:**

- Clear separation of concerns avoids confusion between clinical status and equipment workflow.

- Supports KISS principle (Keep It Simple, Stupid) by keeping workflows explicit and easy to track.

**4. Assigned Therapist via FK:**

Previous issue: Some systems store therapist name directly on PatientProfile.

**Improvements:**

- Store assigned_therapist_id FK to TherapistProfile instead of the therapist name.

- Display names derived dynamically through FK in UI/API.

**Reasoning:**

- Avoids duplication and errors if therapist name changes.

- Ensures SOLID principle (Single Responsibility) — PatientProfile tracks assignment, not therapist identity.

**5. General Observational Feedback Incorporated:**

**Users appreciated:**

- Easier reading of patient and therapist details through consistent naming display.

- Equipment details being separated into category and size for clarity.

**Users requested:**

Improved admin interface to display derived names and email directly for search and filtering implemented in admin refinements.


**Observations**

 While the underlying data model and database relationships fully support Quiporder’s functional requirements at this stage, further UI refinements are required to align the user interface with the intended therapist and patient workflows outlined in the flow diagram below:


```mermaid
flowchart TD
    %% QuipOrder MVP - CRUD Flow (Layered for VS Code readability)

    %% LOGIN LAYER
    subgraph LOGIN
        A[User Login]
        A --> B{User Type?}
    end

    %% DASHBOARD LAYER
    subgraph DASHBOARD
        B -->|Therapist| C[Therapist Dashboard]
        B -->|Patient| D[Patient Dashboard]
    end

    %% THERAPIST CRUD LAYER
    subgraph PATIENT_MANAGEMENT
        C --> E[Manage Patients CRUD]
        E --> E1[Create Patient]
        E --> E2[Read/View Patients List & Details]
        E --> E3[Update Patient Details]
        E --> E4[Delete Patient]
    end

    subgraph EQUIPMENT_MANAGEMENT
        C --> F[Manage Equipment CRUD]
        F --> F1[Create Equipment]
        F --> F2[Read/View Equipment List]
        F --> F3[Update Equipment Stock/Info]
        F --> F4[Delete Equipment]
    end

    subgraph ORDER_MANAGEMENT
        C --> G[Manage Orders CRUD]
        G --> G1[Create Order for Patient]
        G --> G2[Read/View Orders]
        G --> G3[Update Order Status/Quantity]
        G --> G4[Delete/Cancel Order]
    end

    %% PATIENT LAYER
    subgraph PATIENT_VIEW
        D --> H[View My Orders Only Read-Only]
        H --> H1[See Order Status: Pending → Approved → In Transit → Delivered]
    end

    %% COLOR STYLING
    style C fill:#78C7A6,stroke:#333,stroke-width:2px
    style D fill:#56CFE1,stroke:#333,stroke-width:2px
    style E fill:#2A9D8F,stroke:#333
    style F fill:#2A9D8F,stroke:#333
    style G fill:#2A9D8F,stroke:#333
    style H fill:#56CFE1,stroke:#333
```
*Improvements Implemented & Identified*

Custom role-based dashboards should be introduced to complement or replace Django Admin for core CRUD operations in future iterations. These changes would improve usability, enforce clearer role separation, and ensure the interface accurately reflects the system’s real capabilities.

**1.** In particular keeping admin panel for staff level access only with CRUD functionality and the ability to update

**2.** And creating a UI for both Patient and Occupational Terapist needs with relevant Role Baed Access
Ui 
   - **a)** Patient  Dashboard  -> login -> Read view only orders assigned to the patient on the dashboard if such exist
- **b)** Terapist Dashboard -> Login -> CRUD functionality, create orders, view orders, update/edit orders and delete orders 


</br>

### Testing Updates after anonymous observational usability testing 

**Subjects: 5 users - 3 therapist and 2 users
Date:  20-12-2025**

The request was for a view to see which user had superuser permissions, this was added as per below

##### **BEFORE Old Code:**
```
Username | First | Last | Email | DOB | Role | Active | Staff
---------|-------|------|-------|-----|------|--------|------
admin    | Admin | User | ...   | ... |      | ✓      | ✓     ← Blank! Confusing!
drjones  | Dr.   | Jones| ...   | ... | THERAPIST | ✓ | ☐
patient1 | John  | Doe  | ...   | ... | PATIENT   | ✓ | ☐
```

##### **AFTER view with Updates:**
```
Username | First | Last | Email | DOB | Role                      | Active | Staff | Superuser
---------|-------|------|-------|-----|---------------------------|--------|-------|----------
admin    | Admin | User | ...   | ... | System Administrator      | ✓      | ✓     | ✓
drjones  | Dr.   | Jones| ...   | ... | Occupational Therapist    | ✓      | ☐     | ☐
patient1 | John  | Doe  | ...   | ... | Patient 
```


---

### Overall Testing Summary

### 1. Manual Admin CRUD Testing

- All core models (CustomUser, TherapistProfile, PatientProfile, Equipment, EquipmentOrder) tested via Django Admin for create, read, update, delete.
- Steps and sample data are documented in this README (see Manual Testing section above).
- Screenshots stored under:
  - `docs/screenshots_verify_tests_admin_updates/`
  - `docs/screenshots_verify_tests/` (psql verification)

### 2. Database Verification (PostgreSQL)

- Used `psql` to:
  - List tables (`\dt`) and inspect schemas (`\d table_name`)
  - Verify FK relationships via JOINs between `users_customuser`, `users_patientprofile`, `users_therapistprofile`, `equipment_equipment`, and `equipment_equipmentorder`.
- Example JOIN queries are documented in this README to show how patient and therapist records are resolved via foreign keys.

### 3. Code Quality

- **Python:** flake8 run on `equipment/`, `users/`, `quiporder/` with:
  - `--max-line-length=120`
  - `--exclude=migrations,__pycache__`
  - `--ignore=E501,W503,W504`
- Final status: 0 flake8 errors – Python code is PEP8 compliant.

### 4. Frontend Validation

- **HTML:** all key templates validated via W3C Markup Validation Service.
- **CSS:** validated using W3C Jigsaw CSS validator.

Details and screenshots can be found in TESTING.md


### Testing Summary

All code has been validated and follows industry standards. No critical errors found found at present.

</details>

## Future Features

### Planned for Q2 2025 (April)

Below are a list of future plans. I have placed these on my Github projects kanban board called "called Alumsdesigns's Portfolio 4 Code Institute"  in a column titled "Future Quater April 2025" epic with task, [view](https://github.com/users/Alumsdesigns/projects/4)

| Feature | Description | Priority |
|---------|-------------|----------|
| Patient Search Functionality | Search/filter patients by name or MRN | Medium |
| Pagination | Add pagination to order lists and tables | Medium |
| Maybe Footer Navigation | Add useful links to footer | Low |

### Backlog (Future Consideration)

| Feature | Description | Status |
|---------|-------------|--------|
| Create Patient Form | Allow therapists to create patients via UI (not just admin) | Backlog |
| Forgot Password | Password reset via email | Backlog |
| Better Calendar Picker | Improved date selection UI | Backlog |
| GitHub Actions CI Pipeline | Automated testing on push/PR | Backlog |
| Browser Cache Security | Investigate cache clearing on logout | Spike |
| Order Action Improvements | Better UX when therapist didn't create order | Spike |
| Status History Deletion | Investigate if deletion should be prevented | Spike |
| Signup Page Review | Evaluate signup_closed vs open registration | Spike |

### UX Improvements Identified

| Improvement | Description |
|-------------|-------------|
| Username dropdown | Show full name in parentheses when selecting users |
| Empty state messaging | Better feedback when no orders exist |
| Mobile table scrolling | Improved horizontal scroll indicators |

### Out of Scope (This Release)

The following features were intentionally excluded from MVP to focus on core functionality:

- Patient creation by therapists (admin-only for security)
- Email notifications for order status changes
- PDF export of order history
- Multi-language support
- Dark mode theme

---

## Setup Instructions

Quiporder is a Full-Stack Django application for occupational therapists to manage patient equipment orders. Follow these steps to set up the project locally.


### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13+** - [Download Python](https://www.python.org/downloads/)
- **PostgreSQL 14+** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **Git** - [Download Git](https://git-scm.com/downloads/)
- **pip3** - Python package installer (included with Python)

___

### Installation Steps

#### 1. Clone the Repository
```bash
git clone git@github.com:Alumsdesigns/quiporder.git
cd quiporder
```

Or using HTTPS:
```bash
git clone https://github.com/Alumsdesigns/quiporder.git
cd quiporder
```

---

#### 2. Create Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt indicating the virtual environment is active.

---

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs all required Python packages including Django, psycopg2, django-allauth, and python-decouple.


---

#### 4. Setup Environment Variables

Create a `.env` file in the project root directory:
```bash
touch .env
```

Add the following to `.env`:
```env
SECRET_KEY=your-generated-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=quiporder
POSTGRES_USER=yourusername. # Must match your Postgres superuser role
POSTGRES_PASSWORD=yourpassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```


Verify environment variables are set in terminal, example run:
```echo #POSTGRES_DB``` you should see quiporder if you do not you can export this in your terminal, its also good practice to set in your .zshrc or check you are not overriding it in zshrc or by running the echo command. To export them direct in the terminal you can run ```POSTGRES_PORT=5432``` check all variavles are set in wth the same ```echo $variable-name``` command in the terminal

**Important:** 
- Replace `your-generated-secret-key-here` with the key from step 6 below
- Replace `yourusername` and `yourpassword` with your PostgreSQL credentials
- **Never commit `.env` to version control** (already in `.gitignore`)

---

#### 5. Generate Secret Key

Django requires a secret key for security. Generate one using:
```bash
python manage.py shell
```

Then in the Python shell:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
exit()
```

**Copy the generated key** - you'll need into your .env file you created in dstep 4.

Exit the shell type ```exit()``` and enter

---

#### 6. Setup PostgreSQL Database

**Start PostgreSQL:**

**macOS (Homebrew):**
```bash
brew services start postgresql
```

**Linux:**
```bash
sudo service postgresql start
```

**Windows:** PostgreSQL should start automatically, or use pgAdmin.

**Verify Postgres is running:**
```brew services list | grep postgres```
```pg_isready -h localhost -p 5432```

You should see accepting connections on port 5432.


**Next you need to run and create your database:**

```bash
# Login to PostgreSQL Login to PostgreSQL 
psql -U postgres

# Example Connects as role myuser to database mydatabase:
psql -U myuser -d mydatabase


# First Check existing databases:
\l

# Create database
CREATE DATABASE quiporder;

# Verify roles: 
\du

# Create user (optional - use your own credentials)
CREATE USER <enter-a-made-up-username> WITH PASSWORD <'enter-a-password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE quiporder TO yourusername;

# Exit PostgreSQL
\q
```
Update your .env variables with POSTGRES_USER and POSTGRES_PASSWORD with the username and password you chose

---

#### 7. Verify PostgreSQL Connectivity
Before running migrations, confirm Django can connect:
**Using current OS user (default)**
```psql -d quiporder```

 **OR, specify a Postgres user explicitly**
```psql -U <your_postgres_user> -d quiporder```

Should connect without errors.
Optional: check inside psql:
```\l ```   -- list databases
```\dt ```  -- list tables (should be empty initially)
```\q```    -- exit

---

#### 8. Run Database Migrations

Apply database migrations to create all required tables:
```bash
python manage.py makemigrations
python manage.py migrate
```

You should see output confirming migrations were applied.

---

#### 9. Create Django Superuser (Admin)

Create an admin account to access the Django admin panel:
```bash
python manage.py createsuperuser
```

Follow the prompts to set:

**Prompts and answers:**
```
Username
User type (THERAPIST/PATIENT): THERAPIST
Password: ********
Password (again): ********
Superuser created successfully.
```

**Important:** This superuser will have full admin access. Regular therapist and patient accounts should be created through the admin panel after logging in.

---

#### 10. Run Development Server

Start the Django development server:
```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

---

#### 11. Access the Application

**Main Site:**
- Visit: http://127.0.0.1:8000/
- You should see the Quiporder home page

**Admin Panel:**
- Visit: http://127.0.0.1:8000/admin/
- Login with superuser credentials from step 8
- Create therapist and patient accounts here

---

#### Optional: Collect Static Files

Only needed if static files aren't loading locally:
```bash
python manage.py collectstatic --noinput
```

---

### Troubleshooting

#### Database Connection Error
```bash
# Verify PostgreSQL is running
pg_isready

# Check database exists
psql -l

# Verify credentials in .env file
```

#### Migration Errors
```bash
# Reset migrations ( WARNING: Data loss!)
python manage.py migrate --run-syncdb
```

#### Module Not Found Error
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### Port Already in Use
```bash
# Use different port
python manage.py runserver 8001
```

or follow the guide at the bottom of 4. Setup Environment Variables above

---

### Next Steps

Once the server is running:

1. **Create User Accounts:**
   - Go to http://127.0.0.1:8000/admin/
   - Add therapist and patient users
   - Set user types and activate accounts

2. **Add Equipment:**
   - Navigate to Equipment in admin panel
   - Add equipment items with quantities

3. **Test Features as Therapist:**
   - Login as therapist
   - Create equipment orders
   - Test CRUD operations

4. **Test Features as Patient:**
   - Login as patient
   - View orders

---

## Deployment

Quiporder is deployed on Heroku, a cloud platform that supports PostgreSQL databases and Python applications.

**Live Site:** [View Deployed Site](https://quiptorder-f48affb2ee2c.herokuapp.com/)


### Prerequisites for Deployment

#### Post-Deployment Checklist
Before deploying, ensure you have


- [ ] A [Heroku account](https://signup.heroku.com/)
- [ ] [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
- [ ] Git repository with all code committed
- [ ] `requirements.txt` file up to date
- [ ] `Procfile` in project root
- [ ] Project tested locally

#### **Security:**
- [ ] `DEBUG = False` in production
- [ ] Secret keys not in git repository
- [ ] `.env` file in `.gitignore`
- [ ] `ALLOWED_HOSTS` configured correctly

#### **Database:**
- [ ] Migrations applied on Heroku
- [ ] Superuser created
- [ ] Test data added (if needed)

#### **Static Files:**
- [ ] `collectstatic` run successfully
- [ ] CSS/JS loading correctly
- [ ] Images displaying properly

#### **Functionality:**
- [ ] Login/Logout working as admin, therapist and patient
- [ ] CRUD operations working in admin and for therapists
- [ ] Patient logs i and can view orders only, if there is any
- [ ] Admin panel accessible
- [ ] All pages loading correctly

---

### Production Deployment Steps

For production Heroku, the SECRET_KEY is stored in Config Vars (environment variables) and never committed to the repository.

#### 1. Create Heroku App

**Via Heroku Dashboard:**

1. Login to [Heroku](https://heroku.com/)
2. Click **"New"** → **"Create new app"**
3. Choose a unique app name (e.g., `quiporder-app`)
4. Select your region (Europe or United States)
5. Click **"Create app"**

**Or via Heroku CLI:**
```bash
heroku login
heroku create quiporder-app
```

---

#### 2. Add PostgreSQL Database

**Via Heroku Dashboard:**

1. Go to **Resources** tab
2. In **Add-ons** search bar, type: `postgres`
3. Select **"Heroku Postgres"**
4. Choose plan: **"Hobby Dev - Free"**
5. Click **"Submit Order Form"**

**Or via Heroku CLI:**
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

---

#### 3. Configure Environment Variables

**Via Heroku Dashboard:**

1. Go to **Settings** tab
2. Click **"Reveal Config Vars"**
3. Add the following config vars:

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | *Auto-populated by Heroku Postgres* | Leave as-is |
| `SECRET_KEY` | *Your Django secret key* | Generate new one for production |
| `DEBUG` | `False` | **CRITICAL: Must be False** |
| `ALLOWED_HOSTS` | `quiporder-app.herokuapp.com` | Your Heroku app URL |
| `DISABLE_COLLECTSTATIC` | `1` | Temporary - remove before final deployment |

**Generate Production Secret Key:**
```bash
python manage.py shell
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
exit()
```

**Or via Heroku CLI:**
```bash
heroku config:set SECRET_KEY="your-secret-key-here"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="quiporder-app.herokuapp.com"
heroku config:set DISABLE_COLLECTSTATIC=1
```

---

#### 4. Update Django Settings

**File: `quiporder/settings.py`**

Ensure these settings are configured for deployment:
```python
import os
import dj_database_url

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Database
DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

---

#### 5. Create Procfile

**File: `Procfile`** (in project root, no file extension)
```
web: gunicorn quiporder.wsgi
```

This tells Heroku how to run your application.

---

#### 6. Update Requirements

Ensure `requirements.txt` includes deployment dependencies:
```bash
pip install gunicorn dj-database-url psycopg2-binary
pip freeze > requirements.txt
```

**Verify these are in `requirements.txt`:**
- `gunicorn` - WSGI HTTP Server
- `dj-database-url` - Database URL parser
- `psycopg2-binary` - PostgreSQL adapter

---

#### 7. Commit Changes
Always use conventional commit messages:
```bash
git add .
git commit -m "chore(deploy): configure for Heroku deployment

DEPLOYMENT SETUP:
- Add Procfile for gunicorn
- Update settings for production
- Add deployment dependencies
- Configure environment variables

Refs #deployment"
```
---

#### 8. Deploy to Heroku

**Via Git:**
```bash
# Add Heroku remote
heroku git:remote -a quiporder-app

# Push to Heroku
git push heroku main
```

**Or via Heroku Dashboard:**

1. Go to **Deploy** tab
2. **Deployment method:** Select **"GitHub"**
3. Click **"Connect to GitHub"**
4. Search for repository: `quiporder`
5. Click **"Connect"**
6. **Manual deploy:** Select branch `main`
7. Click **"Deploy Branch"**

---

#### 9. Run Migrations on Heroku
```bash
heroku run python manage.py migrate
```

---

#### 10. Create Superuser on Heroku
```bash
heroku run python manage.py createsuperuser
```

Follow prompts to create admin account.

---

#### 11. Collect Static Files

**Remove `DISABLE_COLLECTSTATIC` config var:**
```bash
heroku config:unset DISABLE_COLLECTSTATIC
```

**Collect static files:**
```bash
heroku run python manage.py collectstatic --noinput
```

---

#### 12. Open Application
```bash
heroku open
```

Or visit: `https://quiporder-app.herokuapp.com`

___

### Updating the Deployed Site

**After making changes locally:**
```bash
# 1. Test locally
python manage.py runserver

# 2. Commit changes
git add .
git commit -m "your commit message"

# 3. Push to GitHub
git push origin main

# 4. Deploy to Heroku
git push heroku main

# 5. Run migrations if needed
heroku run python manage.py migrate
```

**Or enable automatic deploys:**

1. Go to **Deploy** tab on Heroku Dashboard
2. **Automatic deploys:** Click **"Enable Automatic Deploys"**
3. Every push to `main` branch will auto-deploy

---

### Troubleshooting Deployment

#### Application Error (H10)
```bash
# Check logs
heroku logs --tail

# Common causes:
# - Missing Procfile
# - Wrong Procfile format
# - Incorrect WSGI path
```

#### Database Connection Error
```bash
# Verify DATABASE_URL
heroku config:get DATABASE_URL

# Reset database (DATA LOSS!)
heroku pg:reset DATABASE_URL
heroku run python manage.py migrate
```

#### Static Files Not Loading
```bash
# Verify DISABLE_COLLECTSTATIC is unset
heroku config

# Re-collect static files
heroku run python manage.py collectstatic --noinput
```

#### Check Application Status
```bash
# View app info
heroku info

# Check dyno status
heroku ps

# View recent logs
heroku logs --tail
```

---

### Heroku CLI Commands Reference
```bash
# View logs
heroku logs --tail

# Run Django commands
heroku run python manage.py <command>

# Open Python shell
heroku run python manage.py shell

# Restart dyno
heroku restart

# View config vars
heroku config

# Scale dynos
heroku ps:scale web=1
```

---

## Security & Data Protection

### Overview

Quiporder implements comprehensive security measures to protect sensitive patient and healthcare data in compliance with data protection regulations. The system follows Django security best practices and healthcare industry standards.

---

### Authentication & Authorization

#### Role-Based Access Control (RBAC)

**Three-tier access model:**

1. **Staff/Admin Users**
   - Full system access via Django Admin
   - User and profile management (CRUD)
   - Equipment inventory management
   - Audit trail access
   - Permission: `is_staff=True` or `is_superuser=True`

2. **Therapist Users**
   - Therapist dashboard access
   - Equipment order management (CRUD within 24-hour window)
   - View assigned patient records
   - Limited to own orders for edit/delete
   - Permission: `user_type='THERAPIST'` and `is_active=True`

3. **Patient Users**
   - Patient dashboard access (read-only)
   - View own equipment orders only
   - No create/edit/delete permissions
   - Permission: `user_type='PATIENT'` and `is_active=True`

**Enforcement Points:**
- View decorators: `@login_required`
- View-level checks: `if request.user.user_type != 'THERAPIST'`
- Template conditionals: `{% if user.is_staff %}`
- Admin permissions: Django's built-in `is_staff` and `is_superuser`

---

### Account Registration & Approval

#### Restricted Registration

**Why signup is closed to public registration:**

Quiporder restricts self-registration to maintain data security and ensure only authorized healthcare professionals and verified patients access the system. This design decision addresses several critical requirements:

1. **Healthcare Compliance:**
   - Only verified healthcare professionals should access patient data
   - Patient accounts must be linked to verified medical records
   - Staff must validate user identity before granting access

2. **Data Protection:**
   - Prevents unauthorized access to sensitive medical information
   - Ensures GDPR/HIPAA-style data handling
   - Maintains audit trail of who created each account

3. **Professional Context:**
   - Therapists must have valid licenses (verified by staff)
   - Patients must be assigned to specific therapists
   - Maintains proper clinical relationships

**Account Creation Workflow:**

1. **Staff creates user account** in Django Admin
   - Sets `user_type` (THERAPIST or PATIENT)
   - Sets `is_active=False` initially
   - Generates temporary password

2. **Staff creates corresponding profile:**
   - TherapistProfile (with license number)
   - OR PatientProfile (with medical record number, assigned therapist)

3. **Staff activates account:**
   - Sets `is_active=True`
   - User receives credentials via secure communication

4. **User logs in:**
   - Django Allauth handles authentication
   - Redirected to appropriate dashboard based on `user_type`

**User Communication:**

The signup page (`/accounts/signup/`) displays:
- Explanation of admin-only account creation
- Instructions for new employees to contact HR/admin
- Security rationale (data protection)
- Admin instructions for account creation workflow

This approach demonstrates:
- An understanding of real-world healthcare security needs
- Professional communication with users
- Thoughtful UX design for restricted access
- Compliance-first architecture

---

### Secret Management

#### Security Incident Disclosure

**Timeline:**
- **Dec 29, 2025:** Django `SECRET_KEY` accidentally committed to repository in plaintext
- **Dec 30, 2025:** Issue identified and remediated

**Impact:**
- Exposed key (`django-insecure-1*#%*n...`) was development-only
- No production deployment occurred with exposed key
- No user data or passwords compromised
- Issue caught before public release

**Remediation Actions:**

1. **Immediate Key Rotation**
```python
   # Generated new SECRET_KEY
   python manage.py shell
   >>> from django.core.management.utils import get_random_secret_key
   >>> print(get_random_secret_key())
```

2. **Environment Variable Migration**
   - Moved `SECRET_KEY` from `settings.py` to `.env` file
   - Added `.env` to `.gitignore`
   - Configured `python-decouple` for environment variable management

3. **Settings Update**
```python
   # quiporder/settings.py
   from decouple import config
   
   SECRET_KEY = config('SECRET_KEY')
   DEBUG = config('DEBUG', default=False, cast=bool)
   ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')
```

4. **Documentation**
   - Created `.env` template
   - Updated README with setup instructions
   - Added security best practices section

5. **Old Key Invalidated**
   - Previous key no longer in use
   - All environments using new key
   - Git history contains invalid key only

---

#### Current Security Posture

**Local Development:**
```env
# .env (gitignored)
SECRET_KEY=<generated-secret-key>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=quiporder
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<password>
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

**Production Deployment (Heroku):**
```bash
# Config Vars (environment variables)
heroku config:set SECRET_KEY="<production-secret-key>"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="quiporder-app.herokuapp.com"
heroku config:set DATABASE_URL="<auto-populated>"
```

**Security Checklist:**
- [ ] SECRET_KEY in environment variables (not in code)
- [ ] `.env` file in `.gitignore`
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS configured correctly
- [ ] Database credentials in environment variables
- [ ] No hardcoded passwords in repository

---

### Django Security Features

#### Built-in Protections

1. **CSRF Protection**
   - Django middleware validates CSRF tokens on all POST requests
   - `{% csrf_token %}` in all forms
   - Prevents cross-site request forgery attacks

2. **SQL Injection Prevention**
   - Django ORM uses parameterized queries
   - User input never directly concatenated into SQL
   - Example: `Equipment.objects.filter(id=user_input)` This is Safe

3. **XSS Prevention**
   - Django templates auto-escape HTML by default
   - `{{ variable }}` automatically escapes `<script>` tags
   - Manual escaping: `{{ variable|escape }}`

4. **Password Security**
   - Passwords hashed using PBKDF2 algorithm (default)
   - Salted hashes stored in database
   - Plain text passwords never stored

5. **Clickjacking Protection**
   - `X-Frame-Options: DENY` header
   - Prevents site from being embedded in iframe

6. **HTTPS Enforcement (Production)**
```python
   # settings.py (production)
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
```

---

### Access Control Implementation

#### View-Level Security

**Decorator-based:**
```python
@login_required
def therapist_dashboard(request):
    if request.user.user_type != 'THERAPIST' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Therapists only.')
        return redirect('home')
    # ... view logic
```

**Template-level:**
```django
{% if user.is_authenticated %}
    {% if user.user_type == 'THERAPIST' %}
        <a href="{% url 'order_create' %}">Create Order</a>
    {% endif %}
{% endif %}
```

**Model-level (Ownership):**
```python
# Users can only edit their own orders
if order.created_by != request.user:
    messages.error(request, 'You can only edit your own orders.')
    return redirect('therapist_dashboard')
```

---

### Data Protection

#### Audit Trail

**Status History Tracking:**
- Every order status change recorded in `EquipmentOrderStatusHistory`
- Captures: old_status, new_status, changed_by, changed_at
- Immutable records (no edit/delete for non-superusers)
- Accessible to staff via Django Admin

**Soft Delete:**
- Orders marked as deleted (not removed from database)
- `deleted_at` timestamp and `deleted_by` user recorded
- Preserves audit trail and referential integrity
- Allows recovery if needed

#### Database Security

**PostgreSQL Configuration:**
- User accounts with minimum required privileges
- Separate credentials for development and production
- Connection pooling for performance and security
- Encrypted connections in production (Heroku SSL)

**Data Integrity:**
- Foreign key constraints enforce relationships
- NOT NULL constraints on required fields
- Unique constraints on sensitive identifiers (email, MRN)
- Check constraints on inventory (available ≤ total)

---

### Production Security

#### Heroku Deployment

**Environment Isolation:**
```python
# settings.py
import os

# Never True in production
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Only allowed domains
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
```

**Secret Management:**
- All secrets in Heroku Config Vars
- Never committed to git
- Rotated regularly
- Different keys for development and production

**HTTPS Enforcement:**
```python
# Production settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

### Best Practices Followed

#### Development
- Virtual environment for dependency isolation
- `.gitignore` includes `.env`, `__pycache__`, `db.sqlite3`
- Requirements.txt for reproducible builds
- Conventional commits for audit trail

#### Code
- PEP8 compliance (flake8 validation)
- No hardcoded credentials
- Parameterized database queries (ORM)
- Input validation on all forms
- Error handling with user-friendly messages

#### Deployment
- DEBUG=False in production
- ALLOWED_HOSTS explicitly configured
- Static files served via Whitenoise/CDN
- Database backups (Heroku automated)
- Logging configured for monitoring

---

### Future Security Enhancements

**Planned for future iterations:**

1. **Two-Factor Authentication (2FA)**
   - SMS or TOTP for therapist accounts
   - Extra security for accessing patient data

2. **Session Management**
   - Automatic logout after inactivity
   - Session expiration for shared computers
   - "Remember me" option with secure tokens

3. **Password Policies**
   - Minimum complexity requirements
   - Password expiration (e.g., 90 days)
   - Password history (prevent reuse)

4. **API Rate Limiting**
   - Prevent brute force login attempts
   - Throttle API requests

5. **Security Logging**
   - Log all authentication attempts
   - Log permission denied events
   - Alert on suspicious activity

6. **Data Encryption at Rest**
   - Encrypt sensitive fields (notes, MRN)
   - Database-level encryption

---

### Note for Assessors

This security implementation demonstrates:

- **LO3 (Authentication & Authorization):** Role-based login with restricted access
- **LO6.4 (Security):** DEBUG=False, secrets in environment variables, no passwords in git
- **Industry Best Practices:** CSRF protection, password hashing, input validation
- **Real-World Application:** Healthcare-appropriate security model
- **Transparency:** Security incident properly disclosed and remediated
- **Compliance-Ready:** Audit trails, soft deletes, access controls

All security measures follow Django documentation and OWASP recommendations.

---

## License
Educational project for Code Institute Portfolio Project 4.

---

## Acknowledgement
I would like to thank my mentor, Brian Macharia, for providing very good advice, tips and feedback, as well as excellent resources that aided greatly in organising and implementing this project.