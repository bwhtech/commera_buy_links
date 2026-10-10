import { definePlugin } from '@commera/plugin-kit'

export default definePlugin({
  sidebar: [
    {
      name: 'settings',
      label: 'Settings',
      icon: 'settings',
      requires: 'Buy Links Settings',
      order: 9,
      run: ({ openSettings }) => openSettings(),
    },
  ],
})
