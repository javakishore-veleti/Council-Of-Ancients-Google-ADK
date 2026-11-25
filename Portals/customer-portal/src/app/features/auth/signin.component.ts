import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { MessageModule } from 'primeng/message';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faScaleBalanced } from '@fortawesome/free-solid-svg-icons';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-signin',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    ButtonModule,
    InputTextModule,
    PasswordModule,
    MessageModule,
    FontAwesomeModule,
  ],
  templateUrl: './signin.component.html',
  styleUrl: './auth-shared.scss',
})
export class SigninComponent {
  readonly brandIcon = faScaleBalanced;
  email = '';
  password = '';
  readonly error = signal('');
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  submit(): void {
    this.error.set('');
    if (!this.auth.signin(this.email.trim(), this.password)) {
      this.error.set('Unable to sign in. Check email and password.');
      return;
    }
    void this.router.navigate(['/app', 'software_architecture', 'overview']);
  }
}
