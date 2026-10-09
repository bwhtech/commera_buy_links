<script>
export const plugin = { label: 'Analytics', icon: 'chart-line', requires: 'Buy Link', order: 2 }
</script>

<script setup>
import LinkAnalytics from '../../shared/LinkAnalytics.vue'
</script>

<template>
  <LinkAnalytics />
</template>
