/**
 * Header Component
 * Displays the application title, optional icon and subtitle
 */

import PropTypes from 'prop-types';
import defaultIcon from '../img/icon.svg';

const Header = ({ title, subtitle, iconSrc, iconAlt, iconSize = 40 }) => {
  const src = iconSrc || defaultIcon;

  return (
    <header className="header">
      <div className="container header-inner">
        <div className="header-left">
          {src ? (
            <img
              src={src}
              alt={iconAlt}
              className="app-icon"
              width={iconSize}
              height={iconSize}
            />
          ) : (
            <div
              className="app-icon app-icon--fallback"
              aria-hidden="true"
              style={{ width: iconSize, height: iconSize }}
            >
              🤖
            </div>
          )}

          <div className="header-text">
            <h1>{title}</h1>
            {subtitle && <p className="subtitle">{subtitle}</p>}
          </div>
        </div>
      </div>
    </header>
  );
};

Header.propTypes = {
  title: PropTypes.string,
  subtitle: PropTypes.string,
  iconSrc: PropTypes.string,
  iconAlt: PropTypes.string,
  iconSize: PropTypes.number,
};

Header.defaultProps = {
  title: 'Knowra Chatbot',
  subtitle: 'Ask me anything about the knowledge base',
  iconSrc: null, // use bundled defaultIcon if not provided
  iconAlt: 'Chatbot icon',
  iconSize: 40,
};

export default Header;
