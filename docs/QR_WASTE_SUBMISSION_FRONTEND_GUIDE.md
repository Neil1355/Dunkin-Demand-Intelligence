# QR Code Waste Submission - Frontend Implementation Guide

## Overview
This guide covers the frontend implementation for the anonymous waste submission system via QR code, including employee submission page and manager approval dashboard.

## Architecture

### Flow Diagram
```
Employee Scans QR → /waste/submit?store_id=12345
                    ↓
          Check if PIN required
                    ↓
        Show submission form
                    ↓
          Submit to backend
                    ↓
      Show success confirmation
                    
Manager Dashboard → Pending Submissions Tab
                    ↓
        View pending submissions
                    ↓
        Approve / Edit / Discard
                    ↓
        Data moves to daily_waste
```

---

## 1. Employee Submission Page

### Route: `/waste/submit`
**Public page - NO authentication required**

### URL Parameters
- `store_id` (required): Store ID from QR code

### Page Components

#### A. Initial Load
```tsx
// Pseudo-code structure
useEffect(() => {
  const storeId = searchParams.get('store_id');
  
  // Check if store requires PIN
  fetch(`/api/v1/anonymous-waste/check-pin/${storeId}`)
    .then(res => res.json())
    .then(data => {
      setStoreId(storeId);
      setPinRequired(data.pin_required);
    });
}, []);
```

#### B. Form Fields
```tsx
<form>
  {/* Hidden/Display field */}
  <input 
    type="text" 
    value={storeId} 
    readOnly 
    label="Store ID"
  />

  {/* Conditional PIN field */}
  {pinRequired && (
    <input 
      type="password" 
      maxLength={4}
      pattern="[0-9]{4}"
      label="Store PIN"
      placeholder="Enter 4-digit PIN"
      required
    />
  )}

  {/* Employee name */}
  <input 
    type="text"
    minLength={2}
    label="Your Name"
    placeholder="First and Last Name"
    required
  />

  {/* Donut count */}
  <input 
    type="number"
    min={0}
    label="Donut Count"
    placeholder="0"
  />

  {/* Munchkin count */}
  <input 
    type="number"
    min={0}
    label="Munchkin Count"
    placeholder="0"
  />

  {/* Other count (optional) */}
  <input 
    type="number"
    min={0}
    label="Other Count (Optional)"
    placeholder="0"
  />

  {/* Notes (optional) */}
  <textarea 
    label="Notes (Optional)"
    placeholder="Any additional information..."
    maxLength={500}
  />

  <button type="submit">Submit Waste</button>
</form>
```

#### C. Submission Handler
```typescript
const handleSubmit = async (e: FormEvent) => {
  e.preventDefault();

  const payload = {
    store_id: storeId,
    store_pin: pinRequired ? pin : undefined,
    submitter_name: employeeName,
    donut_count: donutCount,
    munchkin_count: munchkinCount,
    other_count: otherCount,
    notes: notes
  };

  try {
    const response = await fetch('/api/v1/anonymous-waste/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (response.ok) {
      // Show success message
      setSuccessMessage(data.message);
      // Clear form
      resetForm();
    } else {
      // Handle errors
      if (data.pin_required) {
        setError('Invalid or missing PIN');
      } else {
        setError(data.error);
      }
    }
  } catch (error) {
    setError('Network error. Please try again.');
  }
};
```

#### D. Success State
```tsx
{isSuccess && (
  <div className="success-message">
    <CheckCircleIcon />
    <h2>Submission Successful!</h2>
    <p>Your waste submission is pending manager approval.</p>
    <p>Store ID: {storeId}</p>
    <p>Submitted at: {submittedAt}</p>
    <button onClick={resetAndSubmitAgain}>
      Submit Another Entry
    </button>
  </div>
)}
```

### Validation Rules
1. At least one count (donut, munchkin, or other) must be > 0
2. All counts must be non-negative
3. Employee name must be at least 2 characters
4. PIN must be exactly 4 digits (if required)

### Error Handling
| Status Code | Error | Display Message |
|-------------|-------|-----------------|
| 400 | Missing fields | "Please fill all required fields" |
| 401 | Invalid PIN | "Invalid store PIN. Please check and try again." |
| 404 | Invalid store | "Store not found. Please check QR code." |
| 500 | Server error | "Submission failed. Please try again." |

---

## 2. Manager Dashboard - Pending Submissions Tab

### Route: `/dashboard/pending-waste`
**Protected page - Authentication required**

### Page Components

#### A. Badge/Notification
Add a badge on the dashboard sidebar showing pending count:
```tsx
<NavLink to="/dashboard/pending-waste">
  Pending Submissions
  {pendingCount > 0 && (
    <Badge variant="danger">{pendingCount}</Badge>
  )}
</NavLink>
```

Fetch count on dashboard load:
```typescript
useEffect(() => {
  fetch(`/api/v1/pending-waste/counts?store_id=${storeId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
    .then(res => res.json())
    .then(data => setPendingCount(data.pending));
}, [storeId]);
```

#### B. Submissions List
```tsx
<div className="pending-submissions">
  <h1>Pending Waste Submissions</h1>
  
  {/* Filters */}
  <div className="filters">
    <select value={statusFilter} onChange={handleStatusChange}>
      <option value="pending">Pending ({counts.pending})</option>
      <option value="approved">Approved ({counts.approved})</option>
      <option value="edited">Edited ({counts.edited})</option>
      <option value="discarded">Discarded ({counts.discarded})</option>
    </select>
    
    <input 
      type="date" 
      value={dateFilter}
      onChange={handleDateChange}
    />
  </div>

  {/* Submissions table/cards */}
  <div className="submissions-grid">
    {submissions.map(submission => (
      <SubmissionCard 
        key={submission.id}
        submission={submission}
        onApprove={handleApprove}
        onEdit={handleEdit}
        onDiscard={handleDiscard}
      />
    ))}
  </div>
</div>
```

#### C. Submission Card Component
```tsx
interface Submission {
  id: number;
  store_id: number;
  submitter_name: string;
  donut_count: number;
  munchkin_count: number;
  other_count: number;
  notes: string;
  submission_date: string;
  submitted_at: string;
  status: string;
}

const SubmissionCard = ({ submission, onApprove, onEdit, onDiscard }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedCounts, setEditedCounts] = useState({
    donut_count: submission.donut_count,
    munchkin_count: submission.munchkin_count,
    other_count: submission.other_count,
    notes: submission.notes
  });

  return (
    <div className="submission-card">
      <div className="card-header">
        <h3>{submission.submitter_name}</h3>
        <span className="timestamp">
          {formatDateTime(submission.submitted_at)}
        </span>
      </div>

      <div className="card-body">
        {isEditing ? (
          <>
            <input 
              type="number"
              value={editedCounts.donut_count}
              onChange={(e) => setEditedCounts({
                ...editedCounts, 
                donut_count: e.target.value
              })}
              label="Donuts"
            />
            <input 
              type="number"
              value={editedCounts.munchkin_count}
              onChange={(e) => setEditedCounts({
                ...editedCounts,
                munchkin_count: e.target.value
              })}
              label="Munchkins"
            />
            <input 
              type="number"
              value={editedCounts.other_count}
              onChange={(e) => setEditedCounts({
                ...editedCounts,
                other_count: e.target.value
              })}
              label="Other"
            />
            <textarea 
              value={editedCounts.notes}
              onChange={(e) => setEditedCounts({
                ...editedCounts,
                notes: e.target.value
              })}
              label="Notes"
            />
          </>
        ) : (
          <>
            <div className="counts">
              <div className="count-item">
                <span className="label">Donuts:</span>
                <span className="value">{submission.donut_count}</span>
              </div>
              <div className="count-item">
                <span className="label">Munchkins:</span>
                <span className="value">{submission.munchkin_count}</span>
              </div>
              {submission.other_count > 0 && (
                <div className="count-item">
                  <span className="label">Other:</span>
                  <span className="value">{submission.other_count}</span>
                </div>
              )}
            </div>
            
            {submission.notes && (
              <div className="notes">
                <strong>Notes:</strong>
                <p>{submission.notes}</p>
              </div>
            )}
          </>
        )}
      </div>

      <div className="card-actions">
        {submission.status === 'pending' && (
          <>
            {isEditing ? (
              <>
                <button 
                  className="btn-primary"
                  onClick={() => {
                    onEdit(submission.id, editedCounts);
                    setIsEditing(false);
                  }}
                >
                  Save Changes
                </button>
                <button 
                  className="btn-secondary"
                  onClick={() => setIsEditing(false)}
                >
                  Cancel
                </button>
              </>
            ) : (
              <>
                <button 
                  className="btn-success"
                  onClick={() => onApprove(submission.id)}
                >
                  ✓ Approve
                </button>
                <button 
                  className="btn-warning"
                  onClick={() => setIsEditing(true)}
                >
                  ✎ Edit
                </button>
                <button 
                  className="btn-danger"
                  onClick={() => onDiscard(submission.id)}
                >
                  ✕ Discard
                </button>
              </>
            )}
          </>
        )}
        
        {submission.status !== 'pending' && (
          <span className={`status-badge status-${submission.status}`}>
            {submission.status.toUpperCase()}
          </span>
        )}
      </div>
    </div>
  );
};
```

#### D. Action Handlers
```typescript
// Approve as-is
const handleApprove = async (submissionId: number) => {
  try {
    const response = await fetch('/api/v1/pending-waste/approve', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ submission_id: submissionId })
    });

    const data = await response.json();

    if (response.ok) {
      toast.success(data.message);
      refreshSubmissions();
    } else {
      toast.error(data.error);
    }
  } catch (error) {
    toast.error('Failed to approve submission');
  }
};

// Edit and save
const handleEdit = async (submissionId: number, editedCounts: any) => {
  try {
    const response = await fetch('/api/v1/pending-waste/edit-and-save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        submission_id: submissionId,
        ...editedCounts
      })
    });

    const data = await response.json();

    if (response.ok) {
      toast.success(data.message);
      refreshSubmissions();
    } else {
      toast.error(data.error);
    }
  } catch (error) {
    toast.error('Failed to save changes');
  }
};

// Discard
const handleDiscard = async (submissionId: number) => {
  const reason = prompt('Reason for discarding (optional):');
  
  try {
    const response = await fetch('/api/v1/pending-waste/discard', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        submission_id: submissionId,
        reason: reason
      })
    });

    const data = await response.json();

    if (response.ok) {
      toast.success(data.message);
      refreshSubmissions();
    } else {
      toast.error(data.error);
    }
  } catch (error) {
    toast.error('Failed to discard submission');
  }
};

// Refresh list after any action
const refreshSubmissions = () => {
  fetch(`/api/v1/pending-waste/list?store_id=${storeId}&status=${statusFilter}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
    .then(res => res.json())
    .then(data => setSubmissions(data.submissions));
};
```

---

## 3. API Endpoints Summary

### Public Endpoints (No Auth)

#### Check PIN Requirement
```
GET /api/v1/anonymous-waste/check-pin/{store_id}

Response:
{
  "store_id": 12345,
  "pin_required": true
}
```

#### Submit Waste
```
POST /api/v1/anonymous-waste/submit

Body:
{
  "store_id": 12345,
  "store_pin": "1234",
  "submitter_name": "John Doe",
  "donut_count": 24,
  "munchkin_count": 12,
  "other_count": 5,
  "notes": "Extra waste from broken display"
}

Response (201):
{
  "success": true,
  "message": "Submission successful! Pending manager approval.",
  "submission_id": 789,
  "submitted_at": "2026-02-23T14:30:00",
  ...
}
```

### Protected Endpoints (Auth Required)

#### Get Pending Counts
```
GET /api/v1/pending-waste/counts?store_id=12345

Response:
{
  "success": true,
  "store_id": 12345,
  "counts": {
    "pending": 5,
    "approved": 12,
    "edited": 3,
    "discarded": 1
  },
  "pending": 5
}
```

#### List Submissions
```
GET /api/v1/pending-waste/list?store_id=12345&status=pending&date=2026-02-23

Response:
{
  "success": true,
  "store_id": 12345,
  "status": "pending",
  "count": 5,
  "submissions": [...]
}
```

#### Approve Submission
```
POST /api/v1/pending-waste/approve

Body:
{
  "submission_id": 789
}

Response:
{
  "success": true,
  "message": "Submission approved and added to daily waste",
  "submission_id": 789
}
```

#### Edit and Save
```
POST /api/v1/pending-waste/edit-and-save

Body:
{
  "submission_id": 789,
  "donut_count": 25,
  "munchkin_count": 10,
  "other_count": 3,
  "notes": "Adjusted - extra waste found"
}

Response:
{
  "success": true,
  "message": "Submission edited and saved to daily waste",
  ...
}
```

#### Discard Submission
```
POST /api/v1/pending-waste/discard

Body:
{
  "submission_id": 789,
  "reason": "Duplicate entry"
}

Response:
{
  "success": true,
  "message": "Submission discarded",
  "submission_id": 789
}
```

---

## 4. Database Setup

Run these migrations on your Supabase database:

```sql
-- 1. Add store_pin column
\i backend/migrations/0008_add_store_pin.sql

-- 2. Create pending_waste_submissions table
\i backend/migrations/0007_add_pending_waste_submissions.sql
```

Or run them manually through Supabase SQL Editor.

---

## 5. Store PIN Management

### Setting a PIN (Manager Settings Page)

Add a section in the store settings where managers can set/update their store PIN:

```tsx
<div className="store-pin-settings">
  <h3>QR Code Submission PIN</h3>
  <p>Set a 4-digit PIN to secure employee waste submissions via QR code.</p>
  
  <input 
    type="password"
    maxLength={4}
    pattern="[0-9]{4}"
    value={storePin}
    onChange={(e) => setStorePin(e.target.value)}
    placeholder="Enter 4-digit PIN"
  />
  
  <button onClick={updateStorePin}>
    Update PIN
  </button>
  
  <small>
    Leave blank to allow submissions without PIN verification.
    Post this PIN in your back room for employees to use.
  </small>
</div>
```

API endpoint (you may need to add this):
```
POST /api/v1/stores/update-pin

Body:
{
  "store_id": 12345,
  "store_pin": "1234"
}
```

---

## 6. Styling Recommendations

### Mobile-First Design
The employee submission page will be accessed primarily on mobile phones after scanning QR codes. Design considerations:

- Large tap targets (min 44x44px)
- Clear, readable text (min 16px font size)
- Simple, linear form layout
- Prominent submit button
- Clear success/error states
- Minimal navigation (focused task)

### Color Coding
- **Pending**: Yellow/Amber badge
- **Approved**: Green badge
- **Edited**: Blue badge
- **Discarded**: Red badge

---

## 7. Testing Checklist

### Employee Submission
- [ ] QR code redirects to correct URL with store_id
- [ ] PIN field shows only if required
- [ ] Form validation works (names, counts, PIN format)
- [ ] Success message displays after submission
- [ ] Error messages are clear and helpful
- [ ] Works on mobile devices (different screen sizes)
- [ ] Network error handling

### Manager Dashboard
- [ ] Badge shows correct pending count
- [ ] List loads and displays submissions
- [ ] Filters work (status, date)
- [ ] Approve action works and updates list
- [ ] Edit mode allows changing values
- [ ] Save changes works and updates list
- [ ] Discard action works and updates list
- [ ] Status badges display correctly
- [ ] Refreshing maintains filter state

---

## 8. Future Enhancements

1. **Real-time Updates**: Use WebSocket/polling to refresh pending count automatically
2. **Bulk Actions**: Select multiple submissions and approve/discard at once
3. **Export**: Download submission history as CSV/Excel
4. **Analytics**: Track submission patterns by employee
5. **Photos**: Allow employees to upload photos of waste
6. **Push Notifications**: Notify managers when new submissions arrive
7. **Submission History**: Show employee their past submissions

---

## Support

For backend API questions, see:
- `backend/routes/anonymous_waste_submission.py`
- `backend/routes/pending_waste_management.py`
- `backend/migrations/0007_add_pending_waste_submissions.sql`
- `backend/migrations/0008_add_store_pin.sql`
