export interface User {
  id: string;
  email: string;
  createdAt: string;
}

export interface UserPreferences {
  id: string;
  userId: string;
  dietaryRestrictions: string[];
  favoriteCuisines: string[];
  createdAt: string;
  updatedAt: string;
}

export interface AuthResponse {
  user: User | null;
  session: any | null;
  error: Error | null;
}