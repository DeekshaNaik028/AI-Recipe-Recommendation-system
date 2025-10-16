// components/Common/Card.jsx
import './Common.css';

export default function Card({ children, className = '' }) {
  return (
    <div className={`card ${className}`}>
      {children}
    </div>
  );
}

// components/Common/Loading.jsx
import './Common.css';

export default function Loading() {
  return (
    <div className="loading-container">
      <div className="spinner"></div>
      <p>Loading...</p>
    </div>
  );
}