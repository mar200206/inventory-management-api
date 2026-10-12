"""Inventory Management API — CRUD endpoints for a small product inventory."""
import sqlite3
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response, status

from app.database import get_connection, init_db, row_to_dict
from app.schemas import ProductCreate, ProductRead, ProductUpdate


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Inventory Management API",
    description=(
        "A small REST API for managing an inventory of products. "
        "Built with Python, FastAPI, and SQLite."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.post(
    "/products",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    tags=["products"],
    summary="Create a product",
)
def create_product(product: ProductCreate) -> dict:
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO products (name, sku, quantity, price, description)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    product.name,
                    product.sku,
                    product.quantity,
                    product.price,
                    product.description,
                ),
            )
            row = connection.execute(
                "SELECT * FROM products WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
            return row_to_dict(row)
    except sqlite3.IntegrityError as exc:
        if "UNIQUE constraint failed: products.sku" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A product with SKU '{product.sku}' already exists.",
            ) from exc
        raise HTTPException(status_code=400, detail="Product could not be saved.") from exc


@app.get("/products", response_model=list[ProductRead], tags=["products"], summary="List products")
def list_products(
    search: Optional[str] = Query(
        default=None,
        max_length=100,
        description="Search name or SKU",
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[dict]:
    sql = "SELECT * FROM products"
    params = []

    if search and search.strip():
        sql += " WHERE name LIKE ? OR sku LIKE ?"
        term = f"%{search.strip()}%"
        params.extend([term, term])

    sql += " ORDER BY id LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with get_connection() as connection:
        rows = connection.execute(sql, params).fetchall()
        return [row_to_dict(row) for row in rows]

@app.get(
    "/products/{product_id}",
    response_model=ProductRead,
    tags=["products"],
    summary="Get a product",
)
def get_product(product_id: int) -> dict:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    return row_to_dict(row)


@app.patch(
    "/products/{product_id}",
    response_model=ProductRead,
    tags=["products"],
    summary="Update a product",
)
def update_product(product_id: int, changes: ProductUpdate) -> dict:
    updates = changes.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Provide at least one field to update.")
    if any(value is None for value in updates.values()):
        raise HTTPException(status_code=422, detail="Updated fields cannot be null.")

    updates["updated_at"] = "CURRENT_TIMESTAMP"
    set_parts = []
    values: list[object] = []
    for field, value in updates.items():
        if field == "updated_at":
            set_parts.append("updated_at = CURRENT_TIMESTAMP")
        else:
            set_parts.append(f"{field} = ?")
            values.append(value)
    values.append(product_id)

    try:
        with get_connection() as connection:
            existing = connection.execute(
                "SELECT id FROM products WHERE id = ?", (product_id,)
            ).fetchone()
            if existing is None:
                raise HTTPException(status_code=404, detail="Product not found.")
            connection.execute(
                f"UPDATE products SET {', '.join(set_parts)} WHERE id = ?", values
            )
            row = connection.execute(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            ).fetchone()
            return row_to_dict(row)
    except sqlite3.IntegrityError as exc:
        if "UNIQUE constraint failed: products.sku" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A product with this SKU already exists.",
            ) from exc
        raise HTTPException(status_code=400, detail="Product could not be updated.") from exc


@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["products"],
    summary="Delete a product",
)
def delete_product(product_id: int) -> Response:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM products WHERE id = ?", (product_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Product not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
