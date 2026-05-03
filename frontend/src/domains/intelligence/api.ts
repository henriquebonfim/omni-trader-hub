import { request } from '@/core/api';

export interface NewsAnomaly {
  title: string;
  description: string;
  impact_score: number;
}

export interface AIOverview {
  narrative: string;
  sentiment: string;
  sentiment_score: number;
  risk_score: number;
  anomalies: NewsAnomaly[];
  timestamp: number;
}

export const fetchAIOverview = async (): Promise<AIOverview> => {
  return request<AIOverview>('/api/intelligence/overview');
};

export const triggerAIOverview = async (): Promise<{ status: string; task_id: string }> => {
  return request<{ status: string; task_id: string }>('/api/intelligence/trigger', {
    method: 'POST',
  });
};
