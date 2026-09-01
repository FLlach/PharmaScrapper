<script lang="ts">
  import type { PageData } from './$types';
  import PriceChart from '$lib/components/PriceChart.svelte';

  let { data } = $props<{ data: PageData }>();
  let medicine = $derived(data.productData?.medicine);
  let pharmacies = $derived(data.productData?.pharmacies || []);
  let priceHistory = $derived(data.productData?.price_history || []);

  function formatPrice(price: number | null | undefined) {
    if (price === null || price === undefined) return 'N/A';
    return `$${price.toLocaleString('es-CL')}`;
  }
</script>

<svelte:head>
  <title>{medicine ? medicine.name || medicine.generic_name : 'Producto'} - FarmaCompare</title>
</svelte:head>

<div class="mb-4">
  <a href="/" class="text-blue-600 hover:text-blue-800 flex items-center text-sm font-medium">
    <svg class="mr-1.5 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
    </svg>
    Volver a resultados
  </a>
</div>

{#if !medicine}
  <div class="text-center py-12 bg-white rounded-lg shadow-sm">
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Producto no encontrado</h2>
    <p class="text-gray-500">No pudimos cargar la información de este producto.</p>
  </div>
{:else}
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden mb-8">
    <div class="p-6 sm:p-8">
      <div class="md:flex md:justify-between md:items-start">
        <div>
          <h1 class="text-3xl font-extrabold text-gray-900 mb-2">{medicine.name || medicine.generic_name}</h1>
          <div class="flex flex-wrap gap-2 mb-4">
            {#if medicine.bioequivalent}
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                Bioequivalente
              </span>
            {/if}
            {#if medicine.prescription_required}
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
                Receta Retenida
              </span>
            {/if}
          </div>
        </div>
      </div>

      <div class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm text-gray-600">
        {#if medicine.active_ingredient}
          <div><span class="font-medium text-gray-900">Principio Activo:</span> {medicine.active_ingredient}</div>
        {/if}
        {#if medicine.dosage}
          <div><span class="font-medium text-gray-900">Dosis:</span> {medicine.dosage}</div>
        {/if}
        {#if medicine.presentation}
          <div><span class="font-medium text-gray-900">Presentación:</span> {medicine.presentation}</div>
        {/if}
      </div>
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
    <!-- Lista de farmacias y precios actuales -->
    <div class="lg:col-span-1 space-y-6">
      <h2 class="text-xl font-bold text-gray-900 border-b pb-2">Precios Actuales</h2>

      {#if pharmacies.length === 0}
        <p class="text-gray-500">No hay información de precios en farmacias para este producto.</p>
      {:else}
        <div class="space-y-4">
          {#each pharmacies as ph}
            <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 flex justify-between items-center">
              <div>
                <h3 class="font-bold text-gray-900">{ph.name}</h3>
                {#if !ph.in_stock}
                  <span class="text-xs text-red-500 font-medium">Sin Stock</span>
                {/if}
              </div>
              <div class="text-right">
                {#if ph.price_offer}
                  <p class="text-xs text-gray-400 line-through">{formatPrice(ph.price_regular)}</p>
                  <p class="text-lg font-bold text-green-600">{formatPrice(ph.price_offer)}</p>
                {:else}
                  <p class="text-lg font-bold text-gray-900">{formatPrice(ph.price_regular)}</p>
                {/if}
                {#if ph.product_url}
                  <a href={ph.product_url} target="_blank" rel="noopener noreferrer" class="text-xs text-blue-600 hover:underline mt-1 block">
                    Ver en tienda &rarr;
                  </a>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Gráfico Histórico -->
    <div class="lg:col-span-2">
      <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h2 class="text-xl font-bold text-gray-900 mb-6">Histórico de Precios</h2>
        <PriceChart priceHistoryData={priceHistory} />
      </div>
    </div>
  </div>
{/if}
