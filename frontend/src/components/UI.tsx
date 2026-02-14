import React from 'react';
import clsx from 'clsx';
import { RiskLevel } from '../types/api';

interface MetricCardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  riskLevel?: RiskLevel;
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({ 
  label, 
  value, 
  icon,
  riskLevel,
  className 
}) => {
  const riskColors = {
    CRITICAL: 'border-critical bg-red-950',
    HIGH: 'border-high bg-orange-950',
    MEDIUM: 'border-medium bg-yellow-950',
    LOW: 'border-low bg-green-950',
  };

  const borderColor = riskLevel ? riskColors[riskLevel] : 'border-blue-600 bg-slate-800';

  return (
    <div
      className={clsx(
        'bg-slate-900 border-l-4 rounded-lg p-4 text-white',
        borderColor,
        className
      )}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-300 mb-1">{label}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
        {icon && <div className="text-3xl opacity-50">{icon}</div>}
      </div>
    </div>
  );
};

interface RiskBadgeProps {
  level: RiskLevel | string;
  className?: string;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, className }) => {
  const colors = {
    CRITICAL: 'bg-critical text-white',
    HIGH: 'bg-high text-white',
    MEDIUM: 'bg-medium text-white',
    LOW: 'bg-low text-white',
  };

  const color = colors[level as RiskLevel] || 'bg-gray-600 text-white';

  return (
    <span className={clsx('px-3 py-1 rounded-full text-xs font-semibold', color, className)}>
      {level}
    </span>
  );
};

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'success';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  children,
  className,
  ...props
}) => {
  const variantStyles = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-slate-700 hover:bg-slate-600 text-white',
    danger: 'bg-critical hover:bg-red-700 text-white',
    success: 'bg-low hover:bg-green-700 text-white',
  };

  const sizeStyles = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      {...props}
      disabled={isLoading || props.disabled}
      className={clsx(
        'rounded-lg font-medium transition disabled:opacity-50',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {isLoading ? '⏳ Loading...' : children}
    </button>
  );
};

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  message = 'Loading...' 
}) => {
  const sizeClass = {
    sm: 'w-6 h-6',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  };

  return (
    <div className="flex flex-col items-center justify-center py-8">
      <div className={clsx('border-4 border-slate-600 border-t-blue-500 rounded-full animate-spin', sizeClass[size])} />
      {message && <p className="mt-4 text-gray-300">{message}</p>}
    </div>
  );
};

interface ErrorAlertProps {
  title?: string;
  message: string;
  onDismiss?: () => void;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({ 
  title = 'Error', 
  message, 
  onDismiss 
}) => {
  return (
    <div className="bg-red-900 border border-red-700 rounded-lg p-4 mb-4 flex justify-between items-start">
      <div>
        <h3 className="text-red-200 font-semibold">{title}</h3>
        <p className="text-red-100 text-sm mt-1">{message}</p>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-red-300 hover:text-red-100 ml-4"
        >
          ✕
        </button>
      )}
    </div>
  );
};

interface SuccessAlertProps {
  title?: string;
  message: string;
  onDismiss?: () => void;
}

export const SuccessAlert: React.FC<SuccessAlertProps> = ({ 
  title = 'Success', 
  message, 
  onDismiss 
}) => {
  return (
    <div className="bg-green-900 border border-green-700 rounded-lg p-4 mb-4 flex justify-between items-start">
      <div>
        <h3 className="text-green-200 font-semibold">{title}</h3>
        <p className="text-green-100 text-sm mt-1">{message}</p>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-green-300 hover:text-green-100 ml-4"
        >
          ✕
        </button>
      )}
    </div>
  );
};
