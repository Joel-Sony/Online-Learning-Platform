import { Link } from 'react-router-dom';

function PaymentFailed() {
  return (
    <div style={{ textAlign: 'center', padding: '4rem 2rem' }}>
      <h1 style={{ color: 'red' }}>Payment Failed</h1>
      <p style={{ fontSize: '1.2rem', marginBottom: '2rem' }}>
        We couldn't process your payment. Please try again or contact support.
      </p>
      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
        <Link to="/" style={{ background: 'var(--accent)', color: 'white', padding: '0.7rem 1.5rem', borderRadius: '4px', textDecoration: 'none' }}>
          Back to Home
        </Link>
      </div>
    </div>
  );
}

export default PaymentFailed;
