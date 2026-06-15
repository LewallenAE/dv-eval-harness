import React from 'react';
import LoadingSpinner from './LoadingSpinner';

interface RunButtonProps {
  onClick: () => void;
  loading: boolean;
  disabled?: boolean;
}

export default function RunButton({ onClick, loading, disabled }: RunButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={loading || disabled}
      className={`
        flex items-center justify-center gap-2 px-6 py-2.5 
        rounded-lg font-semibold text-white transition-all
        ${loading || disabled 
          ? 'bg-blue-400 cursor-not-allowed' 
          : 'bg-blue-600 hover:bg-blue-700 active:transform active:scale-95'}
      `}
    >
      {loading ? (
        <>
          <LoadingSpinner size="sm" />
          <span>Running Agent...</span>
        </>
      ) : (
        <>
          <svg 
            className="w-5 h-5" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" 
            />
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
            />
          </svg>
          <span>Run Case</span>
        </>
      )}
    </button>
  );
}
