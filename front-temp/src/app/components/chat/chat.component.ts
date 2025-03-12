import { Component, OnInit, ViewChild, ElementRef, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../services/chat.service';
import { LanguageService } from '../../services/language.service';
import { LanguageSelectorComponent } from '../language-selector/language-selector.component';
import { TranslatePipe } from '../../pipes/translate.pipe';
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
    FormsModule,
    LanguageSelectorComponent,
    TranslatePipe
  ]
})
export class ChatComponent implements OnInit, OnDestroy {
  @ViewChild('messageContainer') private messageContainer!: ElementRef;
  
  messages: ChatMessage[] = [];
  inputMessage: string = '';
  isLoading: boolean = false;
  private destroy$ = new Subject<void>();

  constructor(
    private chatService: ChatService,
    private languageService: LanguageService
  ) {
    marked.setOptions({
      breaks: true,
      gfm: true
    });
  }

  async ngOnInit() {
    // Obter a saudação traduzida de forma assíncrona
    const greeting = await this.languageService.translate('app.chat.greeting');
    this.addBotMessage(greeting);
    
    // Atualizar mensagem de boas-vindas quando o idioma mudar
    this.languageService.currentLanguage$.subscribe(async () => {
      if (this.messages.length === 1) {
        this.messages[0].content = await this.languageService.translate('app.chat.greeting');
      }
    });
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

    // Obtém o idioma atual
    const currentLanguage = this.languageService.getCurrentLanguage();
    
    this.chatService.askManual(messageToSend, currentLanguage)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: async (response) => {
          const formattedContent = marked(response.answer);
          await this.addBotMessage(formattedContent, response.references);
        },
        error: async (error) => {
          const errorMsg = await this.languageService.translate('app.chat.error');
          this.addErrorMessage(errorMsg);
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
    this.scrollToBottom();
  }

  private addErrorMessage(content: string) {
    this.messages.push({
      content,
      type: 'error',
      timestamp: new Date()
    });
    this.scrollToBottom();
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