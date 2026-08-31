<script lang="ts">
  import '../app.css';
  import AuthModals from '$lib/components/AuthModals.svelte';

  let { children } = $props();

  // Estados para controlar los modales
  let isLoginModalOpen = $state(false);
  let isRegisterModalOpen = $state(false);

  function openLogin() {
    isLoginModalOpen = true;
    isRegisterModalOpen = false;
  }

  function openRegister() {
    isRegisterModalOpen = true;
    isLoginModalOpen = false;
  }
</script>

<div class="min-h-screen flex flex-col bg-gray-50">
  <!-- Navbar -->
  <header class="bg-blue-600 text-white shadow-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16 items-center">
        <div class="flex-shrink-0">
          <a href="/" class="text-2xl font-bold tracking-tight">FarmaCompare</a>
        </div>
        <div class="flex space-x-4">
          <button
            class="text-blue-100 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
            onclick={openLogin}
          >
            Iniciar Sesión
          </button>
          <button
            class="bg-white text-blue-600 hover:bg-gray-100 px-4 py-2 rounded-md text-sm font-medium shadow-sm"
            onclick={openRegister}
          >
            Registrarse
          </button>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="flex-grow max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
    {@render children()}
  </main>

  <!-- Footer -->
  <footer class="bg-white border-t border-gray-200 mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <p class="text-center text-sm text-gray-500">
        &copy; 2026 FarmaCompare. Todos los derechos reservados.
      </p>
    </div>
  </footer>

  <AuthModals bind:isLoginOpen={isLoginModalOpen} bind:isRegisterOpen={isRegisterModalOpen} />
</div>
