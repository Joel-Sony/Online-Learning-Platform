import { useState, useRef, useCallback } from 'react';

const TOOLBAR_ITEMS = [
  { cmd: 'bold', icon: 'B', title: 'Bold' },
  { cmd: 'italic', icon: 'I', title: 'Italic', style: { fontStyle: 'italic' } },
  { cmd: 'underline', icon: 'U', title: 'Underline', style: { textDecoration: 'underline' } },
  { type: 'divider' },
  { cmd: 'formatBlock', value: 'h3', icon: 'H', title: 'Heading' },
  { cmd: 'formatBlock', value: 'p', icon: '¶', title: 'Paragraph' },
  { type: 'divider' },
  { cmd: 'insertUnorderedList', icon: '•', title: 'Bullet List' },
  { cmd: 'insertOrderedList', icon: '1.', title: 'Numbered List' },
  { type: 'divider' },
  { cmd: 'removeFormat', icon: '↺', title: 'Clear Formatting' },
];

function RichTextEditor({ value, onChange, placeholder, minHeight = '200px' }) {
  const editorRef = useRef(null);
  const [isFocused, setIsFocused] = useState(false);

  const exec = useCallback((cmd, value = null) => {
    document.execCommand(cmd, false, value);
    if (editorRef.current) {
      onChange(editorRef.current.innerHTML);
    }
    editorRef.current?.focus();
  }, [onChange]);

  const handleInput = () => {
    if (editorRef.current) {
      onChange(editorRef.current.innerHTML);
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const text = e.clipboardData.getData('text/plain');
    document.execCommand('insertText', false, text);
  };

  return (
    <div style={{
      border: `1.5px solid ${isFocused ? 'var(--accent)' : 'var(--border)'}`,
      borderRadius: 'var(--radius-md)',
      overflow: 'hidden',
      transition: 'border-color 0.15s',
      background: 'var(--bg)',
    }}>
      <div style={{
        display: 'flex', flexWrap: 'wrap', gap: '2px',
        padding: '6px 8px',
        borderBottom: '1px solid var(--border)',
        background: 'var(--surface)',
      }}>
        {TOOLBAR_ITEMS.map((item, i) => {
          if (item.type === 'divider') {
            return <div key={i} style={{ width: '1px', height: '20px', background: 'var(--border)', margin: '0 4px', alignSelf: 'center' }} />;
          }
          return (
            <button
              key={i}
              type="button"
              title={item.title}
              onMouseDown={(e) => { e.preventDefault(); exec(item.cmd, item.value); }}
              style={{
                width: '30px', height: '28px',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                border: 'none', borderRadius: '4px',
                background: 'transparent',
                color: 'var(--text-secondary)',
                cursor: 'pointer',
                fontSize: '0.8rem',
                fontWeight: item.cmd === 'bold' ? 700 : 400,
                fontStyle: item.style?.fontStyle || 'normal',
                textDecoration: item.style?.textDecoration || 'none',
                transition: 'all 0.1s',
              }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-subtle)'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
              {item.icon}
            </button>
          );
        })}
      </div>
      <div
        ref={editorRef}
        contentEditable
        suppressContentEditableWarning
        onInput={handleInput}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        onPaste={handlePaste}
        data-placeholder={placeholder}
        style={{
          minHeight,
          padding: '12px 14px',
          fontSize: '0.9rem',
          lineHeight: '1.7',
          color: 'var(--text-primary)',
          outline: 'none',
          overflowY: 'auto',
          cursor: 'text',
        }}
        dangerouslySetInnerHTML={{ __html: value }}
      />
    </div>
  );
}

export default RichTextEditor;
