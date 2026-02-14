import React from 'react';
import { ChevronRight, Home } from 'lucide-react';

interface BreadcrumbItem {
  label: string;
  onClick?: () => void;
  active?: boolean;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ items }) => {
  return (
    <div className="flex items-center gap-2 text-sm mb-4">
      <button
        className="text-gray-400 hover:text-gray-300 transition"
        onClick={() => window.location.href = '/'}
      >
        <Home size={16} />
      </button>

      {items.map((item, idx) => (
        <React.Fragment key={idx}>
          <ChevronRight size={14} className="text-gray-600" />
          {item.onClick ? (
            <button
              onClick={item.onClick}
              className={`${
                item.active
                  ? 'text-white font-semibold'
                  : 'text-gray-400 hover:text-gray-300'
              } transition`}
            >
              {item.label}
            </button>
          ) : (
            <span className={item.active ? 'text-white font-semibold' : 'text-gray-400'}>
              {item.label}
            </span>
          )}
        </React.Fragment>
      ))}
    </div>
  );
};
