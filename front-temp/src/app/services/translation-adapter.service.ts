import { Injectable, OnDestroy } from '@angular/core';
import { LanguageService } from './language.service';
import { Subscription } from 'rxjs';

/**
 * Serviço adaptador para facilitar traduções síncronas em templates
 * Mantém um cache de traduções para uso rápido
 */
@Injectable({
  providedIn: 'root'
})
export class TranslationAdapterService implements OnDestroy {
  private translationCache: {[lang: string]: {[key: string]: string}} = {};
  private currentLang: string;
  private langSubscription: Subscription;
  
  constructor(private languageService: LanguageService) {
    this.currentLang = this.languageService.getCurrentLanguage();
    
    // Inscreve para alterações de idioma
    this.langSubscription = this.languageService.currentLanguage$.subscribe(lang => {
      this.currentLang = lang;
    });
    
    // Pré-carrega traduções
    this.initializeCache();
  }
  
  ngOnDestroy() {
    if (this.langSubscription) {
      this.langSubscription.unsubscribe();
    }
  }
  
  private async initializeCache() {
    await this.languageService.ensureTranslationsLoaded();
    // O cache será preenchido sob demanda
  }
  
  /**
   * Obtém tradução síncrona (usando cache)
   * Se não estiver em cache, retorna a chave e tenta carregar assincronamente para o futuro
   */
  getTranslation(key: string): string {
    if (!key) return '';
    
    const lang = this.currentLang;
    
    // Verifica se já está no cache
    if (this.translationCache[lang]?.[key]) {
      return this.translationCache[lang][key];
    }
    
    // Não está no cache, vamos carregar para o futuro e retornar a chave por enquanto
    this.loadTranslationToCache(key, lang);
    return key;
  }
  
  private async loadTranslationToCache(key: string, lang: string) {
    try {
      const translation = await this.languageService.translate(key);
      
      // Armazena no cache
      if (!this.translationCache[lang]) {
        this.translationCache[lang] = {};
      }
      this.translationCache[lang][key] = translation;
      
      // Força atualização se o componente estiver usando o pipe
      // (isso depende da implementação do seu pipe)
    } catch (err) {
      console.error(`Erro ao carregar tradução para ${key}:`, err);
    }
  }
} 