<script lang="ts">
  let { medicine } = $props();
</script>

<div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
  <div class="p-5">
    <div class="flex justify-between items-start mb-2">
      <h3 class="text-lg font-semibold text-gray-900 line-clamp-2">
        <a href={`/producto/${medicine.id}`} class="hover:text-blue-600">{medicine.name || medicine.generic_name}</a>
      </h3>
      {#if medicine.bioequivalent}
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          Bioequivalente
        </span>
      {/if}
    </div>

    <div class="text-sm text-gray-500 mb-4">
      {#if medicine.active_ingredient}
        <p><span class="font-medium text-gray-700">Activo:</span> {medicine.active_ingredient}</p>
      {/if}
      {#if medicine.dosage}
        <p><span class="font-medium text-gray-700">Dosis:</span> {medicine.dosage}</p>
      {/if}
    </div>

    <div class="mt-4 pt-4 border-t border-gray-100 flex justify-between items-center">
      <div>
        <p class="text-xs text-gray-500 mb-1">Desde</p>
        <p class="text-xl font-bold text-green-600">
          {medicine.lowest_price ? `$${medicine.lowest_price.toLocaleString('es-CL')}` : 'Sin stock'}
        </p>
      </div>
      <a href={`/producto/${medicine.id}`} class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none">
        Comparar
      </a>
    </div>
  </div>
</div>
