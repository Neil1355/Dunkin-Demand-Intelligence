import React, { useState, useEffect } from 'react';

interface WasteSubmissionProps {
  storeId: string;
  onBack: () => void;
}

export function WasteSubmission({ storeId, onBack }: WasteSubmissionProps) {
  const [pinRequired, setPinRequired] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  // Form fields
  const [submitterName, setSubmitterName] = useState('');
  const [storePin, setStorePin] = useState('');
  const [donutCount, setDonutCount] = useState('');
  const [munchkinCount, setMunchkinCount] = useState('');
  const [otherCount, setOtherCount] = useState('');
  const [notes, setNotes] = useState('');

  const API_BASE = import.meta.env.VITE_API_URL || "https://dunkin-demand-intelligence.onrender.com/api/v1";

  // Check if PIN is required on load
  useEffect(() => {
    checkPinRequirement();
  }, [storeId]);

  const checkPinRequirement = async () => {
    try {
      const response = await fetch(`${API_BASE}/anonymous-waste/check-pin/${storeId}`);
      const data = await response.json();
      
      if (response.ok) {
        setPinRequired(data.pin_required);
      } else {
        setError('Invalid store ID');
      }
    } catch (err) {
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    // Validation
    if (submitterName.trim().length < 2) {
      setError('Name must be at least 2 characters');
      setSubmitting(false);
      return;
    }

    const donut = parseInt(donutCount) || 0;
    const munchkin = parseInt(munchkinCount) || 0;
    const other = parseInt(otherCount) || 0;

    if (donut === 0 && munchkin === 0 && other === 0) {
      setError('Please enter at least one count');
      setSubmitting(false);
      return;
    }

    if (pinRequired && storePin.length !== 4) {
      setError('PIN must be 4 digits');
      setSubmitting(false);
      return;
    }

    const payload = {
      store_id: parseInt(storeId),
      store_pin: pinRequired ? storePin : undefined,
      submitter_name: submitterName.trim(),
      donut_count: donut,
      munchkin_count: munchkin,
      other_count: other,
      notes: notes.trim()
    };

    try {
      const response = await fetch(`${API_BASE}/anonymous-waste/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(true);
        // Reset form
        setSubmitterName('');
        setStorePin('');
        setDonutCount('');
        setMunchkinCount('');
        setOtherCount('');
        setNotes('');
      } else {
        setError(data.error || 'Submission failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmitAnother = () => {
    setSuccess(false);
    setError('');
  };

  if (loading) {
    return (
      <div style={{ 
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #FF6B35 0%, #F7931E 100%)',
        fontFamily: 'sans-serif'
      }}>
        <div style={{ textAlign: 'center', color: 'white' }}>
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🍩</div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div style={{ 
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #FF6B35 0%, #F7931E 100%)',
        padding: '20px',
        fontFamily: 'sans-serif'
      }}>
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '40px',
          maxWidth: '500px',
          width: '100%',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '4rem', marginBottom: '20px' }}>✅</div>
          <h2 style={{ 
            color: '#2D5016',
            fontSize: '1.8rem',
            marginBottom: '15px',
            fontWeight: 'bold'
          }}>
            Submission Successful!
          </h2>
          <p style={{ 
            color: '#666',
            fontSize: '1.1rem',
            marginBottom: '10px',
            lineHeight: '1.6'
          }}>
            Your waste submission is pending manager approval.
          </p>
          <p style={{ 
            color: '#999',
            fontSize: '0.9rem',
            marginBottom: '30px'
          }}>
            Store ID: {storeId}
          </p>
          <button
            onClick={handleSubmitAnother}
            style={{
              background: 'linear-gradient(135deg, #FF6B35 0%, #F7931E 100%)',
              color: 'white',
              border: 'none',
              padding: '15px 40px',
              fontSize: '1.1rem',
              borderRadius: '12px',
              cursor: 'pointer',
              fontWeight: 'bold',
              boxShadow: '0 4px 15px rgba(255,107,53,0.4)',
              marginRight: '10px'
            }}
          >
            Submit Another
          </button>
          <button
            onClick={onBack}
            style={{
              background: 'transparent',
              color: '#666',
              border: '2px solid #ddd',
              padding: '15px 40px',
              fontSize: '1.1rem',
              borderRadius: '12px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #FF6B35 0%, #F7931E 100%)',
      padding: '20px',
      fontFamily: 'sans-serif'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '20px',
        padding: '40px',
        maxWidth: '500px',
        width: '100%',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <div style={{ fontSize: '3rem', marginBottom: '15px' }}>🍩</div>
          <h1 style={{ 
            color: '#2D5016',
            fontSize: '1.8rem',
            marginBottom: '10px',
            fontWeight: 'bold'
          }}>
            Submit Waste Count
          </h1>
          <p style={{ color: '#666', fontSize: '0.95rem' }}>
            Store #{storeId}
          </p>
        </div>

        {error && (
          <div style={{
            background: '#FEE',
            border: '1px solid #F88',
            color: '#C33',
            padding: '12px',
            borderRadius: '8px',
            marginBottom: '20px',
            fontSize: '0.9rem'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Employee Name */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ 
              display: 'block',
              color: '#333',
              fontWeight: '600',
              marginBottom: '8px',
              fontSize: '0.95rem'
            }}>
              Your Name *
            </label>
            <input
              type="text"
              value={submitterName}
              onChange={(e) => setSubmitterName(e.target.value)}
              placeholder="First and Last Name"
              required
              minLength={2}
              style={{
                width: '100%',
                padding: '12px',
                fontSize: '1rem',
                border: '2px solid #ddd',
                borderRadius: '8px',
                boxSizing: 'border-box',
                transition: 'border-color 0.3s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#FF6B35'}
              onBlur={(e) => e.target.style.borderColor = '#ddd'}
            />
          </div>

          {/* PIN (conditional) */}
          {pinRequired && (
            <div style={{ marginBottom: '20px' }}>
              <label style={{ 
                display: 'block',
                color: '#333',
                fontWeight: '600',
                marginBottom: '8px',
                fontSize: '0.95rem'
              }}>
                Store PIN *
              </label>
              <input
                type="password"
                value={storePin}
                onChange={(e) => setStorePin(e.target.value.replace(/\D/g, '').slice(0, 4))}
                placeholder="4-digit PIN"
                required
                maxLength={4}
                pattern="[0-9]{4}"
                style={{
                  width: '100%',
                  padding: '12px',
                  fontSize: '1.2rem',
                  border: '2px solid #ddd',
                  borderRadius: '8px',
                  boxSizing: 'border-box',
                  letterSpacing: '8px',
                  textAlign: 'center'
                }}
                onFocus={(e) => e.target.style.borderColor = '#FF6B35'}
                onBlur={(e) => e.target.style.borderColor = '#ddd'}
              />
              <small style={{ color: '#666', fontSize: '0.85rem' }}>
                Enter the 4-digit PIN posted in the back room
              </small>
            </div>
          )}

          {/* Donut Count */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ 
              display: 'block',
              color: '#333',
              fontWeight: '600',
              marginBottom: '8px',
              fontSize: '0.95rem'
            }}>
              Donut Count
            </label>
            <input
              type="number"
              value={donutCount}
              onChange={(e) => setDonutCount(e.target.value)}
              placeholder="0"
              min="0"
              style={{
                width: '100%',
                padding: '12px',
                fontSize: '1rem',
                border: '2px solid #ddd',
                borderRadius: '8px',
                boxSizing: 'border-box'
              }}
              onFocus={(e) => e.target.style.borderColor = '#FF6B35'}
              onBlur={(e) => e.target.style.borderColor = '#ddd'}
            />
          </div>

          {/* Munchkin Count */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ 
              display: 'block',
              color: '#333',
              fontWeight: '600',
              marginBottom: '8px',
              fontSize: '0.95rem'
            }}>
              Munchkin Count
            </label>
            <input
              type="number"
              value={munchkinCount}
              onChange={(e) => setMunchkinCount(e.target.value)}
              placeholder="0"
              min="0"
              style={{
                width: '100%',
                padding: '12px',
                fontSize: '1rem',
                border: '2px solid #ddd',
                borderRadius: '8px',
                boxSizing: 'border-box'
              }}
              onFocus={(e) => e.target.style.borderColor = '#FF6B35'}
              onBlur={(e) => e.target.style.borderColor = '#ddd'}
            />
          </div>

          {/* Other Count */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ 
              display: 'block',
              color: '#333',
              fontWeight: '600',
              marginBottom: '8px',
              fontSize: '0.95rem'
            }}>
              Other Count (Optional)
            </label>
            <input
              type="number"
              value={otherCount}
              onChange={(e) => setOtherCount(e.target.value)}
              placeholder="0"
              min="0"
              style={{
                width: '100%',
                padding: '12px',
                fontSize: '1rem',
                border: '2px solid #ddd',
                borderRadius: '8px',
                boxSizing: 'border-box'
              }}
              onFocus={(e) => e.target.style.borderColor = '#FF6B35'}
              onBlur={(e) => e.target.style.borderColor = '#ddd'}
            />
          </div>

          {/* Notes */}
          <div style={{ marginBottom: '25px' }}>
            <label style={{ 
              display: 'block',
              color: '#333',
              fontWeight: '600',
              marginBottom: '8px',
              fontSize: '0.95rem'
            }}>
              Notes (Optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Any additional information..."
              maxLength={500}
              rows={3}
              style={{
                width: '100%',
                padding: '12px',
                fontSize: '1rem',
                border: '2px solid #ddd',
                borderRadius: '8px',
                boxSizing: 'border-box',
                fontFamily: 'inherit',
                resize: 'vertical'
              }}
              onFocus={(e) => e.target.style.borderColor = '#FF6B35'}
              onBlur={(e) => e.target.style.borderColor = '#ddd'}
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={submitting}
            style={{
              width: '100%',
              background: submitting 
                ? '#ccc' 
                : 'linear-gradient(135deg, #FF6B35 0%, #F7931E 100%)',
              color: 'white',
              border: 'none',
              padding: '16px',
              fontSize: '1.2rem',
              borderRadius: '12px',
              cursor: submitting ? 'not-allowed' : 'pointer',
              fontWeight: 'bold',
              boxShadow: submitting ? 'none' : '0 4px 15px rgba(255,107,53,0.4)',
              transition: 'all 0.3s',
              marginBottom: '15px'
            }}
          >
            {submitting ? 'Submitting...' : 'Submit Waste'}
          </button>

          <button
            type="button"
            onClick={onBack}
            style={{
              width: '100%',
              background: 'transparent',
              color: '#666',
              border: '2px solid #ddd',
              padding: '12px',
              fontSize: '1rem',
              borderRadius: '12px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            Cancel
          </button>
        </form>
      </div>
    </div>
  );
}
