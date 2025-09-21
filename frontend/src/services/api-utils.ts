// API error handling utilities

export class ApiError extends Error {
  constructor(public statusCode: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export const handleApiResponse = async (response: Response): Promise<any> => {
  if (response.status === 403) {
    throw new ApiError(403, 'ACCESS_DENIED');
  }
  
  if (response.status === 401) {
    throw new ApiError(401, 'UNAUTHORIZED');
  }
  
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      // If we can't parse the error response, use the default message
    }
    throw new ApiError(response.status, errorMessage);
  }
  
  return response.json();
};

export const isAccessDeniedError = (error: Error): boolean => {
  return error instanceof ApiError && error.statusCode === 403;
};

export const isUnauthorizedError = (error: Error): boolean => {
  return error instanceof ApiError && error.statusCode === 401;
};