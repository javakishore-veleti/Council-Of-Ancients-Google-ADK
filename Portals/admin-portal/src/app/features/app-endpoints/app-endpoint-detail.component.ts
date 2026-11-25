import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import {
  APP_ENDPOINT_KIND_LABELS,
  AdminApiService,
  AppEndpoint,
} from '../../core/services/admin-api.service';

@Component({
  selector: 'app-app-endpoint-detail',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './app-endpoint-detail.component.html',
  styleUrl: './app-endpoint-detail.component.scss',
})
export class AppEndpointDetailComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  private readonly route = inject(ActivatedRoute);

  readonly endpoint = signal<AppEndpoint | null>(null);
  readonly loading = signal(true);
  readonly notFound = signal(false);
  readonly kindLabel = APP_ENDPOINT_KIND_LABELS;

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id') ?? '';
    if (!id) {
      this.notFound.set(true);
      this.loading.set(false);
      return;
    }
    this.api.getAppEndpoint(id).subscribe({
      next: (ep) => {
        this.endpoint.set(ep);
        this.loading.set(false);
      },
      error: () => {
        this.notFound.set(true);
        this.loading.set(false);
      },
    });
  }
}
