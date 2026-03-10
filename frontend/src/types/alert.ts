/** Alert rule type definitions. */

export interface Alert {
  id: number;
  name: string;
  description: string | null;
  criteria: Record<string, unknown>;
  severity_threshold: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | null;
  notification_channel: 'email' | 'slack' | 'webhook' | 'pagerduty';
  notification_target: string | null;
  is_active: boolean;
  last_triggered_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface AlertCreate {
  name: string;
  description?: string;
  criteria?: Record<string, unknown>;
  severity_threshold?: Alert['severity_threshold'];
  notification_channel?: Alert['notification_channel'];
  notification_target?: string;
  is_active?: boolean;
}
