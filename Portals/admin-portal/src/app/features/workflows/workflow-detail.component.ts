import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import {
  AdminApiService,
  WORKFLOW_ENGINE_LABELS,
  Workflow,
} from '../../core/services/admin-api.service';

@Component({
  selector: 'app-workflow-detail',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './workflow-detail.component.html',
  styleUrl: './workflow-detail.component.scss',
})
export class WorkflowDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly api = inject(AdminApiService);

  readonly workflow = signal<Workflow | null>(null);
  readonly loading = signal(true);
  readonly notFound = signal(false);
  readonly engineLabel = WORKFLOW_ENGINE_LABELS;

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.notFound.set(true);
      this.loading.set(false);
      return;
    }
    this.api.getWorkflow(id).subscribe({
      next: (wf) => {
        this.workflow.set(wf);
        this.loading.set(false);
      },
      error: () => {
        this.notFound.set(true);
        this.loading.set(false);
      },
    });
  }

  labelFor(engine: string): string {
    return this.engineLabel[engine] || engine;
  }
}
