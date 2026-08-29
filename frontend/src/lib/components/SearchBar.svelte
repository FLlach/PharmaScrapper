<script lang="ts">
  // Svelte 5 component template
  let { placeholder = 'Buscar medicamentos...', value = $bindable('') } = $props();

  function handleInput(event: Event) {
    // Lógica de debounce para búsqueda
  }
</script>

<div class="search-bar">
  <input
    type="text"
    {placeholder}
    bind:value
    oninput={handleInput}
  />
</div>

<style>
  .search-bar {
    /* Estilos */
  }
</style>
