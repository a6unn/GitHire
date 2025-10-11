import React, { useState, useEffect } from 'react';

interface JobDescriptionInputProps {
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
}

export const JobDescriptionInput: React.FC<JobDescriptionInputProps> = ({
  value,
  onChange,
  error,
  disabled = false,
}) => {
  const [charCount, setCharCount] = useState(0);
  const [wordCount, setWordCount] = useState(0);

  useEffect(() => {
    setCharCount(value.length);
    const words = value.trim().split(/\s+/).filter((word) => word.length > 0);
    setWordCount(words.length);
  }, [value]);

  return (
    <div className="w-full">
      <label htmlFor="job-description" className="block text-sm font-medium text-gray-700 mb-2">
        Job Description
      </label>
      <textarea
        id="job-description"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className={`
          w-full px-4 py-3 border rounded-lg resize-none
          focus:outline-none focus:ring-2 focus:ring-primary-500
          ${error ? 'border-red-500' : 'border-gray-300'}
          ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
        `}
        rows={12}
        placeholder="Paste your job description here...

Example:
We're looking for a Senior Python Developer with 5+ years of experience.

Required Skills:
- Python (expert level)
- FastAPI, Flask, or Django
- SQLAlchemy or similar ORM
- PostgreSQL or MySQL
- REST API design
- Git and GitHub"
      />
      <div className="mt-2 flex justify-between items-center">
        <div className="text-sm text-gray-600">
          {charCount} characters · {wordCount} words
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
      </div>
    </div>
  );
};
