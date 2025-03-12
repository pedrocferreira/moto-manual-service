import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { LanguageSelectorComponent } from '../language-selector/language-selector.component';
import { TranslatePipe } from '../../pipes/translate.pipe';
import { TranslationDebugComponent } from '../translation-debug/translation-debug.component';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule, 
    RouterModule, 
    LanguageSelectorComponent, 
    TranslatePipe,
    TranslationDebugComponent
  ],
  template: `
    <div class="home-container">
      <div class="language-option">
        <app-language-selector></app-language-selector>
      </div>
      <h1>{{ 'app.home.title' | translate }}</h1>
      <p>{{ 'app.home.description' | translate }}</p>
      <div class="navigation">
        <a routerLink="/chat">{{ 'app.nav.chat' | translate }}</a>
        <a routerLink="/login">{{ 'app.nav.login' | translate }}</a>
      </div>
      
      <!-- Componente de depuração -->
      <app-translation-debug></app-translation-debug>
    </div>
  `,
  styles: [`
    .home-container {
      padding: 20px;
      text-align: center;
    }
    .navigation {
      margin-top: 20px;
    }
    .navigation a {
      margin: 0 10px;
      padding: 10px 20px;
      background-color: #007bff;
      color: white;
      text-decoration: none;
      border-radius: 5px;
    }
    .navigation a:hover {
      background-color: #0056b3;
    }
    .language-option {
      position: absolute;
      top: 10px;
      right: 20px;
    }
  `]
})
export class HomeComponent {}