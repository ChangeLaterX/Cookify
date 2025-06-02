/**
 * Utility functions for date manipulation and formatting
 */

/**
 * Calculate the difference in days between two dates
 * @param currentDate The current date
 * @param targetDate The target date to compare with
 * @returns The difference in days (positive if target is in the future)
 */
export function differenceInDays(currentDate: Date, targetDate: Date): number {
  const msPerDay = 1000 * 60 * 60 * 24;
  const diff = targetDate.getTime() - currentDate.getTime();
  return Math.round(diff / msPerDay);
}

/**
 * Format a date to display in a user-friendly format (e.g., "Jan 15, 2023")
 * @param date The date to format
 * @returns Formatted date string
 */
export function formatDate(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}

/**
 * Calculate the expiration date based on purchase date and shelf life
 * @param purchaseDate Date of purchase
 * @param shelfLifeDays Average shelf life in days
 * @returns The calculated expiration date
 */
export function calculateExpirationDate(
  purchaseDate: Date | string,
  shelfLifeDays: number
): Date {
  const dateObj = typeof purchaseDate === 'string' ? new Date(purchaseDate) : purchaseDate;
  const expirationDate = new Date(dateObj);
  expirationDate.setDate(expirationDate.getDate() + shelfLifeDays);
  return expirationDate;
}

/**
 * Get a human-readable description of time until/since expiration
 * @param expirationDate The expiration date
 * @returns Human-readable string describing time until expiration
 */
export function getExpirationDescription(expirationDate: Date | string): string {
  const now = new Date();
  const expDate = typeof expirationDate === 'string' ? new Date(expirationDate) : expirationDate;
  const days = differenceInDays(now, expDate);
  
  if (days < 0) {
    return `Expired ${Math.abs(days)} days ago`;
  } else if (days === 0) {
    return 'Expires today';
  } else if (days === 1) {
    return 'Expires tomorrow';
  } else {
    return `Expires in ${days} days`;
  }
}