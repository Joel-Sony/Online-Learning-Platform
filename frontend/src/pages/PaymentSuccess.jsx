import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import api from '../api';

function PaymentSuccess() {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const paymentId = searchParams.get('payment_id') || searchParams.get('paymentId');
  const payerId = searchParams.get('PayerID');

  const [statusText, setStatusText] = useState('Verifying your enrollment details...');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (sessionId) {
      verifyStripe();
    } else if (paymentId && payerId) {
      capturePayPal();
    } else {
      setLoading(false);
      setStatusText('Payment received successfully. Your enrollment is being processed.');
    }
  }, [sessionId, paymentId, payerId]);

  const verifyStripe = async () => {
    try {
      const res = await api.post('/enrollments/verify_stripe_session/', {
        session_id: sessionId,
      });
      setStatusText(
        res.data.already_enrolled
          ? `You were already enrolled in "${res.data.course_title}".`
          : `Congratulations! You are now enrolled in "${res.data.course_title}".`
      );
      setLoading(false);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to verify payment with our servers.');
      setLoading(false);
    }
  };

  const capturePayPal = async () => {
    try {
      await api.post('/enrollments/capture_paypal_payment/', {
        payment_id: paymentId,
        payer_id: payerId,
      });
      setStatusText('Payment successful! You are now fully enrolled.');
      setLoading(false);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to capture PayPal payment.');
      setLoading(false);
    }
  };

  return (
    <div className="page" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
      <div className="card" style={{ maxWidth: '500px', width: '100%', textAlign: 'center', padding: '40px' }}>
        
        {loading ? (
          <div className="loading-state">
            <div className="spinner" style={{ marginBottom: '16px', width: '40px', height: '40px' }}></div>
            <h2 className="heading-display">Processing Payment</h2>
            <p>{statusText}</p>
          </div>
        ) : error ? (
          <div className="empty-state">
            <div className="empty-state-icon" style={{ color: 'var(--error)', background: '#fef2f2' }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
            </div>
            <h2 className="heading-display" style={{ color: 'var(--error)' }}>Verification Failed</h2>
            <p>{error}</p>
            <div style={{ marginTop: '24px', display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <Link to="/courses" className="btn btn-secondary">Browse Courses</Link>
              <Link to="/learning" className="btn btn-primary">My Dashboard</Link>
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon" style={{ color: 'var(--success)', background: '#f0fdf4' }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            </div>
            <h2 className="heading-display">Payment Successful!</h2>
            <p>{statusText}</p>
            <div style={{ marginTop: '32px', display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
              <Link to="/learning" className="btn btn-primary btn-lg">Start Learning Now</Link>
              <Link to="/courses" className="btn btn-secondary btn-lg">Browse More Courses</Link>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default PaymentSuccess;
