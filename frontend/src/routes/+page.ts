import type { PageLoad } from './$types';
import { API_BASE_URL } from '$lib/config';

export const load: PageLoad = async ({ fetch }) => {
  try {
    const response = await fetch(`${API_BASE_URL}/medicines`);

    if (response.ok) {
      const medicines = await response.json();
      return { medicines };
    }

    console.error('Error fetching medicines:', response.status);
    return { medicines: [] };
  } catch (error) {
    console.error('Network error fetching medicines:', error);
    return { medicines: [] };
  }
};
