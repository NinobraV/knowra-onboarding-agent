/**
 * Header Component
 * Displays the application title and subtitle
 */

import PropTypes from 'prop-types';

const Header = ({ title, subtitle }) => {
  return (
    <header className="header">
      <div className="container">
        <h1>{title}</h1>
        {subtitle && <p className="subtitle">{subtitle}</p>}
      </div>
    </header>
  );
};

Header.propTypes = {
  title: PropTypes.string,
  subtitle: PropTypes.string,
};

Header.defaultProps = {
  title: '🤖 Knowledge Chatbot',
  subtitle: 'Ask me anything about the knowledge base',
};

export default Header;
