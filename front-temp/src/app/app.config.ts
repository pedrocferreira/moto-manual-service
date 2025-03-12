import { ApplicationConfig, APP_INITIALIZER, importProvidersFrom } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { provideHttpClient, withInterceptors, HTTP_INTERCEPTORS } from '@angular/common/http';
import { AuthInterceptor } from './interceptors/auth.interceptor';
import { TranslatePipe } from './pipes/translate.pipe';
import { LanguageService } from './services/language.service';

// Factory para pré-carregar as traduções
export function preloadTranslationsFactory(languageService: LanguageService) {
  return () => languageService.ensureTranslationsLoaded();
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(),
    { 
      provide: HTTP_INTERCEPTORS, 
      useClass: AuthInterceptor, 
      multi: true 
    },
    LanguageService,
    TranslatePipe,
    {
      provide: APP_INITIALIZER,
      useFactory: preloadTranslationsFactory,
      deps: [LanguageService],
      multi: true
    }
  ]
}; 