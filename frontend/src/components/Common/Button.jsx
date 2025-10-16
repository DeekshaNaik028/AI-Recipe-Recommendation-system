// components/Common/Button.jsx
import './Common.css';

export default function Button({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  disabled = false, 
  full = false,
  ...props 
}) {
  return (
    <button
      className={`btn btn-${variant} btn-${size} ${full ? 'btn-full' : ''}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}