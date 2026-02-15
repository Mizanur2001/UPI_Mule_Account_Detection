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
    CRITICAL: 'dark:border-critical dark:bg-red-950 border-red-300 bg-red-50',
    HIGH: 'dark:border-high dark:bg-orange-950 border-orange-300 bg-orange-50',
    MEDIUM: 'dark:border-medium dark:bg-yellow-950 border-yellow-300 bg-yellow-50',
    LOW: 'dark:border-low dark:bg-green-950 border-green-300 bg-green-50',
  };

  const borderColor = riskLevel ? riskColors[riskLevel] : 'dark:border-blue-600 dark:bg-slate-800 border-blue-300 bg-blue-50';

  return (
    <div
      className={clsx(
        'border-l-4 rounded-lg p-4 dark:text-white text-slate-900',
        borderColor,
        className
      )}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm dark:text-gray-300 text-gray-600 mb-1">{label}</p>
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
    primary: 'dark:bg-blue-600 dark:hover:bg-blue-700 dark:text-white bg-blue-500 hover:bg-blue-600 text-white',
    secondary: 'dark:bg-slate-700 dark:hover:bg-slate-600 dark:text-white bg-slate-300 hover:bg-slate-400 text-slate-900',
    danger: 'dark:bg-critical dark:hover:bg-red-700 dark:text-white bg-red-500 hover:bg-red-600 text-white',
    success: 'dark:bg-low dark:hover:bg-green-700 dark:text-white bg-green-500 hover:bg-green-600 text-white',
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
      <div className={clsx('border-4 dark:border-slate-600 dark:border-t-blue-500 border-slate-300 border-t-blue-400 rounded-full animate-spin', sizeClass[size])} />
      {message && <p className="mt-4 dark:text-gray-300 text-gray-600">{message}</p>}
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
    <div className="dark:bg-red-900 dark:border-red-700 dark:text-white bg-red-100 border-red-300 border rounded-lg p-4 mb-4 flex justify-between items-start text-red-900">
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
