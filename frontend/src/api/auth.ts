import apiClient from './client';
import type {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  RegisterResponse,
  User,
} from '../types/auth';

export const authApi = {
  /**
   * Register a new user
   */
  register: async (data: RegisterRequest): Promise<RegisterResponse> => {
    const response = await apiClient.post<RegisterResponse>('/auth/register', data);
    return response.data;
  },

  /**
   * Login with email and password
   */
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login', data);
    return response.data;
  },

  /**
   * Logout current user
   */
  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },

  /**
   * Get current user profile
   */
  getProfile: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Update user profile
   */
  updateProfile: async (data: { name: string }): Promise<User> => {
    const response = await apiClient.put<User>('/auth/me', data);
    return response.data;
  },

  /**
   * Change password for authenticated user
   */
  changePassword: async (data: {
    current_password: string;
    new_password: string;
  }): Promise<{ message: string }> => {
    const response = await apiClient.put<{ message: string }>('/auth/password', data);
    return response.data;
  },

  /**
   * Request password reset (forgot password)
   */
  forgotPassword: async (data: {
    email: string;
  }): Promise<{ message: string; reset_token?: string }> => {
    const response = await apiClient.post<{ message: string; reset_token?: string }>(
      '/auth/forgot-password',
      data
    );
    return response.data;
  },

  /**
   * Reset password with token
   */
  resetPassword: async (data: {
    token: string;
    new_password: string;
  }): Promise<{ message: string }> => {
    const response = await apiClient.post<{ message: string }>('/auth/reset-password', data);
    return response.data;
  },
};
