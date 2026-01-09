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