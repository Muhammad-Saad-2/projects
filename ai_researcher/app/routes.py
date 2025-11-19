from fastapi import  APIRouter, HTTPException
from app.schemas import QueryRequest, QueryResponse 
from app.utils.logger import get_logger
from app.services.rag_service import RAGService

DEFAULT_SIMILARITY_THRESHOLD = 0.4

router = APIRouter()
logger = get_logger(__name__)
rag_service = RAGService()


@router.post("/query", response_model = QueryResponse)


async def query_knowledge(request: QueryRequest):

    threshold_value = request.similarity_threshold
    if threshold_value == None:
        threshold_value = DEFAULT_SIMILARITY_THRESHOLD

    try:
        logger.info(f"Recieved your Query : {request.query}")
        result = rag_service.query_knowledge(
            query=request.query,
            similarity_threshold=threshold_value,
            top_k=request.top_k
        )

        # if result["status"] != "success":
        #     raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    
    except Exception as e:
        logger.exception(f"❎ error while processing a query request")
        raise HTTPException(status_code=500, detail=str(e))
    




