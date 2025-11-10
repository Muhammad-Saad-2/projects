from app.utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Vector store initialized.")
logger.warning("Embedding failed — retrying...")
logger.error("FAISS index not found!")
