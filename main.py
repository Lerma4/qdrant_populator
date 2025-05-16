import json
import uuid
from openai import OpenAI
from qdrant_client import QdrantClient, models

# Importa la configurazione
import config

def get_openai_embedding(text: str, client: OpenAI, model: str = config.EMBEDDING_MODEL):
    """Genera l'embedding per un dato testo usando OpenAI."""
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

def main():
    """Funzione principale per popolare Qdrant."""
    # Inizializza il client di OpenAI
    try:
        openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
    except Exception as e:
        print(f"Errore durante l'inizializzazione del client OpenAI: {e}")
        print("Assicurati di aver impostato correttamente la variabile OPENAI_API_KEY nel file config.py")
        return

    # Inizializza il client di Qdrant
    try:
        qdrant_client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
    except Exception as e:
        print(f"Errore durante la connessione a Qdrant ({config.QDRANT_HOST}:{config.QDRANT_PORT}): {e}")
        print("Assicurati che Qdrant sia in esecuzione e raggiungibile.")
        return

    # Verifica e crea la collezione se non esiste
    try:
        collections = qdrant_client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        if config.COLLECTION_NAME not in collection_names:
            print(f"Collezione '{config.COLLECTION_NAME}' non trovata. Creazione in corso...")
            vector_size = config.VECTOR_SIZE
            qdrant_client.recreate_collection(
                collection_name=config.COLLECTION_NAME,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
            )
            print(f"Collezione '{config.COLLECTION_NAME}' creata con successo.")
        else:
            print(f"Collezione '{config.COLLECTION_NAME}' trovata.")
    except Exception as e:
        print(f"Errore durante la gestione della collezione Qdrant: {e}")
        return

    # Carica i dati dal file JSON
    try:
        with open(config.JSON_INPUT_FILE, 'r', encoding='utf-8') as f:
            data_to_populate = json.load(f)
    except FileNotFoundError:
        print(f"Errore: File JSON di input '{config.JSON_INPUT_FILE}' non trovato.")
        return
    except json.JSONDecodeError:
        print(f"Errore: Il file '{config.JSON_INPUT_FILE}' non contiene JSON valido.")
        return
    except Exception as e:
        print(f"Errore durante la lettura del file JSON: {e}")
        return

    if not data_to_populate:
        print(f"Nessun dato da processare nel file '{config.JSON_INPUT_FILE}'.")
        return

    print(f"Inizio popolamento di Qdrant con i dati da '{config.JSON_INPUT_FILE}'...")
    points_to_upsert = []
    for i, item in enumerate(data_to_populate):
        try:
            text_to_embed = item.get("text")
            if not text_to_embed:
                print(f"Attenzione: l'elemento {i+1} non ha un campo 'text'. Salto.")
                continue

            print(f"Processo l'elemento {i+1}/{len(data_to_populate)}: Generazione embedding per '{text_to_embed[:50]}...'" )
            vector = get_openai_embedding(text_to_embed, openai_client)

            payload = item.get("metadata", {})

            # Usa l'ID fornito nel JSON se presente e valido, altrimenti genera un UUID
            item_id_val = item.get("id") # Rinomino per chiarezza, per non confondere con point_id finale

            # Controlla se l'ID fornito è valido (int non negativo o stringa non vuota)
            # o se deve essere generato un UUID.
            generate_uuid = True # Flag per decidere se generare un UUID
            if isinstance(item_id_val, int):
                if item_id_val >= 0: # Qdrant specifica "unsigned integer"
                    point_id = item_id_val # Passa come intero, non come stringa
                    generate_uuid = False
                    print(f"  ID numerico fornito ({item_id_val}), passato come intero: {point_id}")
                else:
                    print(f"  ID intero fornito ({item_id_val}) è negativo. Non valido per Qdrant (richiede unsigned).")
            elif isinstance(item_id_val, str):
                item_id_stripped = item_id_val.strip()
                if item_id_stripped:
                    point_id = item_id_stripped
                    generate_uuid = False
                    print(f"  ID stringa valido fornito: {point_id}")
                else:
                    print(f"  ID stringa fornito è vuoto/spazi.")
            elif item_id_val is None:
                print(f"  ID non fornito.")
            else:
                print(f"  ID fornito di tipo non valido ({type(item_id_val).__name__}).")

            if generate_uuid:
                point_id = str(uuid.uuid4())
                print(f"  Generato nuovo ID (UUID): {point_id}")
            # A questo punto, point_id è o un int >= 0, o una stringa non vuota, o un UUID (stringa).

            # Passa l'ID come intero se è un int, altrimenti come stringa
            points_to_upsert.append(models.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            ))
            print(f"  Elemento {i+1} preparato con ID: {point_id}")

        except Exception as e:
            print(f"Errore durante il processamento dell'elemento {i+1} ('{item.get('id', 'N/A')}'): {e}")
            print(f"  Dettagli elemento: {item}")
            continue # Continua con il prossimo elemento

    # Inserisci i punti in Qdrant (in batch se BATCH_SIZE è configurato e implementato)
    if points_to_upsert:
        try:
            batch_size = getattr(config, 'BATCH_SIZE', len(points_to_upsert))
            for i in range(0, len(points_to_upsert), batch_size):
                batch = points_to_upsert[i:i + batch_size]
                qdrant_client.upsert(collection_name=config.COLLECTION_NAME, points=batch)
                print(f"Inseriti {len(batch)} punti nel batch {i // batch_size + 1}")
            print(f"\nInseriti con successo {len(points_to_upsert)} punti nella collezione '{config.COLLECTION_NAME}'.")
        except Exception as e:
            print(f"Errore durante l'inserimento dei punti in Qdrant: {e}")
    else:
        print("Nessun punto valido da inserire in Qdrant.")

    print("Processo di popolamento completato.")

if __name__ == "__main__":
    main()