/**
 * Color utility functions for GitHire
 */

export type ColorVariant = 'primary' | 'secondary' | 'accent' | 'success' | 'error' | 'warning' | 'info' | 'default' | 'danger';
export type ColorShade = 50 | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 950;

/**
 * Get score color based on value (0-100)
 */
export function getScoreColor(score: number): string {
  if (score >= 80) return 'emerald';
  if (score >= 60) return 'green';
  if (score >= 40) return 'yellow';
  if (score >= 20) return 'orange';
  return 'red';
}

/**
 * Get score gradient class based on value
 */
export function getScoreGradient(score: number): string {
  if (score >= 80) return 'from-emerald-500 to-green-500';
  if (score >= 60) return 'from-green-500 to-lime-500';
  if (score >= 40) return 'from-yellow-500 to-amber-500';
  if (score >= 20) return 'from-orange-500 to-red-500';
  return 'from-red-600 to-red-800';
}

/**
 * Get text color class for score
 */
export function getScoreTextColor(score: number): string {
  if (score >= 80) return 'text-emerald-600';
  if (score >= 60) return 'text-green-600';
  if (score >= 40) return 'text-yellow-600';
  if (score >= 20) return 'text-orange-600';
  return 'text-red-600';
}

/**
 * Get background color class for score
 */
export function getScoreBgColor(score: number): string {
  if (score >= 80) return 'bg-emerald-50';
  if (score >= 60) return 'bg-green-50';
  if (score >= 40) return 'bg-yellow-50';
  if (score >= 20) return 'bg-orange-50';
  return 'bg-red-50';
}

/**
 * Get badge color classes based on variant
 */
export function getBadgeColors(variant: ColorVariant): string {
  const colorMap = {
    primary: 'bg-primary-100 text-primary-700 border-primary-200',
    secondary: 'bg-secondary-100 text-secondary-700 border-secondary-200',
    accent: 'bg-accent-100 text-accent-700 border-accent-200',
    success: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    error: 'bg-red-100 text-red-700 border-red-200',
    danger: 'bg-red-100 text-red-700 border-red-200',
    warning: 'bg-amber-100 text-amber-700 border-amber-200',
    info: 'bg-blue-100 text-blue-700 border-blue-200',
    default: 'bg-gray-100 text-gray-700 border-gray-200',
  };
  return colorMap[variant];
}

/**
 * Get status color based on project status
 */
export function getStatusColor(status: string): ColorVariant {
  const statusMap: Record<string, ColorVariant> = {
    completed: 'success',
    success: 'success',
    failed: 'error',
    error: 'error',
    running: 'info',
    pending: 'warning',
    in_progress: 'info',
  };
  return statusMap[status.toLowerCase()] || 'info';
}

/**
 * Generate avatar background color based on string (e.g., email)
 */
export function getAvatarColor(str: string): string {
  const colors = [
    'bg-primary-500',
    'bg-secondary-500',
    'bg-accent-500',
    'bg-emerald-500',
    'bg-blue-500',
    'bg-purple-500',
    'bg-pink-500',
    'bg-indigo-500',
  ];

  const hash = str.split('').reduce((acc, char) => {
    return char.charCodeAt(0) + ((acc << 5) - acc);
  }, 0);

  return colors[Math.abs(hash) % colors.length];
}

/**
 * Convert hex color to RGB
 */
export function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

/**
 * Get contrast text color (black or white) for a background color
 */
export function getContrastText(bgColor: string): 'text-white' | 'text-black' {
  const rgb = hexToRgb(bgColor);
  if (!rgb) return 'text-white';

  // Calculate relative luminance
  const luminance = (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;

  return luminance > 0.5 ? 'text-black' : 'text-white';
}
