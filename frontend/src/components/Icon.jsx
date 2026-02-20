import React from 'react';

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
