import React from 'react';

export const LoadingSkeleton: React.FC<{ count?: number; className?: string }> = ({ 
  count = 3, 
  className = '' 
}) => {
  return (
    <div className={`space-y-4 ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="animate-pulse space-y-2">
          <div className="h-4 bg-slate-700 rounded w-3/4"></div>
          <div className="h-4 bg-slate-700 rounded w-1/2"></div>
        </div>
      ))}
    </div>
  );
};

export const SkeletonCard: React.FC = () => (
  <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 animate-pulse">
    <div className="h-6 bg-slate-700 rounded mb-4 w-1/2"></div>
    <div className="space-y-3">
      <div className="h-4 bg-slate-700 rounded"></div>
      <div className="h-4 bg-slate-700 rounded w-5/6"></div>
      <div className="h-4 bg-slate-700 rounded w-4/6"></div>
    </div>
  </div>
);

export const SkeletonLine: React.FC<{ width?: string }> = ({ width = 'w-full' }) => (
  <div className={`h-2 bg-slate-700 rounded animate-pulse ${width}`}></div>
);
