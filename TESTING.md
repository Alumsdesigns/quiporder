# Testing

## Table of Contents
- [HTML Validation](#html-validation)
- [CSS Validation](#css-validation)
- [JavaScript Testing](#javascript-testing)
- [Python Testing](#python-testing)
- [Lighthouse](#lighthouse)
- [Manual Testing](#manual-testing)
- [User Story Testing](#user-story-testing)
- [Browser Compatibility](#browser-compatibility)
- [Bugs](#bugs)

---

## HTML Validation

HTML was validated using the [W3C Markup Validator](https://validator.w3.org/) by copying page source.

| Page | Result | Screenshot |
|------|--------|------------|
| Home | Pass | [View](docs/testing/html-home.png) |
| Login | Pass | [View](docs/testing/html-login.png) |
| Therapist Dashboard | Pass | [View](docs/testing/html-dashboard.png) |
| Patient Dashboard | Pass | [View](docs/testing/html-patient.png) |
| Order Form | Pass | [View](docs/testing/html-order.png) |
| Equipment List | Pass | [View](docs/testing/html-equipment.png) |
| 403 Error | Pass | [View](docs/testing/html-403.png) |
| 404 Error | Pass | [View](docs/testing/html-404.png) |
| 500 Error | Pass | [View](docs/testing/html-500.png) |

---

## CSS Validation

CSS was validated using the [W3C CSS Validator (Jigsaw)](https://jigsaw.w3.org/css-validator/).

| File | Result | Notes |
|------|--------|-------|
| style.css | Pass | No errors |
| dashboard.css | Pass | No errors |
| forms.css | Pass | No errors |
| errors.css | Pass | No errors |
| home.css | Pass | No errors |

---

## JavaScript Testing

JavaScript was validated using [JSHint](https://jshint.com/).

| File | Result | Notes |
|------|--------|-------|
| validation.js | Pass | No major issues |

### JavaScript Functionality Tested:
- Form validation feedback on blur
- Real-time error clearing on input
- Delete confirmation dialogs
- Quantity input validation
- Back button functionality (history.back())

---

## Python Testing

Python code was validated for PEP8 compliance using `pycodestyle`.
```bash
pycodestyle --max-line-length=100 equipment/ users/ quiporder/
```

| App | Result |
|-----|--------|
| equipment | Pass |
| users | Pass |
| quiporder | Pass |

---

## Lighthouse

Lighthouse testing was performed in Chrome DevTools (Incognito mode).

| Page | Performance | Accessibility | Best Practices | SEO |
|------|-------------|---------------|----------------|-----|
| Home | 95 | 100 | 100 | 100 |
| Login | 98 | 100 | 100 | 100 |
| Dashboard | 92 | 98 | 100 | 100 |
| Order Form | 94 | 100 | 100 | 100 |

---

## Manual Testing

### Authentication Testing

| Test | Steps | Expected | Result |
|------|-------|----------|--------|
| Login valid | Enter valid credentials, submit | Redirect to dashboard | Pass |
| Login invalid | Enter wrong password | Error message displayed | Pass |
| Logout | Click logout button | Redirect to home, logged out | Pass |
| Access protected page | Visit /equipment/dashboard/ without login | Redirect to login | Pass |

### CRUD Testing - Equipment Orders

| Test | Steps | Expected | Result |
|------|-------|----------|--------|
| Create order | Fill form, submit | Order created, success message | Pass |
| Read orders | View dashboard | Orders displayed in table | Pass |
| Update order | Click edit, modify, save | Order updated, success message | Pass |
| Delete order | Click delete, confirm | Order soft-deleted | Pass |

### Role-Based Access

| Test | User Type | Action | Expected | Result |
|------|-----------|--------|----------|--------|
| Dashboard access | Therapist | Visit /equipment/dashboard/ | Access granted | Pass |
| Dashboard access | Patient | Visit /equipment/dashboard/ | Access denied (403) | Pass |
| Create order | Therapist | Submit order form | Order created | Pass |
| Create order | Patient | Attempt to access | Access denied | Pass |
| Admin access | Staff user | Visit /admin/ | Access granted | Pass |
| Admin access | Non-staff | Visit /admin/ | Login required | Pass |

### Form Validation

| Test | Input | Expected | Result |
|------|-------|----------|--------|
| Empty required field | Leave patient blank | Error shown | Pass |
| Quantity < 1 | Enter 0 | Error shown | Pass |
| Valid submission | All fields valid | Form submits | Pass |

---

## User Story Testing

User stories were tested during manual testing. Each user story is matched to its corresponding test case(s).

| User Story | Description | Test Case | Result |
|------------|-------------|-----------|--------|
| **US1** | Admin can create user accounts | TC-AUTH-01 |  Pass |
| **US2** | Therapist can log in | TC-AUTH-02 | Pass |
| **US3** | Patient can log in | TC-AUTH-03 | Pass |
| **US4** | Admin can assign user roles | TC-AUTH-04 | Pass |
| **US5** | Non-authenticated users blocked | TC-AUTH-05 | Pass |
| **US6** | Therapist dashboard displays statistics | TC-DASH-01 | Pass |
| **US7** | Therapist can create orders | TC-ORDER-01 | Pass |
| **US8** | Therapist can edit orders (3 weeks) | TC-ORDER-02 | Pass |
| **US9** | Therapist can delete orders (3 weeks) | TC-ORDER-03 | Pass |
| **US10** | Recent orders displayed | TC-DASH-02 | Pass |
| **US11** | Status badges display correctly | TC-DASH-03 |  Pass |
| **US12** | Staff can access admin panel | TC-ADMIN-01 | Pass |
| **US13** | Patient can view their orders | TC-PAT-01 |  Pass |
| **US14** | Patient cannot edit/delete orders | TC-PAT-02 | Pass |
| **US15** | Patient sees order status | TC-PAT-03 |  Pass |
| **US16** | Therapist can view equipment | TC-EQUIP-01 |  Pass |
| **US17** | Equipment quantities visible | TC-EQUIP-02 |  Pass |
| **US18** | Admin can add equipment | TC-ADMIN-02 | Pass |
| **US19** | Admin can edit equipment | TC-ADMIN-03 | Pass |
| **US20** | Admin can manage inventory | TC-ADMIN-04 | Pass |
| **US21** | Admin can create patient profiles | TC-ADMIN-05 | Pass |
| **US22** | Admin can assign patients to therapists | TC-ADMIN-06 | Pass |
| **US23** | Admin can set patient status | TC-ADMIN-07 | Pass |
| **US24** | Patient accounts cannot get staff privileges | TC-SEC-01 | Pass |
| **US25** | Custom error pages display | TC-ERR-01 | Pass |
| **US26** | Soft delete preserves audit trail | TC-ORDER-04 | Pass |
| **US27** | Keyboard navigation works | TC-A11Y-01 | Pass |
| **US28** | Responsive design on mobile | TC-A11Y-02 | Pass |
| **US29** | Feedback messages display | TC-UX-01 | Pass |

### Test Case Details

#### TC-AUTH-01: Admin Account Creation
**Steps:**
1. Log in to admin panel
2. Navigate to Users > Add User
3. Fill in required fields
4. Select user type (Therapist/Patient)
5. Save

**Expected:** User created with correct role  
**Actual:** Pass

#### TC-ORDER-01: Create Equipment Order
**Steps:**
1. Log in as therapist
2. Navigate to Create Order
3. Select patient, equipment, quantity
4. Submit form

**Expected:** Order created, success message displayed, redirected to dashboard  
**Actual:** Pass

#### TC-ORDER-02: Edit Order Within 3 Weeks
**Steps:**
1. Log in as therapist who created order
2. Click Edit on recent order (< 3 weeks old)
3. Modify details
4. Submit

**Expected:** Order updated, success message displayed  
**Actual:** Pass

#### TC-ORDER-03: Delete Order Within 3 Weeks
**Steps:**
1. Log in as therapist who created order
2. Click Delete on recent order (< 3 weeks old)
3. Confirm deletion

**Expected:** Order soft deleted, removed from dashboard  
**Actual:** Pass

#### TC-SEC-01: Patient Privilege Escalation Prevention
**Steps:**
1. Log in to admin panel
2. Edit patient user
3. Attempt to check "Staff status"
4. Save

**Expected:** Staff status automatically unchecked, warning message displayed  
**Actual:** Pass

#### TC-ERR-01: Custom Error Pages
**Steps:**
1. Visit non-existent URL (404)
2. Access restricted resource (403)
3. Trigger server error (500)

**Expected:** Custom branded error pages display with navigation options  
**Actual:** Pass



## Browser Compatibility

| Browser | Version | Result |
|---------|---------|--------|
| Chrome | 120+ | Pass |
| Firefox | 120+ | Pass |
| Safari | 17+ | Pass |
| Edge | 120+ | Pass |

---

## Responsive Testing

| Device | Screen Size | Result |
|--------|-------------|--------|
| iPhone SE | 375x667 | Pass |
| iPhone 12 | 390x844 | Pass |
| iPad | 768x1024 | Pass |
| Desktop | 1920x1080 | Pass |

---

## Bugs

### Fixed Bugs

| Bug | Description | Fix |
|-----|-------------|-----|
| CSRF error on login | Token mismatch after cache | Added CSRF_TRUSTED_ORIGINS |
| CSS not updating | Browser cache | Clear staticfiles + hard refresh |
| Empty redirect | `redirect('')` in order_create | Changed to `redirect('therapist_dashboard')` |
| Edit buttons missing | 24-hour window expired | Extended to 3 weeks |

### Known Bugs

No known bugs at time of submission.