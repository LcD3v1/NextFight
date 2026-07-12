# Motor de Previsão

## MVP

Começar com regras determinísticas, não machine learning.

## Saída

- horário previsto;
- início mais cedo;
- início mais tarde;
- confiança de 0 a 1;
- fatores utilizados;
- versão do modelo.

## Fatores iniciais

- quantidade de lutas restantes;
- duração máxima das lutas;
- média histórica da organização;
- média de intervalo entre lutas;
- status e round da luta atual;
- posição no card;
- tipo de evento;
- atrasos observados no evento atual.

## Recalcular quando

- evento inicia;
- luta inicia;
- round muda;
- luta termina;
- card é reordenado;
- evento entra em pausa;
- operador corrige o estado.

## Confiança

A confiança deve diminuir quando:

- há muitas lutas restantes;
- o provedor está atrasado;
- o evento está pausado;
- o card muda;
- há dados incompletos.

## Evolução

Após acumular histórico suficiente, treinar modelos supervisionados para estimar duração e intervalo, preservando fallback determinístico.
