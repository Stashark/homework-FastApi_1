import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Сервис объявлений")


class AdvertisementIn(BaseModel):
    title: str
    description: str
    price: float
    author: str


class AdvertisementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    author: Optional[str] = None


class Advertisement(AdvertisementIn):
    id: int
    created_at: datetime.datetime



advertisements: dict[int, Advertisement] = {}
next_id = 1


@app.post("/advertisement", response_model=Advertisement)
def create_advertisement(advertisement: AdvertisementIn):
    global next_id
    new_advertisement = Advertisement(
        id=next_id,
        created_at=datetime.datetime.now(),
        title=advertisement.title,
        description=advertisement.description,
        price=advertisement.price,
        author=advertisement.author,
    )
    advertisements[next_id] = new_advertisement
    next_id += 1
    return new_advertisement


@app.patch("/advertisement/{advertisement_id}", response_model=Advertisement)
def update_advertisement(advertisement_id: int, advertisement: AdvertisementUpdate):
    if advertisement_id not in advertisements:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    old_advertisement = advertisements[advertisement_id]

    update_data = advertisement.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(old_advertisement, field, value)
    return old_advertisement


@app.delete("/advertisement/{advertisement_id}")
def delete_advertisement(advertisement_id: int):
    if advertisement_id not in advertisements:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    del advertisements[advertisement_id]
    return {"message": "Объявление удалено"}


@app.get("/advertisement/{advertisement_id}", response_model=Advertisement)
def get_advertisement(advertisement_id: int):
    if advertisement_id not in advertisements:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    return advertisements[advertisement_id]


@app.get("/advertisement", response_model=list[Advertisement])
def search_advertisement(
    title: Optional[str] = None,
    author: Optional[str] = None,
    price_from: Optional[float] = None,
    price_to: Optional[float] = None,
):
    result = list(advertisements.values())
    if title is not None:
        result = [a for a in result if title.lower() in a.title.lower()]
    if author is not None:
        result = [a for a in result if a.author == author]
    if price_from is not None:
        result = [a for a in result if a.price >= price_from]
    if price_to is not None:
        result = [a for a in result if a.price <= price_to]
    return result


if __name__ == "__main__":
    uvicorn.run(app)
