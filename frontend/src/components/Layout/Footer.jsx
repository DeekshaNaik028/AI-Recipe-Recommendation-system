import { Utensils, Mail, Shield } from 'lucide-react';
import './Layout.css';

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">
          <div className="footer-brand">
            <Utensils size={24} strokeWidth={2} />
            <span>MoodMunch</span>
          </div>
          <p>Cook What You Feel - AI-powered recipe recommendations</p>
        </div>
        
        <div className="footer-links">
          <a href="#about" className="footer-link">
            <span>About</span>
          </a>
          <a href="#privacy" className="footer-link">
            <Shield size={16} strokeWidth={2} />
            <span>Privacy</span>
          </a>
          <a href="#contact" className="footer-link">
            <Mail size={16} strokeWidth={2} />
            <span>Contact</span>
          </a>
        </div>

        <p className="footer-copyright">
          &copy; {year} MoodMunch. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
