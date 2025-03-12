import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { TranslatePipe } from '../../pipes/translate.pipe';
import { LanguageSelectorComponent } from '../language-selector/language-selector.component';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslatePipe, LanguageSelectorComponent],
  template: `
    <div class="login-container">
      <div class="login-box">
        <div class="language-selector-container">
          <app-language-selector></app-language-selector>
        </div>
        <h2>{{ 'app.login.title' | translate }}</h2>
        <form (ngSubmit)="onSubmit()">
          <div class="form-group">
            <input type="text" 
                   [(ngModel)]="username" 
                   name="username" 
                   placeholder="{{ 'app.login.username' | translate }}"
                   required>
          </div>
          <div class="form-group">
            <input type="password" 
                   [(ngModel)]="password" 
                   name="password" 
                   placeholder="{{ 'app.login.password' | translate }}"
                   required>
          </div>
          <button type="submit">{{ 'app.login.submit' | translate }}</button>
          <div *ngIf="error" class="error-message">
            {{ error | translate }}
          </div>
        </form>
      </div>
    </div>
  `,
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  username: string = '';
  password: string = '';
  error: string = '';

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit() {
    if (!this.username || !this.password) {
      this.error = 'app.login.required';
      return;
    }

    this.authService.login(this.username, this.password).subscribe({
      next: () => {
        this.router.navigate(['/chat']);
      },
      error: (err) => {
        this.error = 'app.login.error';
        console.error('Erro no login:', err);
      }
    });
  }
} 