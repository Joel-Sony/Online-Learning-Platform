import { useState } from 'react';

function FlagModal({ isOpen, onClose, onSubmit, title, label }) {
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!reason.trim()) return;
    setSubmitting(true);
    try {
      await onSubmit(reason.trim());
      setReason('');
      onClose();
    } catch {
      // error handled by caller
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <div
        style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)',
          zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}
        onClick={onClose}
      >
        <div
          onClick={e => e.stopPropagation()}
          style={{
            background: '#fff', borderRadius: 'var(--radius-lg)',
            padding: '28px 32px', width: '420px', maxWidth: '90vw',
            boxShadow: '0 20px 60px rgba(0,0,0,0.15)',
          }}
        >
          <h3 style={{ margin: '0 0 4px 0', fontSize: '1.1rem', color: 'var(--text-primary)' }}>
            {title || 'Flag as Inappropriate'}
          </h3>
          <p style={{ margin: '0 0 16px 0', fontSize: '0.85rem', color: 'var(--text-tertiary)' }}>
            {label || 'Please provide a reason for flagging this content.'}
          </p>

          <form onSubmit={handleSubmit}>
            <textarea
              value={reason}
              onChange={e => setReason(e.target.value)}
              placeholder="Why is this content inappropriate?"
              rows={4}
              required
              style={{
                width: '100%', padding: '12px', fontSize: '0.9rem',
                border: '1px solid var(--border-strong)', borderRadius: 'var(--radius-md)',
                resize: 'vertical', fontFamily: 'var(--font-body)',
                boxSizing: 'border-box',
              }}
            />
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' }}>
              <button
                type="button"
                onClick={onClose}
                className="btn btn-secondary"
                style={{ fontSize: '0.85rem' }}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting || !reason.trim()}
                className="btn btn-danger"
                style={{ fontSize: '0.85rem' }}
              >
                {submitting ? 'Submitting…' : 'Submit Flag'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}

export default FlagModal;
