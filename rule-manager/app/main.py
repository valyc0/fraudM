import logging
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import os

from .services.ai_service import AIService
from .services.opensearch_service import OpenSearchService
from .models import Rule, RuleCreate, RuleUpdate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Rule Manager API")

# Initialize services
ai_service = None
opensearch_service = None

@app.on_event("startup")
async def startup_event():
    global ai_service, opensearch_service
    
    # Verify GEMINI_API_KEY is set
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    # Initialize services
    try:
        ai_service = AIService()
        opensearch_service = OpenSearchService()
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise

# Dependency to get services
async def get_services():
    if not ai_service or not opensearch_service:
        raise HTTPException(status_code=503, detail="Services not initialized")
    return {"ai": ai_service, "opensearch": opensearch_service}

@app.get("/health")
async def health_check(services: Dict = Depends(get_services)):
    """Check the health of all services"""
    try:
        ai_health = bool(services["ai"].api_key)
        opensearch_health = await services["opensearch"].check_health()
        
        return {
            "status": "healthy" if ai_health and opensearch_health else "unhealthy",
            "services": {
                "ai_service": "healthy" if ai_health else "unhealthy",
                "opensearch": "healthy" if opensearch_health else "unhealthy"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/rules/create")
async def create_rule(rule_create: RuleCreate, services: Dict = Depends(get_services)):
    try:
        logger.info(f"Creating new rule with description: {rule_create.description}")
        
        # Generate Scala code using AI
        scala_code = await services["ai"].generate_scala_code(rule_create.description)
        
        # Create rule document
        rule = Rule(
            rule_id=str(uuid.uuid4()),
            name=rule_create.name if rule_create.name else f"Rule_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            natural_language=rule_create.description,
            scala_code=scala_code,
            status="created",
            created_at=datetime.now(),
            version=1,
            is_active=False
        )
        
        # Store in OpenSearch
        stored_rule = await services["opensearch"].store_rule(rule)
        logger.info(f"Rule created successfully with ID: {stored_rule.rule_id}")
        
        return stored_rule
        
    except Exception as e:
        logger.error(f"Error creating rule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rules/{rule_id}")
async def get_rule(rule_id: str, services: Dict = Depends(get_services)):
    try:
        rule = await services["opensearch"].get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        return rule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving rule {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rules")
async def list_rules(services: Dict = Depends(get_services)):
    try:
        rules = await services["opensearch"].list_rules()
        return rules
    except Exception as e:
        logger.error(f"Error listing rules: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/rules/{rule_id}")
async def update_rule(rule_id: str, rule_update: RuleUpdate, services: Dict = Depends(get_services)):
    try:
        # Generate new Scala code if description is updated
        scala_code = None
        if rule_update.description:
            scala_code = await services["ai"].generate_scala_code(rule_update.description)
        
        rule = await services["opensearch"].update_rule(rule_id, rule_update, scala_code)
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        logger.info(f"Rule {rule_id} updated successfully")
        return rule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rule {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str, services: Dict = Depends(get_services)):
    try:
        success = await services["opensearch"].delete_rule(rule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        logger.info(f"Rule {rule_id} deleted successfully")
        return {"message": "Rule deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting rule {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rules/{rule_id}/deploy")
async def deploy_rule(rule_id: str, services: Dict = Depends(get_services)):
    try:
        rule = await services["opensearch"].get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        # TODO: Implement Flink deployment logic
        # This will be added in a separate service
        
        # Update rule status
        rule = await services["opensearch"].update_rule_status(rule_id, "deployed")
        logger.info(f"Rule {rule_id} marked as deployed")
        return rule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deploying rule {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)