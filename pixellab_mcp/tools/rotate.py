"""Tools: sprite rotation / view-change."""
from typing import List, Optional

from PIL import Image

from . import image_utils
from . import http_client


def register(mcp) -> None:

    # ── 1. Single rotation ──────────────────────────────────────────────────

    @mcp.tool()
    async def rotate_single(
        from_image_path: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        view_change: int = 0,
        direction_change: int = 45,
        from_view: Optional[str] = None,
        to_view: Optional[str] = None,
        from_direction: Optional[str] = None,
        to_direction: Optional[str] = None,
        image_guidance_scale: float = 3.0,
        isometric: bool = False,
        oblique_projection: bool = False,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
        init_image_strength: int = 300,
        mask_image_path: Optional[str] = None,
    ) -> str:
        """Rotate a sprite by a specific view/direction offset.

        Valid sizes: 16, 32, 64, 128 (powers of two only).

        Args:
            from_image_path: Source sprite to rotate.
            view_change: Vertical tilt change in degrees (e.g. 0).
            direction_change: Horizontal rotation in degrees (e.g. 45, 90, 135, -45).
            from_view: Starting view e.g. "low top-down". Overrides view_change.
            to_view: Target view e.g. "side". Overrides view_change.
            from_direction: Starting direction e.g. "south". Overrides direction_change.
            to_direction: Target direction e.g. "east". Overrides direction_change.
            image_guidance_scale: How closely to follow the source image (1-20).
            isometric: True = isometric view.
            oblique_projection: True = oblique projection.
            mask_image_path: Optional mask image for masked rotation.
        """
        payload = {
            "from_image": {"image": {"base64": image_utils.path_to_png_b64(from_image_path)}, "size": {"width": width, "height": height}},
            "image_size": {"width": width, "height": height},
            "view_change": view_change,
            "direction_change": direction_change,
            "image_guidance_scale": image_guidance_scale,
            "init_image_strength": init_image_strength,
            "isometric": isometric,
            "oblique_projection": oblique_projection,
            "seed": seed,
        }
        if from_view:
            payload["from_view"] = from_view
        if to_view:
            payload["to_view"] = to_view
        if from_direction:
            payload["from_direction"] = from_direction
        if to_direction:
            payload["to_direction"] = to_direction
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if init_image_path:
            payload["init_image"] = {"base64": image_utils.path_to_png_b64(init_image_path)}
        if mask_image_path:
            payload["mask_image"] = {"base64": image_utils.path_to_png_b64(mask_image_path)}

        result = await http_client.call("rotate", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "rotate_single", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 2. Multi-direction rotations ───────────────────────────────────────

    @mcp.tool()
    async def rotations_generate(
        rotation_image_paths: List[str],
        output_dir: str,
        width: int = 64,
        height: int = 64,
        image_guidance_scale: float = 3.0,
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Generate all cardinal rotations (S/E/N/W) for a character from existing views.

        Provide paths to existing direction images in rotation_image_paths
        (order: South, East, North, West). Missing views are generated
        by calling the rotate endpoint for each needed direction.

        Args:
            rotation_image_paths: List of 1-4 paths to existing direction frames.
        """
        # Direction offsets from south: S=0, E=90, N=180, W=-90 (or 270)
        direction_offsets = [0, 90, 180, -90]
        all_paths: List[str] = []

        # Use provided images directly
        for i, path in enumerate(rotation_image_paths):
            all_paths.append(path)

        # Generate missing directions from the first (south) image
        south_image = rotation_image_paths[0] if rotation_image_paths else None
        if not south_image:
            return "Error: at least one rotation image path is required"

        for i in range(len(rotation_image_paths), 4):
            payload = {
                "from_image": {"image": {"base64": image_utils.path_to_png_b64(south_image)}, "size": {"width": width, "height": height}},
                "image_size": {"width": width, "height": height},
                "direction_change": direction_offsets[i],
                "image_guidance_scale": image_guidance_scale,
                "seed": seed,
            }
            if color_image_path:
                payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

            result = await http_client.call("rotate", payload)
            images = image_utils.extract_images(result)
            paths = image_utils.save_response_images(
                images, width, height, f"rotation_{['S','E','N','W'][i]}", output_dir
            )
            all_paths.extend(paths)

        return f"Generated {len(all_paths)} rotation(s):\n" + "\n".join(all_paths)

    # ── 3. Generate 4 rotations from text ──────────────────────────────────

    @mcp.tool()
    async def four_rotations_generate(
        description: str,
        output_dir: str,
        width: int = 32,
        height: int = 32,
        text_guidance_scale: float = 8.0,
        view: str = "low top-down",
        outline: str = "selective outline",
        shading: str = "basic shading",
        detail: str = "medium detail",
        isometric: bool = False,
        force_colors: bool = False,
        mode: Optional[str] = None,
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Generate 4 directional frames (N/E/S/W) for a new character from text.

        Args:
            view: low top-down / high top-down / side
            isometric: True = isometric view.
            force_colors: True = force use of colors from color_image.
            mode: "standard" or "pro" (higher quality, 20-40 gens).
        """
        payload = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "view": view,
            "outline": outline,
            "shading": shading,
            "detail": detail,
            "isometric": isometric,
            "force_colors": force_colors,
            "seed": seed,
        }
        if mode:
            payload["mode"] = mode
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        result = await http_client.call_async("create-character-with-4-directions", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "4_rotations", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 4. Generate 8 rotations from text ──────────────────────────────────

    @mcp.tool()
    async def eight_rotations_generate(
        description: str,
        output_dir: str,
        width: int = 32,
        height: int = 32,
        text_guidance_scale: float = 8.0,
        view: str = "low top-down",
        outline: str = "selective outline",
        shading: str = "basic shading",
        detail: str = "medium detail",
        isometric: bool = False,
        force_colors: bool = False,
        mode: Optional[str] = None,
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Generate 8 directional frames (all eight compass directions) for a new character from text.

        Args:
            view: low top-down / high top-down / side
            isometric: True = isometric view.
            force_colors: True = force use of colors from color_image.
            mode: "standard" or "pro" (higher quality, 20-40 gens).
        """
        payload = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "view": view,
            "outline": outline,
            "shading": shading,
            "detail": detail,
            "isometric": isometric,
            "force_colors": force_colors,
            "seed": seed,
        }
        if mode:
            payload["mode"] = mode
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        result = await http_client.call_async("create-character-with-8-directions", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "8_rotations", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 5. Reference → 8 rotations ─────────────────────────────────────────

    @mcp.tool()
    async def reference_to_8_rotations(
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        view: str = "low top-down",
        style_description: str = "",
        no_background: bool = True,
        seed: int = 0,
        method: str = "create_from_concept",
        concept_image_path: Optional[str] = None,
        reference_image_path: Optional[str] = None,
    ) -> str:
        """Generate all 8 compass-direction rotations from a concept + style reference image.

        Supports 3 methods via the 'method' parameter:
        - "rotate_character": Rotates an existing character (needs reference_image_path).
        - "create_with_style": Creates new character matching style (needs reference_image_path).
        - "create_from_concept" (default): Creates from concept art (needs both concept_image_path and reference_image_path).

        Args:
            method: rotate_character / create_with_style / create_from_concept.
            concept_image_path: Sketch/concept art (only for create_from_concept method).
            reference_image_path: Style reference or character image to rotate.
        """
        payload = {
            "method": method,
            "description": description,
            "style_description": style_description,
            "image_size": {"width": width, "height": height},
            "view": view,
            "no_background": no_background,
            "seed": seed,
        }
        if reference_image_path:
            ref_b64 = image_utils.path_to_png_b64(reference_image_path)
            ref_img = Image.open(reference_image_path)
            rw, rh = ref_img.size
            payload["reference_image"] = {"image": {"base64": ref_b64}, "size": {"width": rw, "height": rh}}
        if concept_image_path:
            concept_b64 = image_utils.path_to_png_b64(concept_image_path)
            concept_img = Image.open(concept_image_path)
            cw, ch = concept_img.size
            payload["concept_image"] = {"image": {"base64": concept_b64}, "size": {"width": cw, "height": ch}}

        result = await http_client.call_async("generate-8-rotations-v2", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "ref_to_8rot", output_dir)
        return f"Saved {len(paths)} rotation(s):\n" + "\n".join(paths)

    # ── 6. Generate 8 rotations v3 (from first frame only) ──────────────────

    @mcp.tool()
    async def generate_8_rotations_v3(
        first_frame_path: str,
        output_dir: str,
        no_background: bool = True,
        seed: int = 0,
    ) -> str:
        """Generate 8 directional rotations from a single reference frame (v3 quality).

        Simpler than reference_to_8_rotations — just provide one sprite as the
        south-facing frame and all 8 directions will be generated automatically.

        Args:
            first_frame_path: Source sprite (south-facing).
            no_background: True = transparent background.
            seed: 0 = random.
        """
        from PIL import Image as _Image
        src = _Image.open(first_frame_path)
        w, h = src.size

        payload = {
            "first_frame": {"image": {"base64": image_utils.path_to_png_b64(first_frame_path)}, "size": {"width": w, "height": h}},
            "no_background": no_background,
            "seed": seed,
        }
        result = await http_client.call_async("generate-8-rotations-v3", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, w, h, "8rot_v3", output_dir)
        return f"Saved {len(paths)} rotation(s):\n" + "\n".join(paths)
