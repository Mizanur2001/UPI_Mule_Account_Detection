import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from 'react';
import { ChevronRight, Home } from 'lucide-react';
export const Breadcrumb = ({ items }) => {
    return (_jsxs("div", { className: "flex items-center gap-2 text-sm mb-4", children: [_jsx("button", { className: "text-gray-400 hover:text-gray-300 transition", onClick: () => window.location.href = '/', children: _jsx(Home, { size: 16 }) }), items.map((item, idx) => (_jsxs(React.Fragment, { children: [_jsx(ChevronRight, { size: 14, className: "text-gray-600" }), item.onClick ? (_jsx("button", { onClick: item.onClick, className: `${item.active
                            ? 'text-white font-semibold'
                            : 'text-gray-400 hover:text-gray-300'} transition`, children: item.label })) : (_jsx("span", { className: item.active ? 'text-white font-semibold' : 'text-gray-400', children: item.label }))] }, idx)))] }));
};
