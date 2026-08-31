import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
  try {
    const response = await fetch(`http://localhost:3000/api/v1/medicines/${params.id}/comparison`);

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
