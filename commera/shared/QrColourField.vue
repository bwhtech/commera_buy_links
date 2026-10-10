<script setup>
import { computed } from 'vue'
import { TextInput } from 'frappe-ui'
import { isHexColour } from './qrSettings'

const props = defineProps({
  label: { type: String, required: true },
  presets: { type: Array, default: () => [] },
})
const colour = defineModel({ type: String, default: '' })

const isValid = computed(() => isHexColour(colour.value))
</script>

<template>
  <div class="flex flex-col gap-1">
    <div class="flex flex-wrap items-center gap-2">
      <span class="w-20 text-sm text-ink-gray-6">{{ label }}</span>
      <label
        class="relative size-7 shrink-0 cursor-pointer overflow-hidden rounded-full border border-outline-gray-2 shadow-sm"
        :style="{ backgroundColor: isValid ? colour : 'transparent' }"
      >
        <input
          v-model="colour"
          type="color"
          class="absolute inset-0 cursor-pointer opacity-0"
          :aria-label="`Pick the ${label.toLowerCase()} colour`"
        />
      </label>
      <TextInput v-model="colour" class="w-24 font-mono" :aria-label="`${label} hex`" placeholder="#000000" />
      <div class="flex basis-full gap-1.5 pl-[5.5rem]">
        <button
          v-for="preset in presets"
          :key="preset"
          type="button"
          class="size-5 rounded-full border border-outline-gray-2 outline-offset-2 transition-transform hover:scale-110"
          :class="preset.toLowerCase() === colour?.toLowerCase() && 'outline outline-2 outline-outline-gray-4'"
          :style="{ backgroundColor: preset }"
          :aria-label="`Use ${preset}`"
          @click="colour = preset"
        />
      </div>
    </div>
    <p v-if="!isValid" class="pl-[5.5rem] text-sm text-ink-red-6">Use six hex digits, such as #111827.</p>
  </div>
</template>
