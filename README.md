# Qdrant Populator con OpenAI Embeddings

Questa applicazione Python popola un'istanza di Qdrant con dati provenienti da un file JSON, generando vettori di embedding utilizzando l'API di OpenAI.

## Prerequisiti

- Python 3.8 o superiore
- Un'istanza di Qdrant in esecuzione e accessibile.
- Una chiave API di OpenAI valida.

## Configurazione

1.  **Clona il repository (o scarica i file):**
    ```bash
    # Se fosse un repository git
    # git clone <url_del_repository>
    # cd qdrant-populator
    ```

2. **Preparazione del file di configurazione:**
   ```bash
   cp config.example.py config.py
   ```

2.  **Crea un ambiente virtuale (consigliato):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Su macOS/Linux
    # venv\Scripts\activate  # Su Windows
    ```

3.  **Installa le dipendenze:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configura i parametri:**
    Modifica il file `config.py` con i tuoi valori:
    -   `QDRANT_HOST`: L'host della tua istanza Qdrant (es. "localhost").
    -   `QDRANT_PORT`: La porta della tua istanza Qdrant (es. 6333).
    -   `COLLECTION_NAME`: Il nome della collezione che vuoi creare/usare in Qdrant.
    -   `OPENAI_API_KEY`: La tua chiave API di OpenAI. **Importante: non committare mai la tua chiave API in un repository pubblico.**
    -   `EMBEDDING_MODEL`: Il modello di embedding di OpenAI da utilizzare (es. "text-embedding-ada-002").
    -   `VECTOR_SIZE`: La dimensione del vettore per la collezione Qdrant (es. 1536 per "text-embedding-ada-002").
    -   `BATCH_SIZE`: (Opzionale) Numero di punti da inserire in ogni batch durante l'upsert su Qdrant.
    -   `JSON_INPUT_FILE`: Il percorso del file JSON contenente i dati da popolare (es. "data.json").

5.  **Prepara il file JSON di input:**
    Assicurati che il file specificato in `JSON_INPUT_FILE` (default: `data.json`) esista e sia formattato correttamente. Ogni oggetto nel JSON array dovrebbe avere almeno un campo "text" per la generazione dell'embedding. Puoi includere un campo "id" (stringa o intero) e un campo "metadata" (oggetto) per ogni elemento.

    Esempio di `data.json`:
    ```json
    [
      {
        "id": 1,
        "text": "Questo è il primo documento.",
        "metadata": {
          "source": "esempio",
          "category": "test"
        }
      },
      {
        "id": "doc-abc-123",
        "text": "Questo è il secondo documento con informazioni diverse.",
        "metadata": {
          "source": "esempio",
          "category": "prova"
        }
      }
    ]
    ```

## Esecuzione

Una volta configurato tutto, esegui lo script principale:

```bash
python main.py
```

Lo script si connetterà a Qdrant, creerà la collezione se non esiste, leggerà i dati dal file JSON, genererà gli embedding per ogni elemento testuale e inserirà i punti (ID, vettore, payload) nella collezione specificata. L'inserimento avviene in batch secondo il parametro `BATCH_SIZE`.

## Struttura del Progetto

-   `main.py`: Script principale che orchestra il processo di popolamento, gestendo la parametrizzazione della dimensione del vettore e il batching.
-   `config.py`: File di configurazione per i parametri variabili, inclusi `VECTOR_SIZE` e `BATCH_SIZE`.
-   `requirements.txt`: Elenco delle dipendenze Python.
-   `data.json` (esempio): File JSON di input con i dati da processare.
-   `README.md`: Questo file.
-   `.gitignore`: File di esclusione per i principali IDE e file temporanei.

## Note

-   **Gestione degli Errori**: Lo script include una gestione di base degli errori per la connessione a OpenAI e Qdrant, e per la lettura del file JSON.
-   **Dimensione dei Vettori**: La dimensione del vettore per la collezione Qdrant è ora parametrizzata tramite `VECTOR_SIZE` in `config.py`. Se usi un modello di embedding diverso, aggiorna questo parametro di conseguenza.
-   **Batching**: L'inserimento in Qdrant avviene in batch secondo il parametro `BATCH_SIZE` (configurabile). Questo migliora le prestazioni su dataset di grandi dimensioni.
-   **ID dei Punti**: Se un `id` non è fornito nel file JSON o non è valido, viene generato un UUID v4.
-   **.gitignore**: È presente un file `.gitignore` che esclude file e cartelle generate dai principali IDE e file temporanei, per mantenere pulito il repository.# qdrant_populator
