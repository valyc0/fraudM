import os
import time
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from opensearchpy import OpenSearch, ConnectionError, RequestError, NotFoundError
from ..models import Rule, RuleUpdate

logger = logging.getLogger(__name__)

class OpenSearchService:
    def __init__(self):
        self.max_retries = 5
        self.retry_delay = 5  # seconds
        self.index = "rules"
        
        # Get configuration from environment
        self.host = os.getenv('OPENSEARCH_HOST', 'opensearch')
        self.port = int(os.getenv('OPENSEARCH_PORT', '9200'))
        self.user = os.getenv('OPENSEARCH_USER', 'admin')
        self.password = os.getenv('OPENSEARCH_PASSWORD', 'admin')
        
        # Initialize client with retries
        self.client = self._initialize_client()
        self._ensure_index()

    def _initialize_client(self) -> OpenSearch:
        """Initialize OpenSearch client with retry logic"""
        for attempt in range(self.max_retries):
            try:
                client = OpenSearch(
                    hosts=[{'host': self.host, 'port': self.port}],
                    http_auth=(self.user, self.password),
                    use_ssl=False,   # Disabled for development
                    verify_certs=False,
                    ssl_show_warn=False,
                    retry_on_timeout=True,
                    max_retries=3
                )
                # Test connection
                client.info()
                logger.info(f"Successfully connected to OpenSearch at {self.host}:{self.port}")
                return client
            except ConnectionError as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Failed to connect to OpenSearch (attempt {attempt + 1}/{self.max_retries}). Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Failed to connect to OpenSearch after multiple attempts")
                    raise Exception(f"Could not connect to OpenSearch: {str(e)}")

    def _ensure_index(self):
        """Ensure the rules index exists with correct mappings"""
        try:
            if not self.client.indices.exists(index=self.index):
                mappings = {
                    "properties": {
                        "rule_id": {"type": "keyword"},
                        "name": {"type": "text"},
                        "natural_language": {"type": "text"},
                        "scala_code": {"type": "text"},
                        "status": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"},
                        "deployed_at": {"type": "date"},
                        "version": {"type": "integer"},
                        "is_active": {"type": "boolean"}
                    }
                }
                
                self.client.indices.create(
                    index=self.index,
                    body={"mappings": mappings}
                )
                logger.info(f"Created index '{self.index}' with mappings")
        except Exception as e:
            logger.error(f"Error ensuring index existence: {str(e)}")
            raise

    async def store_rule(self, rule: Rule) -> Rule:
        """Store a new rule in OpenSearch"""
        try:
            document = rule.model_dump()
            response = self.client.index(
                index=self.index,
                body=document,
                id=rule.rule_id,
                refresh=True
            )
            
            if response['result'] not in ['created', 'updated']:
                raise Exception("Failed to store rule in OpenSearch")
            
            logger.info(f"Successfully stored rule {rule.rule_id}")
            return rule
        except Exception as e:
            logger.error(f"Error storing rule: {str(e)}")
            raise

    async def get_rule(self, rule_id: str) -> Optional[Rule]:
        """Retrieve a rule by ID"""
        try:
            response = self.client.get(
                index=self.index,
                id=rule_id
            )
            return Rule(**response['_source'])
        except NotFoundError:
            logger.warning(f"Rule {rule_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving rule {rule_id}: {str(e)}")
            return None

    async def list_rules(self) -> List[Rule]:
        """List all rules"""
        try:
            response = self.client.search(
                index=self.index,
                body={
                    "query": {"match_all": {}},
                    "sort": [{"created_at": {"order": "desc"}}]
                },
                size=100  # Adjust as needed
            )
            
            rules = []
            for hit in response['hits']['hits']:
                rules.append(Rule(**hit['_source']))
            
            return rules
        except Exception as e:
            logger.error(f"Error listing rules: {str(e)}")
            raise

    async def update_rule(self, rule_id: str, rule_update: RuleUpdate, scala_code: Optional[str] = None) -> Optional[Rule]:
        """Update an existing rule"""
        try:
            existing_rule = await self.get_rule(rule_id)
            if not existing_rule:
                logger.warning(f"Rule {rule_id} not found for update")
                return None

            # Prepare update data
            update_data = rule_update.model_dump(exclude_unset=True)
            update_data['updated_at'] = datetime.now()
            
            if scala_code:
                update_data['scala_code'] = scala_code
                update_data['version'] = existing_rule.version + 1

            # Update in OpenSearch
            response = self.client.update(
                index=self.index,
                id=rule_id,
                body={"doc": update_data},
                refresh=True
            )

            if response['result'] != 'updated':
                raise Exception("Failed to update rule in OpenSearch")

            logger.info(f"Successfully updated rule {rule_id}")
            return await self.get_rule(rule_id)
        except Exception as e:
            logger.error(f"Error updating rule {rule_id}: {str(e)}")
            raise

    async def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule"""
        try:
            response = self.client.delete(
                index=self.index,
                id=rule_id,
                refresh=True
            )
            success = response['result'] == 'deleted'
            if success:
                logger.info(f"Successfully deleted rule {rule_id}")
            return success
        except NotFoundError:
            logger.warning(f"Rule {rule_id} not found for deletion")
            return False
        except Exception as e:
            logger.error(f"Error deleting rule {rule_id}: {str(e)}")
            return False

    async def update_rule_status(self, rule_id: str, status: str) -> Optional[Rule]:
        """Update rule status"""
        try:
            now = datetime.now().isoformat()
            update_body = {
                "doc": {
                    "status": status,
                    "updated_at": now,
                    **({"deployed_at": now} if status == "deployed" else {})
                }
            }
            
            response = self.client.update(
                index=self.index,
                id=rule_id,
                body=update_body,
                refresh=True
            )
            
            if response['result'] == 'updated':
                logger.info(f"Successfully updated status to '{status}' for rule {rule_id}")
                return await self.get_rule(rule_id)
            return None
        except NotFoundError:
            logger.warning(f"Rule {rule_id} not found for status update")
            return None
        except Exception as e:
            logger.error(f"Error updating status for rule {rule_id}: {str(e)}")
            return None

    async def check_health(self) -> bool:
        """Check if OpenSearch is healthy and accessible"""
        try:
            self.client.info()
            return True
        except Exception as e:
            logger.error(f"OpenSearch health check failed: {str(e)}")
            return False