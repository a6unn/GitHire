export interface User {
  user_id: string;
  email: string;
  name?: string | null;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterResponse {
  user_id: string;
  email: string;
  created_at: string;
}
