export interface ChatMessage {
  content: string;
  type: 'user' | 'bot' | 'error';
  timestamp: Date;
  isLoading?: boolean;
  references?: string[];
} 