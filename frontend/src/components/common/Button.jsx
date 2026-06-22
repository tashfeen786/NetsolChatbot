import React from 'react';

export default function Button({ children, onClick, variant = 'primary', className = '', ...props }) {
  const base = 'px-5 py-2.5 rounded-xl font-medium transition-all duration-200';
  const variants = {
    primary: 'gradient-primary gradient-primary-hover text-white shadow-lg shadow-indigo-500/25',
    secondary: 'bg-gray-200 text-gray-700 hover:bg-gray-300',
    outline: 'border-2 border-gray-300 text-gray-700 hover:bg-gray-50',
  };
  return (
    <button className={`${base} ${variants[variant]} ${className}`} onClick={onClick} {...props}>
      {children}
    </button>
  );
}