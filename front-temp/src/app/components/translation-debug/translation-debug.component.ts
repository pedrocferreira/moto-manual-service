import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-translation-debug',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="debug-panel" *ngIf="showDebug">
      <h3>Debug de Traduções</h3>
      <p>Idioma atual: {{ currentLanguage }}</p>
      <p>Status de carregamento: {{ loaded ? 'Carregado' : 'Carregando...' }}</p>
      <div *ngIf="loaded">
        <h4>Chaves disponíveis (primeiras 10):</h4>
        <ul>
          <li *ngFor="let key of availableKeys.slice(0, 10)">
            {{ key }}: {{ translations[key] }}
          </li>
        </ul>
      </div>
      <button (click)="toggleDebug()">Fechar</button>
    </div>
    <button 
      *ngIf="!showDebug" 
      (click)="toggleDebug()"
      style="position: fixed; bottom: 10px; right: 10px; z-index: 1000;">
      Debug i18n
    </button>
  `,
  styles: [`
    .debug-panel {
      position: fixed;
      bottom: 0;
      right: 0;
      width: 300px;
      background-color: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 10px;
      z-index: 1000;
      max-height: 400px;
      overflow-y: auto;
    }
  `]
})
export class TranslationDebugComponent implements OnInit {
  showDebug = false;
  currentLanguage = '';
  loaded = false;
  translations: {[key: string]: string} = {};
  availableKeys: string[] = [];

  constructor(private languageService: LanguageService) {}

  ngOnInit() {
    this.currentLanguage = this.languageService.getCurrentLanguage();
    this.languageService.ensureTranslationsLoaded().then(() => {
      this.loaded = true;
      // Simular a obtenção de todas as chaves de tradução
      this.loadSampleKeys();
    });
    
    this.languageService.currentLanguage$.subscribe(lang => {
      this.currentLanguage = lang;
      this.loadSampleKeys();
    });
  }

  async loadSampleKeys() {
    // Exemplos de chaves para testar
    const sampleKeys = [
      'app.title',
      'app.chat.placeholder',
      'app.chat.send',
      'app.nav.home',
      'app.login.title'
    ];
    
    this.availableKeys = sampleKeys;
    this.translations = {};
    
    for (const key of sampleKeys) {
      this.translations[key] = await this.languageService.translate(key);
    }
  }

  toggleDebug() {
    this.showDebug = !this.showDebug;
  }
} 