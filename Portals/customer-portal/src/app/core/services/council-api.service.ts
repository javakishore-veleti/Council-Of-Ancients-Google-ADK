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

  private offlineReply(message: string, _ctx: EffectiveContext): string {
    return (
      `The council is briefly unavailable. Please try again in a moment.\n\n` +
      `Your question was saved: “${message}”`
    );
  }
}
