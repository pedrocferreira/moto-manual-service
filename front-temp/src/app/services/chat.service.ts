import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { ChatMessage } from '../models/chat.model';

interface ApiResponse {
  answer: string;
  references?: string[];
  status: string;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = '/ask-manual/';

  constructor(private http: HttpClient) {}

  askManual(query: string): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(this.apiUrl, { query }).pipe(
      catchError(this.handleError)
    );
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'Ocorreu um erro ao processar sua solicitação.';
    
    if (error.error instanceof ErrorEvent) {
      errorMessage = `Erro: ${error.error.message}`;
    } else {
      errorMessage = `Código: ${error.status}, Mensagem: ${error.error?.message || error.message}`;
    }
    
    return throwError(() => errorMessage);
  }
} 