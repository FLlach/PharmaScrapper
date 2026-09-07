<script lang="ts">
  let { placeholder = 'Buscar medicamentos, principios activos...', value = $bindable('') } = $props();

  function debounce<T extends (...args: any[]) => void>(fn: T, delay = 300) {
    let timeout: ReturnType<typeof setTimeout>;
    return (...args: Parameters<T>) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn(...args), delay);
    };
  }

  const handleInput = debounce((event: Event) => {
    const target = event.target as HTMLInputElement;
    value = target.value;
  }, 300);
</script>

<div class="relative max-w-2xl mx-auto mb-8">
  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
    <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
      <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
    </svg>
  </div>
  <input
    type="text"
    {placeholder}
    value={value}
    oninput={handleInput}
    class="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-lg shadow-sm"
  />
</div>
