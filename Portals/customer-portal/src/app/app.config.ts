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
      50: '#f7f1e8',
      100: '#f0e6d8',
      200: '#e0c9a8',
      300: '#d4a574',
      400: '#e08a3a',
      500: '#c45c26',
      600: '#a3481c',
      700: '#7a3514',
      800: '#2a1f18',
      900: '#1a1410',
      950: '#100c09',
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
