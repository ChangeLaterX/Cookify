/**
 * Formats a date as YYYY-MM-DD
 */
export const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0];
};

/**
 * Calculates days until expiration
 */
export const getDaysUntilExpiration = (expirationDate: string | null): number | null => {
  if (!expirationDate) return null;
  
  const expDate = new Date(expirationDate);
  const today = new Date();
  
  // Reset hours to compare just the dates
  today.setHours(0, 0, 0, 0);
  expDate.setHours(0, 0, 0, 0);
  
  const diffTime = expDate.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  return diffDays;
};

/**
 * Determines expiration status: 'expired', 'expiring-soon', 'good'
 */
export const getExpirationStatus = (expirationDate: string | null): 'expired' | 'expiring-soon' | 'good' | 'unknown' => {
  if (!expirationDate) return 'unknown';
  
  const daysUntilExpiration = getDaysUntilExpiration(expirationDate);
  
  if (daysUntilExpiration === null) return 'unknown';
  if (daysUntilExpiration < 0) return 'expired';
  if (daysUntilExpiration <= 3) return 'expiring-soon';
  return 'good';
};

/**
 * Format relative time (today, yesterday, X days ago)
 */
export const formatRelativeTime = (date: string): string => {
  const now = new Date();
  const itemDate = new Date(date);
  
  // Reset hours to compare just the dates
  now.setHours(0, 0, 0, 0);
  itemDate.setHours(0, 0, 0, 0);
  
  const diffTime = now.getTime() - itemDate.getTime();
  const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 30) return `${diffDays} days ago`;
  
  const months = Math.round(diffDays / 30);
  return months === 1 ? '1 month ago' : `${months} months ago`;
};