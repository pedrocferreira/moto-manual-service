import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-language-selector',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="language-selector">
      <select (change)="changeLanguage($event)" [value]="currentLanguage">
        <option *ngFor="let lang of availableLanguages" [value]="lang.code">
          {{ lang.name }}
        </option>
      </select>
    </div>
  `,
  styles: [`
    .language-selector {
      display: inline-block;
    }
    
    select {
      padding: 0.5rem;
      border-radius: 0.5rem;
      background: rgba(255, 255, 255, 0.1);
      color: #fff;
      border: 1px solid rgba(255, 255, 255, 0.2);
      cursor: pointer;
    }
    
    select:focus {
      outline: none;
      box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.5);
    }
  `]
})
export class LanguageSelectorComponent implements OnInit {
  currentLanguage: string = 'pt-br';
  availableLanguages: {code: string, name: string}[] = [];

  constructor(private languageService: LanguageService) {}

  ngOnInit() {
    this.availableLanguages = this.languageService.getAvailableLanguages();
    this.languageService.currentLanguage$.subscribe(lang => {
      this.currentLanguage = lang;
    });
  }

  changeLanguage(event: Event) {
    const select = event.target as HTMLSelectElement;
    this.languageService.setLanguage(select.value);
  }
} 