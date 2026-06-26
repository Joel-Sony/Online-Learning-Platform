import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import api from '../api';

function PaymentSuccess() {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const paymentId = searchParams.get('payment_id') || searchParams.get('paymentId');
  const payerId = searchParams.get('PayerID');

  const [statusText, setStatusText] = useState('Processing your enrollment...');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (sessionId) {
      // Stripe flow: verify session and create enrollment immediately
      verifyStripe();
    } else if (paymentId && payerId) {
      // PayPal flow: capture payment and create enrollment
      capturePayPal();
    } else {
      setLoading(false);
      setStatusText('Payment received. Your enrollment is being processed.');
    }
  }, [sessionId, paymentId, payerId]);

  const verifyStripe = async () => {
    try {
      const res = await api.post('/enrollments/verify_stripe_session/', {
        session_id: sessionId,
      });
      setStatusText(
        res.data.already_enrolled
          ? `You are already enrolled in "${res.data.course_title}".`
          : `You are now enrolled in "${res.data.course_title}"!`
      );
      setLoading(false);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to verify Stripe payment.');
      setLoading(false);
    }
  };

  const capturePayPal = async () => {
    try {
      await api.post('/enrollments/capture_paypal_payment/', {
        payment_id: paymentId,
        payer_id: payerId,
      });
      setStatusText('Payment successful! You are now enrolled.');
      setLoading(false);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to capture PayPal payment.');
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: 'center', padding: '4rem 2rem' }}>
      {error ? (
        <>
          <h1 style={{ color: 'red' }}>Payment Verification Failed</h1>
          <p style={{ fontSize: '1.2rem', marginBottom: '2rem' }}>{error}</p>
        </>
      ) : (
        <>
          <h1 style={{ color: loading ? '#555' : 'green' }}>
            {loading ? 'Verifying Payment...' : 'Payment Successful! 🎉'}
          </h1>
          <p style={{ fontSize: '1.2rem', marginBottom: '2rem' }}>{statusText}</p>
        </>
      )}

      {!loading && (
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          <Link
            to="/learning"
            style={{
              background: 'var(--accent)',
              color: 'white',
              padding: '0.7rem 1.5rem',
              borderRadius: '4px',
              textDecoration: 'none',
              fontWeight: 'bold',
            }}
          >
            Go to My Courses →
          </Link>
          <Link to="/" style={{ color: 'var(--text)', padding: '0.7rem 1.5rem', textDecoration: 'none' }}>
            Browse More
          </Link>
        </div>
      )}
    </div>
  );
}

export default PaymentSuccess;
