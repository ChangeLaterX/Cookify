import { BaseItem } from './common';

export interface PantryItem extends BaseItem {
  name: string;
  quantity: number;
  unit: string;
  category: PantryCategory;
  expirationDate: string | null;
  purchaseDate: string | null;
  isStaple: boolean;
  notes?: string;
}

export type PantryCategory = 
  | 'produce'
  | 'dairy'
  | 'meat'
  | 'seafood'
  | 'frozen'
  | 'canned'
  | 'dry goods'
  | 'snacks'
  | 'beverages'
  | 'condiments'
  | 'spices'
  | 'baking'
  | 'other';

export interface ShoppingListItem extends BaseItem {
  name: string;
  quantity: number;
  unit: string;
  category: PantryCategory;
  isChecked: boolean;
  notes?: string;
}

export interface ShoppingList extends BaseItem {
  name: string;
  items: ShoppingListItem[];
}