import { Routes } from '@angular/router';
import { AdminShellComponent } from './layout/admin-shell.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { KnowledgeSourcesComponent } from './features/knowledge-sources/knowledge-sources.component';

export const routes: Routes = [
  {
    path: '',
    component: AdminShellComponent,
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'knowledge/sources', component: KnowledgeSourcesComponent },
    ],
  },
  { path: '**', redirectTo: 'dashboard' },
];
