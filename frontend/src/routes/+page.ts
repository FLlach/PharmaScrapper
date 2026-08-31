import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
  try {
    const response = await fetch('http://localhost:3000/api/v1/medicines');

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
