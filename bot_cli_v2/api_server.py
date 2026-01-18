from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core import AppService

logger = logging.getLogger("assistant_bot")


class ContactIn(BaseModel):
    name: str
    phone: str
    birthday: Optional[str] = None
    notes: Optional[str] = None


app = FastAPI(title="AddressBook API")

# Використовувати директорію даних з оточення, якщо вказана (допомагає тестам), інакше поруч з цим файлом
BASE_DIR = Path(os.environ.get("AB_DATA_DIR", Path(__file__).parent))
service = AppService(BASE_DIR, enable_backups=True, allow_duplicate_phones=False)


@app.get("/contacts")
def list_contacts():
    logger.info("HTTP: list contacts")
    return service.all()


@app.get("/contacts/{name}")
def get_contact(name: str):
    try:
        return service.get(name)
    except Exception as e:
        logger.exception("HTTP get_contact failed: %s", name)
        raise HTTPException(status_code=404, detail="Contact not found") from e


@app.post("/contacts", status_code=201)
def create_contact(payload: ContactIn):
    try:
        service.add(
            payload.name, payload.phone, birthday=payload.birthday, notes=payload.notes
        )
        logger.info("HTTP: created contact %s", payload.name)
        return {"status": "ok"}
    except Exception as e:
        logger.exception("HTTP create_contact failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.put("/contacts/{name}")
def update_contact(name: str, payload: ContactIn):
    try:
        service.change(
            name, payload.phone, birthday=payload.birthday, notes=payload.notes
        )
        logger.info("HTTP: changed contact %s", name)
        return {"status": "ok"}
    except Exception as e:
        logger.exception("HTTP update_contact failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.delete("/contacts/{name}")
def delete_contact(name: str):
    try:
        service.remove(name)
        logger.info("HTTP: removed contact %s", name)
        return {"status": "ok"}
    except Exception as e:
        logger.exception("HTTP delete_contact failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/fsearch")
def http_fuzzy_search(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    try:
        from utils import fuzzy_search

        results = fuzzy_search(query, service.all())
        logger.info("HTTP: fuzzy search '%s' -> %d results", query, len(results))
        return results
    except Exception as e:
        logger.exception("HTTP fuzzy search failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/birthdays")
def list_upcoming_birthdays(days: int = 7):
    try:
        results = service.upcoming_birthdays(days=days)
        logger.info(
            "HTTP: upcoming birthdays next %d days -> %d results", days, len(results)
        )
        return results
    except Exception as e:
        logger.exception("HTTP birthdays failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
