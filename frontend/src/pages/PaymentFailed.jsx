import { Link } from 'react-router-dom';

function PaymentFailed() {
  return (
    <div className="page" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
      <div className="card" style={{ maxWidth: '500px', width: '100%', textAlign: 'center', padding: '40px' }}>
        <div className="empty-state">
          <div className="empty-state-icon" style={{ color: 'var(--error)', background: '#fef2f2' }}>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="15" y1="9" x2="9" y2="15"></line>
              <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>
          </div>
          <h2 className="heading-display" style={{ color: 'var(--text-primary)' }}>Payment Failed</h2>
          <p>
            We couldn't process your payment. Your card has not been charged. Please try again or contact support if the issue persists.
          </p>
          <div style={{ marginTop: '32px', display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <Link to="/courses" className="btn btn-primary btn-lg">Return to Courses</Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PaymentFailed;
