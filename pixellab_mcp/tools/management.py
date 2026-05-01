"""Tools: character and object management (CRUD operations)."""
import json
from typing import Optional

from . import http_client


def register(mcp) -> None:

    # ── Character management ──────────────────────────────────────────────────

    @mcp.tool()
    async def list_characters(
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        """List your characters (paginated).

        Args:
            limit: Results per page (1-100).
            offset: Pagination offset.
        """
        result = await http_client.get("characters", {"limit": limit, "offset": offset})
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_character(
        character_id: str,
    ) -> str:
        """Get character details including rotation URLs and animation info.

        Args:
            character_id: The character UUID.
        """
        result = await http_client.get(f"characters/{character_id}")
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def delete_character(
        character_id: str,
    ) -> str:
        """Delete a character and all its data.

        Args:
            character_id: The character UUID.
        """
        result = await http_client.delete(f"characters/{character_id}")
        return f"Character {character_id} deleted."

    @mcp.tool()
    async def export_character_zip(
        character_id: str,
        output_dir: str,
    ) -> str:
        """Export a character as a ZIP file with all rotations, animations, and metadata.

        Args:
            character_id: The character UUID.
        """
        import os
        import httpx

        url = http_client.BASE_URL + f"characters/{character_id}/zip"
        out_dir = os.path.join(output_dir)
        os.makedirs(out_dir, exist_ok=True)
        zip_path = os.path.join(out_dir, f"character_{character_id}.zip")

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(url, headers=http_client._headers())
            if resp.status_code >= 400:
                return f"Error exporting character: {resp.status_code} {resp.text}"
            with open(zip_path, "wb") as f:
                f.write(resp.content)

        return f"Exported to {zip_path}"

    @mcp.tool()
    async def update_character_tags(
        character_id: str,
        tags: str,
    ) -> str:
        """Update tags for a character.

        Args:
            character_id: The character UUID.
            tags: JSON array of strings, max 20 tags, max 50 chars each.
        """
        tag_list = json.loads(tags)
        result = await http_client.patch(
            f"characters/{character_id}/tags",
            {"tags": tag_list},
        )
        return f"Updated tags for character {character_id}."

    # ── Object management ─────────────────────────────────────────────────────

    @mcp.tool()
    async def list_objects(
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        """List your objects (paginated).

        Args:
            limit: Results per page (1-100).
            offset: Pagination offset.
        """
        result = await http_client.get("objects", {"limit": limit, "offset": offset})
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_object(
        object_id: str,
    ) -> str:
        """Get object details including rotation URLs.

        Args:
            object_id: The object UUID.
        """
        result = await http_client.get(f"objects/{object_id}")
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def delete_object(
        object_id: str,
    ) -> str:
        """Delete an object and all its data.

        Args:
            object_id: The object UUID.
        """
        result = await http_client.delete(f"objects/{object_id}")
        return f"Object {object_id} deleted."

    @mcp.tool()
    async def update_object_tags(
        object_id: str,
        tags: str,
    ) -> str:
        """Update tags for an object.

        Args:
            object_id: The object UUID.
            tags: JSON array of strings, max 20 tags, max 50 chars each.
        """
        tag_list = json.loads(tags)
        result = await http_client.patch(
            f"objects/{object_id}/tags",
            {"tags": tag_list},
        )
        return f"Updated tags for object {object_id}."

    # ── Tileset / Tile management ─────────────────────────────────────────────

    @mcp.tool()
    async def list_tilesets(
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        """List all tilesets (top-down and sidescroller) created by you (paginated).

        Args:
            limit: Results per page (1-100).
            offset: Pagination offset.
        """
        result = await http_client.get("tilesets", {"limit": limit, "offset": offset})
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_tileset(
        tileset_id: str,
    ) -> str:
        """Retrieve a completed tileset by its UUID.

        Returns 423 (still generating) until the tileset is ready.

        Args:
            tileset_id: The tileset UUID.
        """
        result = await http_client.get(f"tilesets/{tileset_id}")
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def list_isometric_tiles(
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        """List all isometric tiles created by you (paginated).

        Args:
            limit: Results per page (1-100).
            offset: Pagination offset.
        """
        result = await http_client.get("isometric-tiles", {"limit": limit, "offset": offset})
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_isometric_tile(
        tile_id: str,
    ) -> str:
        """Retrieve a completed isometric tile by its UUID.

        Returns 423 (still generating) until the tile is ready.

        Args:
            tile_id: The isometric tile UUID.
        """
        result = await http_client.get(f"isometric-tiles/{tile_id}")
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def list_tiles_pro(
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        """List all tiles-pro created by you (paginated).

        Args:
            limit: Results per page (1-100).
            offset: Pagination offset.
        """
        result = await http_client.get("tiles-pro", {"limit": limit, "offset": offset})
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def get_tiles_pro(
        tile_id: str,
    ) -> str:
        """Retrieve completed tiles-pro by their UUID.

        Returns 423 (still generating) until the tiles are ready.

        Args:
            tile_id: The tiles-pro UUID.
        """
        result = await http_client.get(f"tiles-pro/{tile_id}")
        return json.dumps(result, indent=2)
