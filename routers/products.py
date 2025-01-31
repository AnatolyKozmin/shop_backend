import sys
import os
sys.path.append(os.getcwd())

from fastapi import APIRouter, Depends, status, HTTPException
#from sqlalchemy.orm import Session  нужно для неасинхронных запросов
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import insert
from sqlalchemy import update

from typing import Annotated
from slugify import slugify

from app.backend.dp_depends import get_db
from app.models.products import Product
from app.models.category import Category
from app.schemas import CreateProduct
from app.routers.auth import get_current_user




router = APIRouter(prefix='/products', tags=['products'])



@router.get('/')
async def all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(select(Product).where(Product.is_active == True, Product.stock > 0)).all()
    if products is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no product'
        )
    return products.all() # Посмотреть в коде 




@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_product(db: Annotated[AsyncSession, Depends(get_db)], create_product: CreateProduct, 
                         get_user: Annotated[dict, Depends(get_current_user)]):
    
    if get_user.get('is_admin') or get_user.get('is_supplier'):

        category = await db.scalar(select(Category).where(Category.id == create_product.category))
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no category found'
            )
        
        db.execute(insert(Product).values(name=create_product.name,
                                        description=create_product.description,
                                        price=create_product.price,
                                        image_url=create_product.image_url,
                                        stock=create_product.stock,
                                        category_id=create_product.category,
                                        rating=0.0,
                                        supplier_id=get_user.get('id'),
                                        slug=slugify(create_product.name)
                                        ))
        
        await db.commit()

        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be authorizate for this method'
        )

                                      
    

@router.get('/{category_slug}')
async def product_by_category(db: Annotated[AsyncSession, Depends(get_db)] ,category_slug: str):
    category = await db.scalar(select(Category).where(Category.slug == category_slug))
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail='File Not Found')
    
    subcategory = await db.scalars(select(Category.parent_id == category.id)).all()
    categories_and_subcategories = [category.id] + [i.id for i in subcategory.all()]
    products_category = await db.scalars(
                            select(Product).where(Product.category_id.in_(categories_and_subcategories), Product.is_active == True, 
                                                    Product.stock > 0))
    return products_category.all()


@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(
                        select(Product).where(Product.slug == product_slug, Product.is_active == True, Product.stock > 0))
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='File Not Found')
    return product


@router.put('/detail/{product_slug}')
async def update_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str,
                         update_product_model: CreateProduct, get_user: Annotated[dict, Depends(get_current_user)]):
    product_update = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no found product'
        )
    if get_user.get('is_supplier') or get_user.get('is_admin'):
        if get_user.get('id') == product_update.supplier_id or get_user.get('is_admin'):
            await db.execute(
                update(Product).where(Product.slug == product_slug)
                .values(name=update_product_model.name,
                        description=update_product_model.description,
                        price=update_product_model.price,
                        image_url=update_product_model.image_url,
                        stock=update_product_model.stock,
                        category_id=update_product_model.category,
                        slug=slugify())
            )
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'detail': 'Product update is successful !'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not authorized to use this method'
            )
    else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not authorized to use this method'
            )



@router.delete('/')
async def delete_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    product_delete = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product_delete is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
             )
    if get_user.get('is_supplier') or get_user.get('is_admin'):
        if get_user.get('id') == product_delete.supplier_id or get_user.get('is_admin'):
            product_delete.is_active = False
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Product delete is successful'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You have not enough permission for this action'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not enough permission for this action'
        )
