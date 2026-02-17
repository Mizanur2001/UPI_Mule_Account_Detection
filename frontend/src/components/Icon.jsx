import React from 'react';

/**
 * Wrapper for Google Material Symbols Outlined icons.
 * Usage: <Icon name="shield" size={20} color="#ef4444" />
 */
export default function Icon({ name, size = 20, color, style, className = '' }) {
  return (
    <span
      className={`material-symbols-outlined ${className}`}
      style={{
        fontSize: size,
        verticalAlign: 'middle',
        color,
        lineHeight: 1,
        ...style,
      }}
    >
      {name}
    </span>
  );
}
