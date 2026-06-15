import React from 'react';

interface ScoreBadgeProps {
  score: number;
  label?: string;
}

export default function ScoreBadge({ score, label }: ScoreBadgeProps) {
  const percentage = Math.round(score * 100);
  
  let bgColor = 'bg-red-100 text-red-800 border-red-200';
  if (score >= 0.8) {
    bgColor = 'bg-green-100 text-green-800 border-green-200';
  } else if (score >= 0.5) {
    bgColor = 'bg-yellow-100 text-yellow-800 border-yellow-200';
  }

  return (
    <div className="flex items-center gap-2">
      {label && <span className="text-sm font-medium text-gray-700">{label}:</span>}
      <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${bgColor}`}>
        {percentage}%
      </span>
    </div>
  );
}
