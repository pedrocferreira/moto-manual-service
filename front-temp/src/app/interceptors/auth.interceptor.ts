import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Obter o token do localStorage
    const token = localStorage.getItem('token');
    
    // Se não houver token, continue com a requisição original
    if (!token) {
      return next.handle(req);
    }
    
    // Clone a requisição e adicione o token de autorização
    const authReq = req.clone({
      headers: req.headers.set('Authorization', `Bearer ${token}`)
    });
    
    console.log('Interceptor adicionou token à requisição:', 
      req.url, 
      token.substring(0, 20) + '...');
    
    // Envie a requisição modificada
    return next.handle(authReq);
  }
} 