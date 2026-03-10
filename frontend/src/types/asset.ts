/** Asset type definitions. */

export interface Asset {
  id: number;
  name: string;
  vendor: string | null;
  version: string | null;
  asset_type: 'application' | 'os' | 'library' | 'firmware' | 'network' | 'hardware';
  cpe: string | null;
  description: string | null;
  tags: string[] | null;
  extra: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface AssetCreate {
  name: string;
  vendor?: string;
  version?: string;
  asset_type?: Asset['asset_type'];
  cpe?: string;
  description?: string;
  tags?: string[];
}
