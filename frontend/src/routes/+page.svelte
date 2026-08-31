<script lang="ts">
  import type { PageData } from './$types';
  import SearchBar from '$lib/components/SearchBar.svelte';
  import ProductCard from '$lib/components/ProductCard.svelte';

  let { data } = $props<{ data: PageData }>();

  let searchQuery = $state('');

  // Filtro en cliente reactivo
  let filteredMedicines = $derived(
    data.medicines.filter((med: any) => {
      const search = searchQuery.toLowerCase();
      const nameMatch = (med.name || med.generic_name || '').toLowerCase().includes(search);
      const activeMatch = (med.active_ingredient || '').toLowerCase().includes(search);
      return nameMatch || activeMatch;
    })
  );
</script>

<svelte:head>
  <title>FarmaCompare - Busca y compara medicamentos en Chile</title>
</svelte:head>

<div class="text-center mb-10">
  <h1 class="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl mb-4">
    Encuentra el <span class="text-blue-600">mejor precio</span>
  </h1>
  <p class="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
    Compara precios de medicamentos y productos farmacéuticos en las principales cadenas de Chile.
  </p>
</div>

<SearchBar bind:value={searchQuery} />

{#if data.medicines.length === 0}
  <div class="text-center py-12 bg-white rounded-lg shadow-sm">
    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
    <h3 class="mt-2 text-sm font-medium text-gray-900">Sin medicamentos</h3>
    <p class="mt-1 text-sm text-gray-500">No se pudieron cargar los datos de la API o el catálogo está vacío.</p>
  </div>
{:else if filteredMedicines.length === 0}
  <div class="text-center py-12">
    <p class="text-lg text-gray-500">No se encontraron medicamentos para "{searchQuery}".</p>
  </div>
{:else}
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
    {#each filteredMedicines as medicine (medicine.id)}
      <ProductCard {medicine} />
    {/each}
  </div>
{/if}
