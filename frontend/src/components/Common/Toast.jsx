import { useEffect } from 'react';
import { CheckCircle, AlertCircle, Info, AlertTriangle, X } from 'lucide-react';
import './Common.css';

const iconMap = {
  success: CheckCircle,
  error: AlertCircle,
  info: Info,
  warning: AlertTriangle,
};

export default function Toast({ message, type = 'info', onClose }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const IconComponent = iconMap[type];

  return (
    <div className={`toast toast-${type}`}>
      {IconComponent && <IconComponent className="toast-icon" size={20} strokeWidth={2} />}
      <span className="toast-message">{message}</span>
      <button className="toast-close" onClick={onClose}>
        <X size={16} strokeWidth={2} />
      </button>
    </div>
  );
}
