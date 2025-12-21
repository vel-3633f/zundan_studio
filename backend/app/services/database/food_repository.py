import logging
from typing import List, Dict, Optional
from datetime import datetime
from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class FoodRepository:
    """Repository for food data operations."""

    def __init__(self):
        self.client = get_supabase_client()
        self.table_name = "foods"

    def get_all_foods(self) -> List[Dict]:
        """Get all foods from database."""
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Failed to get foods: {e}")
            raise

    def add_food(self, name: str) -> Dict:
        """Add new food to database."""
        try:
            data = {
                "name": name,
                "is_generated": False,
            }
            response = self.client.table(self.table_name).insert(data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Failed to add food: {e}")
            raise

    def update_generation_status(
        self, food_id: str, is_generated: bool, video_info: Optional[str] = None
    ) -> Dict:
        """Update food generation status."""
        try:
            data = {
                "is_generated": is_generated,
                "updated_at": datetime.utcnow().isoformat(),
            }

            if is_generated:
                data["generated_at"] = datetime.utcnow().isoformat()
                if video_info:
                    data["video_info"] = video_info
            else:
                data["generated_at"] = None
                data["video_info"] = None

            response = (
                self.client.table(self.table_name)
                .update(data)
                .eq("id", food_id)
                .execute()
            )
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Failed to update generation status: {e}")
            raise

    def update_food_name(self, food_id: str, name: str) -> Dict:
        """Update food name."""
        try:
            data = {
                "name": name,
                "updated_at": datetime.utcnow().isoformat(),
            }
            response = (
                self.client.table(self.table_name)
                .update(data)
                .eq("id", food_id)
                .execute()
            )
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Failed to update food name: {e}")
            raise

    def delete_food(self, food_id: str) -> bool:
        """Delete food from database."""
        try:
            self.client.table(self.table_name).delete().eq("id", food_id).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to delete food: {e}")
            raise
