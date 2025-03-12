import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

// Interface para a resposta da API de login
interface LoginResponse {
  access: string;
  refresh?: string;
  username?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = '/api';
  
  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/login/`, { username, password }).pipe(
      tap(response => {
        console.log('Resposta de login:', response);
        localStorage.setItem('token', response.access);
        localStorage.setItem('isLoggedIn', 'true');
        console.log('Token armazenado:', this.getToken());
      })
    );
  }

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('isLoggedIn');
  }

  isLoggedIn(): boolean {
    return localStorage.getItem('isLoggedIn') === 'true';
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }
} 