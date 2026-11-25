import { Routes } from '@angular/router';
import { AdminShellComponent } from './layout/admin-shell.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { KnowledgeSourcesComponent } from './features/knowledge-sources/knowledge-sources.component';
import { KnowledgeSourceDetailComponent } from './features/knowledge-sources/knowledge-source-detail.component';
import { AppEndpointsComponent } from './features/app-endpoints/app-endpoints.component';
import { AppEndpointDetailComponent } from './features/app-endpoints/app-endpoint-detail.component';

export const routes: Routes = [
  {
    path: '',
    component: AdminShellComponent,
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'knowledge/sources', component: KnowledgeSourcesComponent },
      { path: 'knowledge/sources/:id', component: KnowledgeSourceDetailComponent },
      { path: 'app-endpoints', component: AppEndpointsComponent },
      { path: 'app-endpoints/:id', component: AppEndpointDetailComponent },
    ],
  },
  { path: '**', redirectTo: 'dashboard' },
];
