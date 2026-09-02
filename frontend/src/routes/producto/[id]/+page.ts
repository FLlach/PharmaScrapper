import type { PageLoad } from './$types';
import { API_BASE_URL } from '$lib/config';

export const load: PageLoad = async ({ params, fetch }) => {
  try {
    const response = await fetch(`${API_BASE_URL}/medicines/${params.id}/comparison`);

    if (response.ok) {
      const productData = await response.json();
      return { productData };
    }

    return { productData: null };
  } catch (error) {
    console.error('Error fetching product comparison:', error);
    return { productData: null };
  }
};
