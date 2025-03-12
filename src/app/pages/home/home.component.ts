import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div>
      <h1>Home Component</h1>
      <p>Esta é a página inicial</p>
    </div>
  `,
  styles: []
})
export class HomeComponent {
} 