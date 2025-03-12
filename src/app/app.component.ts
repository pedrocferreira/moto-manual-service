import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ChatComponent } from './chat/chat.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule, ChatComponent],
  template: `
    <router-outlet></router-outlet>
    <app-chat></app-chat>
  `,
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'seu-projeto';
} 