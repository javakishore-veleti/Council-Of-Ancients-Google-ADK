import { Injectable, signal, computed } from '@angular/core';
import { CookieService } from 'ngx-cookie-service';

export interface PortalUser {
  id: string;
  email: string;
  displayName: string;
}

const USER_KEY = 'coa_portal_user';
const TOKEN_KEY = 'coa_portal_token';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly userSignal = signal<PortalUser | null>(this.readUser());

  readonly user = this.userSignal.asReadonly();
  readonly isAuthenticated = computed(() => !!this.userSignal());

  constructor(private readonly cookies: CookieService) {}

  signup(email: string, password: string, displayName: string): boolean {
    if (!email || !password || password.length < 6) {
      return false;
    }
    const user: PortalUser = {
      id: `cust_${btoa(email).replace(/=+/g, '').slice(0, 12)}`,
      email,
      displayName: displayName || email.split('@')[0],
    };
    // Local stub until coa_auth_api lands
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    this.cookies.set(TOKEN_KEY, `stub.${user.id}`, 7, '/');
    this.userSignal.set(user);
    return true;
  }

  signin(email: string, password: string): boolean {
    if (!email || !password) {
      return false;
    }
    const existing = this.readUser();
    if (existing && existing.email === email) {
      this.cookies.set(TOKEN_KEY, `stub.${existing.id}`, 7, '/');
      this.userSignal.set(existing);
      return true;
    }
    return this.signup(email, password, email.split('@')[0]);
  }

  signout(): void {
    localStorage.removeItem(USER_KEY);
    this.cookies.delete(TOKEN_KEY, '/');
    this.userSignal.set(null);
  }

  token(): string | null {
    return this.cookies.get(TOKEN_KEY) || null;
  }

  private readUser(): PortalUser | null {
    try {
      const raw = localStorage.getItem(USER_KEY);
      return raw ? (JSON.parse(raw) as PortalUser) : null;
    } catch {
      return null;
    }
  }
}
