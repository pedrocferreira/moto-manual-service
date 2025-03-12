import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { ChatMessage } from '../models/chat.model';

export interface ApiResponse {
  answer: string;
  references?: string[];
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  // Use URL absoluta para desenvolvimento, o proxy vai redirecionar
  private apiUrl = '/ask-manual/';

  constructor(private http: HttpClient) {
    console.log('ChatService inicializado com URL:', this.apiUrl);
  }

  askManual(query: string, language: string = 'pt-br'): Observable<ApiResponse> {
    console.log('Enviando consulta para:', this.apiUrl);
    console.log('Idioma selecionado:', language);
    
    // Obtenha o token do localStorage
    const token = localStorage.getItem('token');
    console.log('Token usado na requisição:', token?.substring(0, 20) + '...');
    
    // Configure os headers com o token
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      'Accept-Language': language // Adiciona o idioma no header
    });
    
    // Adiciona o idioma no corpo da requisição também
    // (alguns backends podem preferir um ou outro método)
    const payload = {
      query: query,
      language: language
    };
    
    // Envie a requisição com os headers
    return this.http.post<ApiResponse>(this.apiUrl, payload, { headers })
      .pipe(
        catchError(this.handleError)
      );
  }

  private handleError(error: any) {
    console.log('Resposta de erro completa:', error);
    let errorMsg = 'Erro desconhecido';
    if (error.error && error.error.detail) {
      errorMsg = `Erro na API: ${error.error.detail}`;
    } else if (error.status) {
      errorMsg = `Erro na API: Código: ${error.status}, Mensagem: ${error.message}`;
    }
    return throwError(() => errorMsg);
  }
} 