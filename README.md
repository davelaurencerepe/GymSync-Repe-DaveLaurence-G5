# GymSync

GymSync is a gym management web application built with Django and PostgreSQL (Supabase). It keeps member, membership, and payment records in one organized system, with role-based access for Admin, Staff, and Member users.

**Course:** IM2 / IT317 - Project Development 2 (Core Feature: Vertical Slice)
**Student:** Dave Laurence R. Repe
**Repository:** GymSync-Repe-DaveLaurence-G5

---

## Tech Stack

- **Backend:** Python, Django 6.1
- **Database:** PostgreSQL hosted on Supabase
- **Frontend:** Django templates, Bootstrap 5, Bootstrap Icons
- **Version control:** Git and GitHub (main / develop / feature branches)

---

## Features

### Standard Features (Project Development 1)

- Account registration
- Login and logout
- Role-based user dashboard (Admin, Member; Staff uses the admin dashboard)
- User profile (view and edit details)

### Core Feature: Membership Payment Logging (Project Development 2)

Staff and Admin users record membership payments for gym members. Each payment is linked to a membership plan, and the membership expiry date is calculated automatically from the plan duration. Members can log in and see their own membership status, expiry date, and payment history.

**How the flow works**

1. Staff or Admin opens **Membership Payments** from the dashboard.
2. They click **Record Payment**, choose a member and a plan, and enter the amount, method, and dates.
3. The system validates the form, saves the payment to PostgreSQL, and computes the "valid until" date (`period_start` + plan duration).
4. The member opens **Membership & Payments** on their dashboard and sees an ACTIVE or EXPIRED status, the valid-until date, and their payment history.

**CRUD operations**

| Operation | Who can do it |
|-----------|---------------|
| Create (record a payment) | Admin, Staff |
| Read (list and search all payments) | Admin, Staff |
| Read (own payments and membership status) | Member (own records only) |
| Update (edit a payment) | Admin (any payment), Staff (only payments they recorded) |
| Delete | Admin only |

**Validation and messages**

- Amount must be greater than 0
- Amount cannot be less than the selected plan price
- Payment date cannot be in the future
- Member and plan are required
- Success and error messages are shown after each action

**Access control**

- Only logged-in users can access any payment page
- Members cannot open the payments management pages (403 Forbidden)
- Each payment stores the staff or admin user who recorded it (`recorded_by`)
- Members can only see their own payments

---

## Database Design

**User** (custom model, `accounts.User`): extends `AbstractUser` with `role` (ADMIN, STAFF, MEMBER), `contact_number`, and `profile_photo`.

**MembershipPlan**: `name`, `duration_days`, `price`

**Payment**

| Field | Type | Notes |
|-------|------|-------|
| member | ForeignKey -> User | the member who paid |
| plan | ForeignKey -> MembershipPlan | |
| recorded_by | ForeignKey -> User | staff/admin who recorded it |
| amount | Decimal | greater than 0 |
| method | Choice | cash, gcash, card, bank |
| payment_date | Date | |
| period_start | Date | |
| period_end | Date | computed from plan duration |
| notes | Text | optional |
| created_at | DateTime | auto |

**Relationships:** one User has many Payments (as member), one User has many recorded Payments (as recorded_by), and one MembershipPlan has many Payments.

---

## URL Routes

| URL | Purpose | Access |
|-----|---------|--------|
| `/register/` | Create an account | Public |
| `/login/` | Log in | Public |
| `/dashboard/` | Redirects to the dashboard for the user's role | Logged in |
| `/profile/` | View and edit profile | Logged in |
| `/payments/` | List and search all payments | Admin, Staff |
| `/payments/new/` | Record a payment | Admin, Staff |
| `/payments/<id>/edit/` | Edit a payment | Admin, Staff (own records) |
| `/payments/<id>/delete/` | Delete a payment | Admin |
| `/payments/mine/` | My membership and payment history | Logged in (own data) |

---

## Setup Instructions

### 1. Clone the repository

```
git clone https://github.com/davelaurencerepe/GymSync-Repe-DaveLaurence-G5.git
cd GymSync-Repe-DaveLaurence-G5
```

### 2. Create and activate a virtual environment

```
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Create the `.env` file

Create a file named `.env` in the project root (next to `manage.py`). Do not commit it. It is already listed in `.gitignore`.

```
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=postgres
DB_USER=postgres.your-project-ref
DB_PASSWORD=your-database-password
DB_HOST=your-supabase-pooler-host
DB_PORT=5432
```

Get the database values from your Supabase project: **Connect -> Session pooler**.

### 5. Apply migrations

```
python manage.py migrate
```

### 6. Add the membership plans

```
python manage.py shell
```
```python
from payments.models import MembershipPlan
MembershipPlan.objects.create(name="Monthly", duration_days=30, price=1000)
MembershipPlan.objects.create(name="Quarterly", duration_days=90, price=2700)
MembershipPlan.objects.create(name="Annual", duration_days=365, price=10000)
exit()
```

### 7. Create an admin account

```
python manage.py createsuperuser
```
Then open `/admin/accounts/user/` and set the user's **role** to Admin. Use the same page to set other users' roles to Staff or Member.

### 8. Run the server

```
python manage.py runserver
```
Open http://127.0.0.1:8000/

---

## Branching Strategy

- `main`: stable code only, no direct commits
- `develop`: integration branch created from `main`
- `feature/<feature-name>`: one branch per feature, created from `develop`

Workflow: feature branch -> Pull Request into `develop` -> when the increment is done, Pull Request from `develop` into `main`. Merged feature branches are kept.

Feature branches in this phase:

- `feature/payment-models-views`
- `feature/payment-templates`
- `feature/pd2-docs`

---

## Project Structure

```
GymSync/
├── accounts/            # custom user, auth, dashboards, profile
├── dashboard/
├── payments/            # core feature: models, forms, views, urls, templates
│   └── templates/payments/
├── gymsync_project/     # settings and root URLs
├── templates/accounts/  # login, register, profile, dashboards
├── docs/                # PD2 completion report
├── manage.py
└── requirements.txt
```

---

## Notes

- `.env` is not included in the repository. Create it as shown above.
- The database is hosted on Supabase, so an internet connection is required to run the app.
