# PRD — Product Requirements Document

## 1. Produto

**Nome:** NextFight  
**Categoria:** Esportes, alertas e acompanhamento ao vivo  
**Plataformas:** iOS, Android e painel web administrativo

## 2. Problema

Eventos de MMA e boxe possuem horários imprevisíveis. O usuário conhece o horário do card, mas raramente sabe quando uma luta específica realmente começará. Nocautes, decisões, intervalos comerciais, mudanças no card e atrasos alteram continuamente a programação.

## 3. Solução

O NextFight acompanha o andamento real do evento, identifica a luta atual, estima o início das próximas lutas e envia alertas inteligentes configuráveis.

## 4. Proposta de valor

> Escolha a luta. O NextFight acompanha o evento por você.

## 5. Público-alvo

- Fãs casuais que querem assistir apenas às lutas principais.
- Fãs dedicados que acompanham cards completos.
- Usuários em fusos horários diferentes.
- Apostadores que precisam acompanhar eventos ativos.
- Equipes, academias, atletas e criadores de conteúdo.

## 6. Escopo do MVP

### Usuário

- Cadastro, login e recuperação de senha.
- Perfil, idioma e fuso horário.
- Lista de eventos futuros e ativos.
- Página do evento com card ordenado.
- Página da luta.
- Favoritar eventos, organizações e atletas.
- Criar alerta para uma luta.
- Receber notificações de mudança de card.
- Receber alerta quando a luta estiver próxima.
- Histórico de alertas.

### Evento ao vivo

- Status do evento.
- Luta atual.
- Luta anterior e próxima luta.
- Timeline do card.
- Previsão de início.
- Nível de confiança da previsão.
- Atualizações em tempo real.

### Administração

- Criar e editar organizações, eventos, atletas e lutas.
- Importar dados de provedor externo.
- Corrigir ordem do card.
- Alterar status de evento e luta.
- Disparar alerta manual.
- Visualizar logs e falhas de entrega.
- Acompanhar usuários e assinaturas.

## 7. Fora do MVP

- Chat público.
- Fantasy completo.
- Apostas com dinheiro real.
- Streaming próprio.
- Marketplace.
- Rede social completa.
- Inteligência artificial avançada treinada com grande volume de dados.

## 8. Requisitos funcionais principais

### RF-001 Autenticação
O usuário deve criar conta com e-mail e senha, entrar, sair e recuperar acesso.

### RF-002 Eventos
O sistema deve exibir eventos por data, organização e status.

### RF-003 Card
O sistema deve exibir a ordem atual das lutas e refletir mudanças.

### RF-004 Alertas
O usuário deve configurar alertas por luta e antecedência.

### RF-005 Monitoramento
O sistema deve identificar o progresso do card.

### RF-006 Previsão
O sistema deve calcular uma janela provável de início e um score de confiança.

### RF-007 Realtime
Atualizações relevantes devem chegar ao aplicativo sem atualização manual.

### RF-008 Administração
Operadores devem corrigir dados ao vivo com auditoria.

## 9. Requisitos não funcionais

- Disponibilidade inicial alvo: 99,5%.
- Atualizações ao vivo com atraso alvo inferior a 10 segundos após entrada do dado.
- APIs comuns com p95 inferior a 500 ms.
- Suporte inicial a português e inglês.
- Compatibilidade com leitores de tela e contraste adequado.
- Criptografia em trânsito e em repouso quando disponível.
- Logs estruturados e rastreabilidade por request ID.

## 10. Critérios de sucesso do MVP

- Usuário consegue criar alerta em menos de 60 segundos.
- Pelo menos 95% dos alertas disparados pelo backend são aceitos pelo provedor push.
- Operador consegue corrigir o estado de um evento em menos de 30 segundos.
- Nenhum alerta é enviado duas vezes pela mesma transição.
- O sistema preserva histórico de mudanças de card.

## 11. Métricas

- Ativação: primeiro alerta criado.
- Retenção D1, D7 e D30.
- Eventos seguidos por usuário.
- Alertas criados e entregues.
- Taxa de abertura da notificação.
- Erro médio de previsão.
- Conversão para premium.
- Churn mensal.

## 12. Monetização inicial

### Gratuito
- Eventos e cards.
- Quantidade limitada de alertas.
- Publicidade opcional futura.

### Premium
- Alertas ilimitados.
- Múltiplos alertas por luta.
- Histórico completo.
- Widgets e Live Activities quando disponíveis.
- Experiência sem anúncios.

## 13. Riscos

- Dados ao vivo inconsistentes.
- Restrições de notificação em iOS.
- Mudanças de card não informadas rapidamente.
- Dependência excessiva de um único provedor.
- Prometer precisão superior ao que os dados permitem.

## 14. Estratégia de redução de risco

- Sistema híbrido automático + operador humano.
- Provedor primário e possibilidade de fonte secundária.
- Alertas baseados em estados, não apenas horário exato.
- Mensagens transparentes sobre nível de confiança.
