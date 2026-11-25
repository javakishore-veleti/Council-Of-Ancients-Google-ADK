import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { providePrimeNG } from 'primeng/config';
import Aura from '@primeng/themes/aura';
import { definePreset } from '@primeng/themes';
import { routes } from './app.routes';

const CoaAura = definePreset(Aura, {
  semantic: {
    primary: {
      50: '#e8f7f2',
      100: '#d4efe8',
      200: '#a8ddd4',
      300: '#6fc4b8',
      400: '#3aa39a',
      500: '#127a86',
      600: '#0a4f5c',
      700: '#083f4a',
      800: '#062a36',
      900: '#041e28',
      950: '#021419',
    },
  },
});

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(),
    provideAnimationsAsync(),
    providePrimeNG({
      theme: {
        preset: CoaAura,
        options: {
          darkModeSelector: false,
        },
      },
    }),
  ],
};
