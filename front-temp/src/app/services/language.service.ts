import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, forkJoin, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { catchError, tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class LanguageService {
  private availableLanguages = [
    { code: 'pt-br', name: 'Português' },
    { code: 'en', name: 'English' },
    { code: 'fr', name: 'Français' }
  ];

  private currentLanguageSubject = new BehaviorSubject<string>(this.getDefaultLanguage());
  public currentLanguage$ = this.currentLanguageSubject.asObservable();
  
  private translations: {[key: string]: {[key: string]: string}} = {};
  private translationsLoaded = false;
  private translationsLoadingPromise: Promise<void> | null = null;
  
  constructor(private http: HttpClient) {
    this.loadTranslations();
  }

  private getDefaultLanguage(): string {
    // Verifica se há um idioma salvo no localStorage
    const savedLanguage = localStorage.getItem('preferredLanguage');
    if (savedLanguage && this.isLanguageSupported(savedLanguage)) {
      return savedLanguage;
    }
    
    // Verifica idioma do navegador
    const browserLang = navigator.language.toLowerCase();
    if (browserLang.startsWith('pt')) return 'pt-br';
    if (browserLang.startsWith('fr')) return 'fr';
    return 'en'; // fallback para inglês
  }

  private isLanguageSupported(langCode: string): boolean {
    return this.availableLanguages.some(lang => lang.code === langCode);
  }

  getAvailableLanguages() {
    return this.availableLanguages;
  }

  getCurrentLanguage(): string {
    return this.currentLanguageSubject.value;
  }

  setLanguage(langCode: string) {
    if (this.isLanguageSupported(langCode)) {
      localStorage.setItem('preferredLanguage', langCode);
      this.currentLanguageSubject.next(langCode);
      document.documentElement.lang = langCode;
    }
  }

  private loadTranslations(): Promise<void> {
    if (this.translationsLoadingPromise) {
      return this.translationsLoadingPromise;
    }

    this.translationsLoadingPromise = new Promise((resolve) => {
      const requests: Observable<any>[] = [];
      
      this.availableLanguages.forEach(lang => {
        requests.push(
          this.http.get<{[key: string]: string}>(`/assets/i18n/${lang.code}.json`)
            .pipe(
              tap(translations => {
                this.translations[lang.code] = translations;
                console.log(`Traduções carregadas para ${lang.code}:`, Object.keys(translations).length);
              }),
              catchError(error => {
                console.error(`Erro ao carregar traduções para ${lang.code}:`, error);
                return of({});
              })
            )
        );
      });
      
      forkJoin(requests).subscribe(() => {
        this.translationsLoaded = true;
        console.log('Todas as traduções foram carregadas');
        resolve();
      });
    });
    
    return this.translationsLoadingPromise;
  }

  async ensureTranslationsLoaded(): Promise<void> {
    if (!this.translationsLoaded) {
      await this.loadTranslations();
    }
    return Promise.resolve();
  }

  async translate(key: string): Promise<string> {
    await this.ensureTranslationsLoaded();
    
    const currentLang = this.getCurrentLanguage();
    if (this.translations[currentLang] && this.translations[currentLang][key]) {
      return this.translations[currentLang][key];
    }
    // Fallback para inglês se a tradução não for encontrada
    if (currentLang !== 'en' && this.translations['en'] && this.translations['en'][key]) {
      return this.translations['en'][key];
    }
    return key; // Retorna a chave se nenhuma tradução for encontrada
  }
} 