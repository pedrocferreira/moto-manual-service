import { Component, OnInit, ViewChild, ElementRef, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../services/chat.service';
import { ChatMessage } from '../../models/chat.model'
import { marked } from 'marked';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ]
})
export class ChatComponent implements OnInit, OnDestroy {
  @ViewChild('messageContainer') private messageContainer!: ElementRef;
  
  messages: ChatMessage[] = [];
  inputMessage: string = '';
  isLoading: boolean = false;
  private destroy$ = new Subject<void>();

  constructor(private chatService: ChatService) {
    marked.setOptions({
      breaks: true,
      gfm: true
    });
  }

  ngOnInit() {
    this.addBotMessage('Olá! Sou seu assistente especializado em mecânica de motos. Como posso ajudar?');
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  async sendMessage() {
    if (!this.inputMessage.trim() || this.isLoading) return;

    this.addUserMessage(this.inputMessage);
    const messageToSend = this.inputMessage;
    this.inputMessage = '';
    this.isLoading = true;

    this.chatService.askManual(messageToSend)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: async (response) => {
          const formattedContent = marked(response.answer);
          await this.addBotMessage(formattedContent, response.references);
        },
        error: (error) => {
          this.addErrorMessage('Desculpe, ocorreu um erro ao processar sua mensagem.');
          console.error('Erro na API:', error);
        },
        complete: () => {
          this.isLoading = false;
          this.scrollToBottom();
        }
      });
  }

  private addUserMessage(content: string) {
    this.messages.push({
      content,
      type: 'user',
      timestamp: new Date()
    });
    this.scrollToBottom();
  }

  async addBotMessage(content: string | Promise<string>, references?: string[]) {
    const resolvedContent = await Promise.resolve(content);
    this.messages.push({
      content: resolvedContent,
      type: 'bot',
      timestamp: new Date(),
      references
    });
  }

  private addErrorMessage(content: string) {
    this.messages.push({
      content,
      type: 'error',
      timestamp: new Date()
    });
  }

  private scrollToBottom() {
    setTimeout(() => {
      const element = this.messageContainer.nativeElement;
      element.scrollTop = element.scrollHeight;
    });
  }

  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }
} 