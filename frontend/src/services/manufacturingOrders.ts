const API_URL = import.meta.env.VITE_API_URL;

export interface ManufacturingOrder {
  _id: string;
  productName: string;
  quantity: number;
  bomId: string;
  status: 'planned' | 'progress' | 'completed' | 'delayed';
  createdAt: string;
  updatedAt: string;
}

export const getManufacturingOrders = async (
  status: string,
  searchTerm: string,
  token: string
): Promise<ManufacturingOrder[]> => {
  const params = new URLSearchParams();
  if (status !== 'all') {
    params.append('status', status);
  }
  // Assuming your backend supports a search query parameter, e.g., 'q'
  if (searchTerm) {
    params.append('q', searchTerm);
  }

  const response = await fetch(`${API_URL}/api/manufacturing-orders?${params.toString()}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) throw new Error('Failed to fetch manufacturing orders');
  const data = await response.json();
  return data.data; // Assuming the API returns { data: [...] }
};