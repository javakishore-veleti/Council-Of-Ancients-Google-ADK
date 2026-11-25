import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { ShellComponent } from './layout/shell.component';
import { SigninComponent } from './features/auth/signin.component';
import { SignupComponent } from './features/auth/signup.component';
import { OverviewComponent } from './features/overview/overview.component';
import { ChamberComponent } from './features/chamber/chamber.component';
import { SessionsComponent } from './features/sessions/sessions.component';
import { SettingsComponent } from './features/settings/settings.component';
import { SectionHubComponent } from './features/section-hub/section-hub.component';
import { PackId } from './core/models/pack';
import { inject } from '@angular/core';
import { PreferencesService } from './core/services/preferences.service';
import { CanActivateFn, Router } from '@angular/router';

const syncPackGuard: CanActivateFn = (route) => {
  const prefs = inject(PreferencesService);
  const router = inject(Router);
  const packId = route.paramMap.get('packId') as PackId | null;
  if (!packId) {
    return router.createUrlTree(['/app', 'software_architecture', 'overview']);
  }
  if (prefs.activePackId() !== packId) {
    prefs.setPack(packId);
  }
  return true;
};

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'app/software_architecture/overview' },
  { path: 'signin', component: SigninComponent },
  { path: 'signup', component: SignupComponent },
  {
    path: 'app',
    component: ShellComponent,
    canActivate: [authGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'software_architecture/overview' },
      {
        path: 'settings/global',
        component: SettingsComponent,
        data: { scope: 'global' },
      },
      {
        path: ':packId',
        canActivate: [syncPackGuard],
        children: [
          { path: '', pathMatch: 'full', redirectTo: 'overview' },
          { path: 'overview', component: OverviewComponent },
          { path: 'section', component: SectionHubComponent },
          { path: 'chamber', component: ChamberComponent },
          { path: 'sessions', component: SessionsComponent },
          {
            path: 'settings',
            component: SettingsComponent,
            data: { scope: 'pack' },
          },
        ],
      },
    ],
  },
  { path: '**', redirectTo: 'app/software_architecture/overview' },
];
