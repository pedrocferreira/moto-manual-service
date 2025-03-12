import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="home-container">
      <h1>Bem-vindo ao Sistema de Consulta de Manuais</h1>
      <p>Esta é a página inicial do nosso sistema.</p>
      <div class="navigation">
        <a routerLink="/chat">Ir para o Chat</a>
        <a routerLink="/login">Login</a>
      </div>
    </div>
  `,
  styles: [`
    .home-container {
      padding: 20px;
      text-align: center;
    }
    .navigation {
      margin-top: 20px;
    }
    .navigation a {
      margin: 0 10px;
      padding: 10px 20px;
      background-color: #007bff;
      color: white;
      text-decoration: none;
      border-radius: 5px;
    }
    .navigation a:hover {
      background-color: #0056b3;
    }
  `]
})
export class HomeComponent {} 