import { AgentResponse, MemoryRecord } from './types';

// Mock DB
export const MOCK_MEMORIES: MemoryRecord[] = [
  {
    id: 'mem_01_python',
    user_id: 'user_1',
    subject: 'User',
    predicate: 'uses',
    object: 'Python',
    memory_type: 'preference',
    content: 'Python',
    confidence: 1.0,
    status: 'SUPERSEDED',
    valid_from: '2025-01-01T00:00:00Z',
    valid_until: '2026-01-01T00:00:00Z',
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z'
  },
  {
    id: 'mem_02_java',
    user_id: 'user_1',
    subject: 'User',
    predicate: 'uses',
    object: 'Java',
    memory_type: 'preference',
    content: 'Java',
    confidence: 1.0,
    status: 'SUPERSEDED',
    valid_from: '2026-01-01T00:00:00Z',
    valid_until: '2026-04-01T00:00:00Z',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z'
  },
  {
    id: 'mem_03_cpp',
    user_id: 'user_1',
    subject: 'User',
    predicate: 'uses',
    object: 'C++',
    memory_type: 'preference',
    content: 'C++',
    confidence: 1.0,
    status: 'ACTIVE',
    valid_from: '2026-04-01T00:00:00Z',
    created_at: '2026-04-01T00:00:00Z',
    updated_at: '2026-04-01T00:00:00Z'
  },
  {
    id: 'mem_contra_dog',
    user_id: 'user_1',
    subject: 'User',
    predicate: 'likes',
    object: 'Dog',
    memory_type: 'preference',
    content: 'Dog',
    confidence: 1.0,
    status: 'ACTIVE',
    valid_from: '2026-01-01T00:00:00Z',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z'
  },
  {
    id: 'mem_contra_cat',
    user_id: 'user_1',
    subject: 'User',
    predicate: 'likes',
    object: 'Cat',
    memory_type: 'preference',
    content: 'Cat',
    confidence: 1.0,
    status: 'ACTIVE',
    valid_from: '2026-02-01T00:00:00Z',
    created_at: '2026-02-01T00:00:00Z',
    updated_at: '2026-02-01T00:00:00Z'
  },
  {
    id: 'mem_forgotten',
    user_id: 'user_1',
    subject: 'User',
    predicate: 'has',
    object: 'Code123',
    memory_type: 'fact',
    content: 'Code123',
    confidence: 1.0,
    status: 'FORGOTTEN',
    valid_from: '2026-01-01T00:00:00Z',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z'
  }
];

export async function sendMessage(userId: string, query: string): Promise<AgentResponse> {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 800));

  const q = query.toLowerCase();
  
  if (q.includes('currently using') || q.includes('current programming language')) {
    const mem = MOCK_MEMORIES.find(m => m.id === 'mem_03_cpp')!;
    return {
      answer: "You're currently using C++.",
      sources: [{ memory_id: mem.id, reason: ['semantic_match', 'current_state_match', 'active_memory'], confidence: 0.94, status: 'ACTIVE' }],
      uncertainty: false,
      conflict_detected: false,
      memories: [mem]
    };
  }

  if (q.includes('before c++')) {
    const mem = MOCK_MEMORIES.find(m => m.id === 'mem_02_java')!;
    return {
      answer: "Before C++, you were using Java.",
      sources: [{ memory_id: mem.id, reason: ['semantic_match'], confidence: 0.91, status: 'SUPERSEDED' }],
      uncertainty: false,
      conflict_detected: false,
      memories: [mem]
    };
  }

  if (q.includes('change') || q.includes('timeline')) {
    const mems = MOCK_MEMORIES.filter(m => m.id.startsWith('mem_0'));
    return {
      answer: "You started with Python in 2025, switched to Java in early 2026, and moved to C++ in April 2026.",
      sources: mems.map(m => ({ memory_id: m.id, reason: ['semantic_match'], confidence: 0.95, status: m.status })),
      uncertainty: false,
      conflict_detected: false,
      memories: mems
    };
  }

  if (q.includes('animal') || q.includes('pet')) {
    const mems = MOCK_MEMORIES.filter(m => m.id.startsWith('mem_contra'));
    return {
      answer: "I see conflicting information. You previously stated you like Dogs, but also mentioned liking Cats.",
      sources: mems.map(m => ({ memory_id: m.id, reason: ['semantic_match', 'active_memory'], confidence: 0.98, status: 'ACTIVE' })),
      uncertainty: false,
      conflict_detected: true,
      memories: mems
    };
  }

  if (q.includes('secret code') || q.includes('code123')) {
    return {
      answer: "I couldn't find a stored memory relevant to this question.",
      sources: [],
      uncertainty: true,
      conflict_detected: false,
      memories: []
    };
  }
  
  if (q.includes('user 2') || userId === 'user_2') {
    return {
      answer: "I don't have any records for that user or project in your context.",
      sources: [],
      uncertainty: true,
      conflict_detected: false,
      memories: []
    };
  }

  return {
    answer: "I'm not sure. I don't have a relevant memory for that.",
    sources: [],
    uncertainty: true,
    conflict_detected: false,
    memories: []
  };
}

export async function getTimeline(userId: string): Promise<MemoryRecord[]> {
  await new Promise(resolve => setTimeout(resolve, 500));
  if (userId !== 'user_1') return [];
  return MOCK_MEMORIES.filter(m => m.id.startsWith('mem_0'));
}
