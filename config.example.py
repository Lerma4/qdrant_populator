# File di configurazione di esempio per Qdrant Populator

# Configurazione di Qdrant
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "nome_collezione"

# Configurazione di OpenAI
OPENAI_API_KEY = "INSERISCI_LA_TUA_API_KEY_OPENAI"
EMBEDDING_MODEL = "text-embedding-ada-002"

# Configurazione del file di input
JSON_INPUT_FILE = "data.json"

# Altri parametri
BATCH_SIZE = 100
# Vector size from OpenAI ada-002 model, 1536 for ada-002
VECTOR_SIZE = 1536