import { Routes } from '@angular/router';
import { AdminShellComponent } from './layout/admin-shell.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { KnowledgeSourcesComponent } from './features/knowledge-sources/knowledge-sources.component';
import { KnowledgeSourceDetailComponent } from './features/knowledge-sources/knowledge-source-detail.component';
import { AppEndpointsComponent } from './features/app-endpoints/app-endpoints.component';
import { AppEndpointDetailComponent } from './features/app-endpoints/app-endpoint-detail.component';
import { WorkflowsComponent } from './features/workflows/workflows.component';
import { WorkflowDetailComponent } from './features/workflows/workflow-detail.component';
import { WfExecLogDetailComponent } from './features/wf-exec-logs/wf-exec-log-detail.component';

export const routes: Routes = [
  {
    path: '',
    component: AdminShellComponent,
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'knowledge/sources', component: KnowledgeSourcesComponent },
      { path: 'knowledge/sources/:id', component: KnowledgeSourceDetailComponent },
      { path: 'workflows', component: WorkflowsComponent },
      { path: 'workflows/:id', component: WorkflowDetailComponent },
      { path: 'app-endpoints', component: AppEndpointsComponent },
      { path: 'app-endpoints/:id', component: AppEndpointDetailComponent },
      /** Reusable ops execution detail — back link returns to owning source. */
      { path: 'wf-exec-logs/:id', component: WfExecLogDetailComponent },
    ],
  },
  { path: '**', redirectTo: 'dashboard' },
];
