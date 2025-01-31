import sys
import os
sys.path.append(os.getcwd())

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select 
from sqlalchemy import insert 
from sqlalchemy import update 
from typing import Annotated
from datetime import datetime

from app.backend.dp_depends import get_db
from app.models.category import Category
from app.models.products import Product
from app.models.raiting import Raiting
from app.models.reviews import Review
from app.schemas import CreateRewiev
from app.schemas import CreateRaiting
from app.routers.auth import get_current_user


router = APIRouter(prefix='/reviews', tags=['reviews'])
@router.get('/')
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Review).where(Review.is_active == True))
    if reviews is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no reviews !'
        )

    return reviews.all()

@router.get('/detail/{product_slug}')
async def product_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug, Product.is_active ==True))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product is Not Find'
        )

    reviews = await db.scalars(select(Review).where(Review.product_id == product.id, Review.is_active == True))
    raitings = await db.scalars(select(Raiting).where(Raiting.product_id ==product.id))
    raiting = sum([raiting for raiting in raitings.all()]) // len(raitings)
    return {'Reviews': reviews.all(),
            'Raiting': raiting}

@router.post('/', status_code=status.HTTP_200_OK)
async def create_review(db: Annotated[AsyncSession, Depends(get_db)], 
                        get_user: Annotated[dict, Depends(get_current_user)],
                        create_review: CreateRewiev,
                        create_raiting: CreateRaiting):
    product = await db.scalar(select(Product).where(Product.id == create_review.product))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product Not Found'
        )
    await db.execute(insert(Review).values(
        comment=create_review.comment,
        raiting=create_review.raiting,
        comment_date=create_review.datetime.now(),
        user_id=get_user.get('id'),
        product_id=product.id,))
        #raiting=create_review.raiting,))

    await db.execute(insert(Raiting).values(
        grade=create_raiting.grade,
        user_id=create_raiting.get_user('id'),
        product_id=create_raiting.product.id,
    ))

    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction_1': 'Create reviews is successful !',
        'transaction_2': 'Create raiting is successful !'
    }

@router.delete('/')
async def delete_reviews(db: Annotated[AsyncSession, Depends(get_db)], 
                         reviews_id: int,
                         get_user: Annotated[AsyncSession, Depends(get_current_user)]):
    review = await db.scalar(select(Review).where(Review.id == reviews_id))
    if review is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no reviews'
        )

    if get_user.get('is_supplier') or get_user.get('is_admin'):
        if get_user.get('id') == review.user_id or get_user.get('is_admin'):
            review.is_active = False
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transacrion': 'Reviews delete is Successful !'
            }
        else: 
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You have not permission for this action'
            )
    else: 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not permission for this action'
        )