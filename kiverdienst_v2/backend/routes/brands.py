"""
Brands management API routes
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from database import get_db
from models import Brand, Character, SystemLog

logger = logging.getLogger(__name__)
router = APIRouter()


class BrandCreate(BaseModel):
    """Request model for creating a brand"""
    name: str
    niche: Optional[str] = None
    tonality: Optional[str] = None
    target_audience: Optional[str] = None
    tiktok_account: Optional[str] = None
    instagram_account: Optional[str] = None
    youtube_account: Optional[str] = None


class BrandUpdate(BaseModel):
    """Request model for updating a brand"""
    name: Optional[str] = None
    niche: Optional[str] = None
    tonality: Optional[str] = None
    target_audience: Optional[str] = None
    tiktok_account: Optional[str] = None
    instagram_account: Optional[str] = None
    youtube_account: Optional[str] = None
    status: Optional[str] = None


class BrandResponse(BaseModel):
    """Response model for brand data"""
    id: int
    name: str
    niche: Optional[str]
    tonality: Optional[str]
    target_audience: Optional[str]
    tiktok_account: Optional[str]
    instagram_account: Optional[str]
    youtube_account: Optional[str]
    status: str
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[BrandResponse])
async def list_brands(
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    List all brands
    Supports filtering by status and pagination
    """
    try:
        query = db.query(Brand)
        
        # Filter by status if provided
        if status:
            query = query.filter(Brand.status == status)
        
        # Order by created date (newest first)
        query = query.order_by(desc(Brand.created_at))
        
        # Apply pagination
        brands = query.offset(skip).limit(limit).all()
        
        # Convert to response models
        return [
            BrandResponse(
                id=brand.id,
                name=brand.name,
                niche=brand.niche,
                tonality=brand.tonality,
                target_audience=brand.target_audience,
                tiktok_account=brand.tiktok_account,
                instagram_account=brand.instagram_account,
                youtube_account=brand.youtube_account,
                status=brand.status,
                created_at=str(brand.created_at),
                updated_at=str(brand.updated_at)
            )
            for brand in brands
        ]
    
    except Exception as e:
        logger.error(f"Error listing brands: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=BrandResponse)
async def create_brand(
    brand_data: BrandCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new brand
    """
    try:
        # Create new brand
        new_brand = Brand(
            name=brand_data.name,
            niche=brand_data.niche,
            tonality=brand_data.tonality,
            target_audience=brand_data.target_audience,
            tiktok_account=brand_data.tiktok_account,
            instagram_account=brand_data.instagram_account,
            youtube_account=brand_data.youtube_account,
            status='active'
        )
        
        db.add(new_brand)
        db.commit()
        db.refresh(new_brand)
        
        # Log creation
        log_entry = SystemLog(
            level="INFO",
            component="brands",
            message=f"Brand created: {brand_data.name}",
            brand_id=new_brand.id,
            details={"brand_id": new_brand.id, "name": brand_data.name}
        )
        db.add(log_entry)
        db.commit()
        
        logger.info(f"Brand created: {brand_data.name} (ID: {new_brand.id})")
        
        return BrandResponse(
            id=new_brand.id,
            name=new_brand.name,
            niche=new_brand.niche,
            tonality=new_brand.tonality,
            target_audience=new_brand.target_audience,
            tiktok_account=new_brand.tiktok_account,
            instagram_account=new_brand.instagram_account,
            youtube_account=new_brand.youtube_account,
            status=new_brand.status,
            created_at=str(new_brand.created_at),
            updated_at=str(new_brand.updated_at)
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating brand: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{brand_id}", response_model=BrandResponse)
async def get_brand(
    brand_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific brand by ID
    """
    try:
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        return BrandResponse(
            id=brand.id,
            name=brand.name,
            niche=brand.niche,
            tonality=brand.tonality,
            target_audience=brand.target_audience,
            tiktok_account=brand.tiktok_account,
            instagram_account=brand.instagram_account,
            youtube_account=brand.youtube_account,
            status=brand.status,
            created_at=str(brand.created_at),
            updated_at=str(brand.updated_at)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{brand_id}", response_model=BrandResponse)
async def update_brand(
    brand_id: int,
    brand_data: BrandUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a brand
    """
    try:
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        # Update fields if provided
        update_data = brand_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(brand, field, value)
        
        db.commit()
        db.refresh(brand)
        
        # Log update
        log_entry = SystemLog(
            level="INFO",
            component="brands",
            message=f"Brand updated: {brand.name}",
            brand_id=brand.id,
            details={"brand_id": brand.id, "updated_fields": list(update_data.keys())}
        )
        db.add(log_entry)
        db.commit()
        
        logger.info(f"Brand updated: {brand.name} (ID: {brand.id})")
        
        return BrandResponse(
            id=brand.id,
            name=brand.name,
            niche=brand.niche,
            tonality=brand.tonality,
            target_audience=brand.target_audience,
            tiktok_account=brand.tiktok_account,
            instagram_account=brand.instagram_account,
            youtube_account=brand.youtube_account,
            status=brand.status,
            created_at=str(brand.created_at),
            updated_at=str(brand.updated_at)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{brand_id}")
async def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a brand
    This will cascade delete all related data
    """
    try:
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        brand_name = brand.name
        
        # Log deletion
        log_entry = SystemLog(
            level="WARNING",
            component="brands",
            message=f"Brand deleted: {brand_name}",
            details={"brand_id": brand_id, "name": brand_name}
        )
        db.add(log_entry)
        
        # Delete brand (cascade will handle related data)
        db.delete(brand)
        db.commit()
        
        logger.info(f"Brand deleted: {brand_name} (ID: {brand_id})")
        
        return {
            "success": True,
            "message": f"Brand '{brand_name}' deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{brand_id}/status")
async def toggle_brand_status(
    brand_id: int,
    db: Session = Depends(get_db)
):
    """
    Toggle brand status between active and paused
    """
    try:
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        # Toggle status
        new_status = 'paused' if brand.status == 'active' else 'active'
        brand.status = new_status
        
        db.commit()
        db.refresh(brand)
        
        # Log status change
        log_entry = SystemLog(
            level="INFO",
            component="brands",
            message=f"Brand status changed: {brand.name}",
            brand_id=brand.id,
            details={
                "brand_id": brand.id,
                "new_status": new_status
            }
        )
        db.add(log_entry)
        db.commit()
        
        logger.info(f"Brand status changed: {brand.name} -> {new_status}")
        
        return {
            "success": True,
            "brand_id": brand.id,
            "status": new_status,
            "message": f"Brand is now {new_status}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error toggling brand status {brand_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{brand_id}/stats")
async def get_brand_stats(
    brand_id: int,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific brand
    """
    try:
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        # Count related entities
        characters_count = len(brand.characters)
        scripts_count = len(brand.video_scripts)
        videos_count = len(brand.videos)
        schedules_count = len(brand.posting_schedules)
        
        return {
            "brand_id": brand.id,
            "brand_name": brand.name,
            "characters": characters_count,
            "scripts": scripts_count,
            "videos": videos_count,
            "schedules": schedules_count,
            "status": brand.status
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting brand stats {brand_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
