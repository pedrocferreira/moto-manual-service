import { Pipe, PipeTransform, OnDestroy } from '@angular/core';
import { LanguageService } from '../services/language.service';
import { Observable, Subject, from, of } from 'rxjs';
import { catchError, takeUntil } from 'rxjs/operators';

@Pipe({
  name: 'translate',
  standalone: true,
  pure: false
})
export class TranslatePipe implements PipeTransform, OnDestroy {
  private value: string = '';
  private lastKey: string = '';
  private destroy$ = new Subject<void>();

  constructor(private languageService: LanguageService) {}

  transform(key: string): string {
    if (!key) return '';
    if (key !== this.lastKey) {
      this.lastKey = key;
      this.updateValue(key);
    }
    return this.value;
  }

  private updateValue(key: string): void {
    from(this.languageService.translate(key))
      .pipe(
        takeUntil(this.destroy$),
        catchError(err => {
          console.error('Erro ao traduzir:', err);
          return of(key);
        })
      )
      .subscribe(translation => {
        this.value = translation;
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
} 