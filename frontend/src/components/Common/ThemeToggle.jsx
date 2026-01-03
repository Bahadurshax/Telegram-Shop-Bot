import React from 'react';
import { useTheme } from '../../context/ThemeContext';

const ThemeToggle = ({ className = '', showLabel = true }) => {
    const { theme, toggleTheme } = useTheme();

    const isDark = theme === 'dark';

    return (
        <button
            onClick={toggleTheme}
            className={`flex items-center ${showLabel ? 'w-full px-4 py-2' : 'p-2 justify-center'} text-sm font-medium rounded-lg transition-colors 
                ${isDark
                    ? 'text-slate-400 hover:bg-slate-700 hover:text-slate-200'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                } ${className}`}
            title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
            {isDark ? (
                // Sun Icon for Dark Mode (to switch to light)
                <svg className={`w-5 h-5 ${showLabel ? 'mr-3' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4-9H3m3.343-5.657l-.707-.707m12.728 12.728l-.707-.707M6.343 17.657l-.707.707M17.657 6.343l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
            ) : (
                // Moon Icon for Light Mode (to switch to dark)
                <svg className={`w-5 h-5 ${showLabel ? 'mr-3' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
            )}

            {showLabel && (
                <span>{isDark ? 'Светлая тема' : 'Ночная тема'}</span>
            )}
        </button>
    );
};

export default ThemeToggle;
