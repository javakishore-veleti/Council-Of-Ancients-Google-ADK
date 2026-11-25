import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, map, of, timeout } from 'rxjs';
import { EffectiveContext } from '../models/pack';

export interface DeliberateResponse {
  session_id: string;
  reply: string;
  status: string;
}

@Injectable({ providedIn: 'root' })
export class CouncilApiService {
  private readonly http = inject(HttpClient);
  /** Empty = same-origin / Angular proxy; override via window.COA_AGENTS_URL */
  private readonly baseUrl =
    (typeof window !== 'undefined' &&
      (window as unknown as { COA_AGENTS_URL?: string }).COA_AGENTS_URL) ||
    '';

  deliberate(
    sessionId: string,
    userId: string,
    message: string,
    ctx: EffectiveContext,
  ): Observable<DeliberateResponse> {
    return this.http
      .post<DeliberateResponse>(`${this.baseUrl}/v1/council/deliberate`, {
        session_id: sessionId,
        user_id: userId,
        message,
        ctx_data: ctx,
      })
      .pipe(
        timeout(120_000),
        catchError(() =>
          of({
            session_id: sessionId,
            status: 'offline',
            reply: this.offlineReply(message, ctx),
          }),
        ),
        map((r) => r),
      );
  }

  private offlineReply(message: string, ctx: EffectiveContext): string {
    const pack = ctx.pack_id.replace(/_/g, ' ');
    const opts = Object.keys(ctx.domain_options).join(', ') || 'none';
    return (
      `Council API is unreachable, so this is a local preview.\n\n` +
      `Pack: ${pack}\n` +
      `Left nav: ${ctx.left_nav}\n` +
      `Options: ${opts}\n` +
      `Tone: ${String(ctx.settings['tone'] ?? 'balanced')}\n\n` +
      `Your question: “${message}”\n\n` +
      `Start coa_agents_api (\`npm run local:middleware:api:all:start\`) to hear the live Facilitator and counselors.`
    );
  }
}
