
// components/Common/Card.jsx
import './Common.css';

export default function Card({ children, className = '' }) {
  return (
    <div className={`card ${className}`}>
      {children}
    </div>
  );
}