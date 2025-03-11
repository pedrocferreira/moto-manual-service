import { Component, OnInit, ViewChild, ElementRef, OnDestroy } from '@angular/core';
import { ChatService } from '../../../../../front-temp/src/app/services/chat.servicep/services/chat.service';
import { ChatMessage } from '../../../../../front-temp/src/app/models/chat.modelc/app/models/chat.model';
import { marked } from 'marked';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent implements OnInit, OnDestroy {
  @ViewChild('messageContainer') private messageContainer: ElementRef;
  
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
        next: (response) => {
          const formattedContent = marked(response.answer);
          this.addBotMessage(formattedContent, response.references);
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

  private addBotMessage(content: string, references?: string[]) {
    this.messages.push({
      content,
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