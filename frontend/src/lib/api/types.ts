export type MemoryStatus = 'ACTIVE' | 'SUPERSEDED' | 'EXPIRED' | 'FORGOTTEN' | 'ARCHIVED';
export type MemoryType = 'fact' | 'preference' | 'relationship';

export interface MemoryRecord {
  id: string;
  user_id: string;
  subject: string;
  predicate: string;
  object: string;
  memory_type: MemoryType;
  content: string;
  confidence: number;
  status: MemoryStatus;
  valid_from?: string;
  valid_until?: string;
  created_at: string;
  updated_at: string;
}

export interface ProvenanceSource {
  memory_id: string;
  reason: string[];
  confidence: number;
  status: MemoryStatus;
}

export interface AgentResponse {
  answer: string;
  sources: ProvenanceSource[];
  uncertainty: boolean;
  conflict_detected: boolean;
  memories?: MemoryRecord[]; // Appended by mock for easy UI rendering
}

