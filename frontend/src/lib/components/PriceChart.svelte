<script lang="ts">
  import { onMount } from 'svelte';
  import Chart from 'chart.js/auto';
  import 'chartjs-adapter-date-fns';
  import { es } from 'date-fns/locale';

  let { priceHistoryData } = $props();

  let chartCanvas = $state<HTMLCanvasElement | null>(null);
  let chartInstance: any = null;

  onMount(() => {
    if (!priceHistoryData || priceHistoryData.length === 0 || !chartCanvas) return;

    const datasets = priceHistoryData.map((ph: any, index: number) => {
      const colors = ['#2563eb', '#16a34a', '#dc2626', '#d97706', '#7c3aed'];
      const color = colors[index % colors.length];

      return {
        label: ph.pharmacy_name,
        data: ph.data.map((d: any) => ({ x: new Date(d.date), y: d.price })),
        borderColor: color,
        backgroundColor: color,
        tension: 0.1,
        fill: false
      };
    });

    chartInstance = new Chart(chartCanvas, {
      type: 'line',
      data: {
        datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            callbacks: {
              label: function(context) {
                let label = context.dataset.label || '';
                if (label) label += ': ';
                if (context.parsed.y !== null) {
                  label += new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(context.parsed.y);
                }
                return label;
              }
            }
          }
        },
        scales: {
          x: {
            type: 'time',
            adapters: {
              date: {
                locale: es
              }
            },
            time: {
              unit: 'day',
              displayFormats: {
                day: 'dd MMM'
              }
            },
            title: {
              display: true,
              text: 'Fecha'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Precio (CLP)'
            },
            ticks: {
              callback: function(value) {
                return '$' + Number(value).toLocaleString('es-CL');
              }
            }
          }
        }
      }
    });

    return () => {
      if (chartInstance) chartInstance.destroy();
    };
  });
</script>

<div class="h-80 w-full relative">
  {#if priceHistoryData && priceHistoryData.length > 0}
    <canvas bind:this={chartCanvas}></canvas>
  {:else}
    <div class="absolute inset-0 flex items-center justify-center text-gray-500 bg-gray-50 rounded border border-dashed border-gray-300">
      No hay datos históricos de precios disponibles.
    </div>
  {/if}
</div>
