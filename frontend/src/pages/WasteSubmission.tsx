import React, { useState, useEffect } from 'react';

interface WasteSubmissionProps {
  storeId: string;
  onBack: () => void;
}

interface Product {
  product_id: number;
  product_name: string;
  product_type: string;
  is_active: boolean;
}

interface ProductQuantities {
  [key: number]: string; // product_id -> quantity string
}

export function WasteSubmission({ storeId, onBack }: WasteSubmissionProps) {
  const [pinRequired, setPinRequired] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  // Products data
  const [products, setProducts] = useState<Product[]>([]);
  const [quantities, setQuantities] = useState<ProductQuantities>({});

  // Form fields
  const [submitterName, setSubmitterName] = useState('');
  const [storePin, setStorePin] = useState('');
  const [notes, setNotes] = useState('');

  const API_BASE = import.meta.env.VITE_API_URL || "https://dunkin-demand-intelligence.onrender.com/api/v1";

  // Load data on mount
  useEffect(() => {
    loadInitialData();
  }, [storeId]);

  const loadInitialData = async () => {
    try {
      // Check PIN requirement
      const pinResponse = await fetch(`${API_BASE}/anonymous-waste/check-pin/${storeId}`);
      const pinData = await pinResponse.json();
      
      if (!pinResponse.ok) {
        setError('Invalid store ID');
        setLoading(false);
        return;
      }
      
      setPinRequired(pinData.pin_required);

      // Fetch products list
      const productsResponse = await fetch(`${API_BASE}/anonymous-waste/products`);
      const productsData = await productsResponse.json();
      
      if (productsResponse.ok) {
        setProducts(productsData);
        
        // Initialize quantities to 0
        const initialQuantities: ProductQuantities = {};
        productsData.forEach((p: Product) => {
          initialQuantities[p.product_id] = '';
        });
        setQuantities(initialQuantities);
      } else {
        setError('Failed to load products');
      }
    } catch (err) {
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  const loadInitialData = async () => {
    try {
      // Check PIN requirement
      const pinResponse = await fetch(`${API_BASE}/anonymous-waste/check-pin/${storeId}`);
      const pinData = await pinResponse.json();
      
      if (!pinResponse.ok) {
        setError('Invalid store ID');
        setLoading(false);
        return;
      }
      
      setPinRequired(pinData.pin_required);

      // Fetch products list
      const productsResponse = await fetch(`${API_BASE}/anonymous-waste/products`);
      const productsData = await productsResponse.json();
      
      if (productsResponse.ok) {
        setProducts(productsData);
        
        // Initialize quantities to 0
        const initialQuantities: ProductQuantities = {};
        productsData.forEach((p: Product) => {
          initialQuantities[p.product_id] = '';
        });
        setQuantities(initialQuantities);
      } else {
        setError('Failed to load products');
      }
    } catch (err) {
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = (productId: number, value: string) => {
    setQuantities(prev => ({
      ...prev,
      [productId]: value
    }));
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

    // Build product items array (only non-zero quantities)
    const productItems = products
      .map(p => ({
        product_id: p.product_id,
        product_name: p.product_name,
        waste_quantity: parseInt(quantities[p.product_id]) || 0
      }))
      .filter(item => item.waste_quantity > 0);

    if (productItems.length === 0) {
      setError('Please enter at least one waste quantity');
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
      product_items: productItems,
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
        const resetQuantities: ProductQuantities = {};
        products.forEach(p => {
          resetQuantities[p.product_id] = '';
        });
        setQuantities(resetQuantities);
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

          {/* Products by Category */}
          <div style={{ marginBottom: '25px' }}>
            <label style={{ 
              display: 'block',
              color: '#333',
              fontWeight: '600',
              marginBottom: '12px',
              fontSize: '1rem'
            }}>
              Waste Quantities by Product *
            </label>
            
            {/* Group products by type */}
            {['donut', 'munchkin', 'bagel', 'muffin', 'bakery', 'other'].map(type => {
              const typeProducts = products.filter(p => p.product_type === type);
              if (typeProducts.length === 0) return null;
              
              const typeLabel = type.charAt(0).toUpperCase() + type.slice(1) + 's';
              const typeColor = type === 'donut' ? '#FF671F' : type === 'munchkin' ? '#DA1884' : '#8B7355';
              
              return (
                <div key={type} style={{ marginBottom: '20px' }}>
                  <div style={{ 
                    fontSize: '0.9rem',
                    fontWeight: '600',
                    color: typeColor,
                    marginBottom: '8px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px'
                  }}>
                    {typeLabel}
                  </div>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr',
                    gap: '8px'
                  }}>
                    {typeProducts.map(product => (
                      <div key={product.product_id} style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '10px 12px',
                        background: '#FFF8F0',
                        borderRadius: '8px',
                        border: '1px solid #FFE8D6'
                      }}>
                        <span style={{
                          color: '#333',
                          fontSize: '0.9rem',
                          flex: 1
                        }}>
                          {product.product_name}
                        </span>
                        <input
                          type="number"
                          value={quantities[product.product_id]}
                          onChange={(e) => updateQuantity(product.product_id, e.target.value)}
                          placeholder="0"
                          min="0"
                          style={{
                            width: '70px',
                            padding: '6px 8px',
                            fontSize: '0.95rem',
                            border: '2px solid #ddd',
                            borderRadius: '6px',
                            textAlign: 'center',
                            boxSizing: 'border-box'
                          }}
                          onFocus={(e) => e.target.style.borderColor = typeColor}
                          onBlur={(e) => e.target.style.borderColor = '#ddd'}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
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
