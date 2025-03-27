# Rule Template Design

## Overview
Per rendere la generazione del codice più affidabile e standardizzata, introdurremo un sistema basato su template per le regole Scala. Invece di generare l'intero codice con l'AI, useremo un template base che include tutte le parti critiche e configurazioni, lasciando all'AI solo la generazione della logica specifica della regola.

## Template Structure

### 1. Base Template Components
- Import delle librerie necessarie
- Configurazioni per input Kafka (bootstrap servers, topic, etc)
- Configurazioni per output Kafka 
- Configurazioni per OpenSearch
- Setup base dello stream processing
- Placeholder per la logica della regola
- Output handling per alert e logging

### 2. Template Personalization
- L'AI genererà solo la parte della logica della regola
- Il sistema farà il merge della logica generata nel placeholder [RULE_LOGIC]
- Il nome della classe verrà automaticamente generato dalla descrizione della regola

## Implementation Steps

1. Creare la directory `app/templates/` con due file:
   - `base_template.scala`: template base con le parti fisse
   - `pattern_templates.scala`: modelli comuni di pattern di frode

2. Modificare AIService per:
   - Utilizzare il template base
   - Generare solo la logica della regola
   - Fare il merge con il template base utilizzando il placeholder
   - Salvare il file risultante in app/scala/
   - Gestire errori di generazione o merge

3. Aggiungere logging e validazione per:
   - Verifica della sintassi del codice generato
   - Controllo della presenza di tutte le parti necessarie
   - Log degli errori di generazione

## Benefits
1. Configurazioni standardizzate e sicure
2. Codice più affidabile
3. Minor rischio di errori nella generazione
4. Manutenzione più semplice
5. Migliore gestione delle dipendenze

## Next Steps
1. Implementare la struttura dei template
2. Modificare AIService per utilizzare il nuovo approccio
3. Aggiungere validazione e logging
4. Testare con vari tipi di regole