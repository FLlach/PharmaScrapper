<script lang="ts">
  // Svelte 5 component template
  let { medicine } = $props();
</script>

<div class="product-card">
  <h3>{medicine.name}</h3>
  <!-- Mostrar precio más bajo, farmacia, stock, bioequivalencia -->
</div>

<style>
  .product-card {
    /* Estilos */
  }
</style>
