"""Tools: image editing, inpainting, correcting, resizing."""
from typing import List, Optional

from . import image_utils
from . import ws_client


def register(mcp) -> None:

    # ── 1. Edit (simple) ─────────────────────────────────────────────────────

    @mcp.tool()
    async def edit_generate(
        image_path: str,
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        text_guidance_scale: float = 8.0,
        no_background: bool = True,
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Edit an existing pixel art image based on a text instruction.

        Args:
            image_path: The sprite to edit.
            description: Edit instruction e.g. "change facial expression to smiling", "add a sword".
        """
        payload = {
            "image": image_utils.path_to_png_b64(image_path),
            "description": description,
            "image_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "no_background": no_background,
            "seed": str(seed),
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        result = await ws_client.call("generate-edit", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "edit", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 2. Edit image Pro ─────────────────────────────────────────────────────

    @mcp.tool()
    async def edit_image_pro(
        reference_image_path: str,
        description: str,
        output_dir: str,
        edit_image_path: Optional[str] = None,
        width: int = 256,
        height: int = 256,
        method: str = "text",
        no_background: bool = True,
        output_format: str = "frames",
        seed: int = 0,
    ) -> str:
        """Edit a pixel art image with advanced controls (Pro quality).

        Args:
            reference_image_path: Original sprite to use as style/context reference.
            edit_image_path: The specific image to edit (can differ from reference).
            description: Edit instruction e.g. "add a sword", "change armor color to red".
            method: "text" = text-guided edit.
            width/height: Output size (up to 512×512 on tier-2).
        """
        payload = {
            "display_reference_image": image_utils.path_to_png_b64(reference_image_path),
            "description": description,
            "image_size": {"width": width, "height": height},
            "method": method,
            "no_background": no_background,
            "output_format": output_format,
            "seed": str(seed),
        }
        if edit_image_path:
            payload["display_edit_image"] = image_utils.path_to_png_b64(edit_image_path)

        result = await ws_client.call("edit-image-pro", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "edit_image_pro", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 3. Edit animation Pro ─────────────────────────────────────────────────

    @mcp.tool()
    async def edit_animation_pro(
        frame_image_paths: List[str],
        description: str,
        output_dir: str,
        no_background: bool = True,
        output_format: str = "frames",
        seed: int = 0,
    ) -> str:
        """Edit all frames of an animation consistently using a text instruction (Pro).

        Pass all animation frames; they will all be edited in a consistent style.

        Args:
            frame_image_paths: List of animation frame paths (in order).
            description: Edit instruction applied uniformly to all frames.
        """
        frames_b64 = [image_utils.path_to_png_b64(p) for p in frame_image_paths]
        payload = {
            "display_edit_images": frames_b64,
            "description": description,
            "no_background": no_background,
            "output_format": output_format,
            "seed": str(seed),
        }
        result = await ws_client.call("edit-animation-pro", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, 64, 64, "edit_anim_pro", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 4. Multi-edit ─────────────────────────────────────────────────────────

    @mcp.tool()
    async def multi_edit_generate(
        image_paths: List[str],
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        text_guidance_scale: float = 8.0,
        no_background: bool = True,
        n_images: int = 1,
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Apply a text edit instruction to multiple images at once.

        Args:
            image_paths: List of sprite paths to edit.
            description: Edit instruction e.g. "change facial expression to smiling".
            n_images: Number of variations to generate per input image (default 1).
        """
        images_b64 = [image_utils.path_to_png_b64(p) for p in image_paths]
        payload = {
            "images": images_b64,
            "description": description,
            "image_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "no_background": no_background,
            "n_images": n_images,
            "seed": str(seed),
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        result = await ws_client.call("generate-multi-edit", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "multi_edit", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 5. Inpainting ─────────────────────────────────────────────────────────

    @mcp.tool()
    async def inpainting_generate(
        inpainting_image_path: str,
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        view: str = "none",
        direction: str = "none",
        text_guidance_scale: float = 8.0,
        init_image_strength: int = 500,
        transparent_background: bool = True,
        seed: int = 0,
        reference_image_path: Optional[str] = None,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Edit a region of an image using an embedded mask (white areas are regenerated).

        The inpainting image must already contain a white-masked region indicating
        where new content should be generated.

        Args:
            inpainting_image_path: Image with white mask over the region to fill.
            description: What to generate in the masked area.
            reference_image_path: Optional pose/style reference.
        """
        payload = {
            "inpainting_image": image_utils.path_to_png_b64(inpainting_image_path),
            "description": description,
            "image_size": {"width": width, "height": height},
            "view": view,
            "direction": direction,
            "text_guidance_scale": text_guidance_scale,
            "init_image_strength": init_image_strength,
            "transparent_background": transparent_background,
            "seed": str(seed),
            "isometric": False,
            "oblique_projection": False,
            "force_colors": False,
        }
        if reference_image_path:
            payload["reference_image"] = {"base64": image_utils.path_to_png_b64(reference_image_path)}
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        result = await ws_client.call("generate-inpainting", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "inpainting", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 6. Inpainting v3 ──────────────────────────────────────────────────────

    @mcp.tool()
    async def inpainting_v3_generate(
        inpainting_image_path: str,
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        no_background: bool = False,
        crop_to_mask: bool = False,
        seed: int = 0,
    ) -> str:
        """Inpaint a masked region of a pixel art image (v3 – improved quality).

        Args:
            inpainting_image_path: Image with white masked region to fill.
            description: Description of what to generate in the masked area.
            crop_to_mask: If true, output is cropped to the masked region.
        """
        payload = {
            "display_inpainting_image": image_utils.path_to_png_b64(inpainting_image_path),
            "description": description,
            "image_size": {"width": width, "height": height},
            "no_background": no_background,
            "crop_to_mask": crop_to_mask,
            "output_format": "frames",
            "seed": str(seed),
        }
        result = await ws_client.call("generate-inpainting-v3", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "inpainting_v3", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 7. Correct pixel art ──────────────────────────────────────────────────

    @mcp.tool()
    async def correct_pixelart(
        image_paths: List[str],
        output_dir: str,
        width: int = 64,
        height: int = 64,
        strength: int = 10,
    ) -> str:
        """Fix and clean up pixel art images: removes artifacts, noise, and mixed pixels.

        Args:
            image_paths: List of pixel art images to correct.
            strength: Clean-up strength 1–100; higher = more aggressive correction.
        """
        images_b64 = [image_utils.path_to_png_b64(p) for p in image_paths]
        payload = {
            "display_images": images_b64,
            "image_size": {"width": width, "height": height},
            "strength": strength,
        }
        result = await ws_client.call("correct-pixelart", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "correct_pixelart", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 8. Remove background ──────────────────────────────────────────────────

    @mcp.tool()
    async def remove_background(
        image_path: str,
        output_dir: str,
        text: str = "",
        background_removal_task: str = "Simple",
        width: int = 64,
        height: int = 64,
        seed: int = 0,
    ) -> str:
        """Remove the background from a pixel art sprite.

        Args:
            image_path: Sprite to process.
            text: Optional description hint for complex backgrounds.
            background_removal_task: "Simple" for solid/transparent backgrounds.
        """
        payload = {
            "image": image_utils.path_to_png_b64(image_path),
            "text": text,
            "background_removal_task": background_removal_task,
            "image_size": {"width": width, "height": height},
            "seed": str(seed),
        }
        result = await ws_client.call("remove-background", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "remove_bg", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 9. Reshape ────────────────────────────────────────────────────────────

    @mcp.tool()
    async def reshape_generate(
        reference_image_path: str,
        shape_image_path: str,
        output_dir: str,
        description: str = "",
        view: str = "low top-down",
        image_guidance_scale: float = 2.0,
        shape_guidance_scale: float = 1.5,
        text_guidance_scale: float = 4.0,
        init_image_strength: int = 300,
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Reshape a character to match the silhouette/shape of another image.

        Args:
            reference_image_path: The character to reshape.
            shape_image_path: Silhouette/shape to conform to.
            image_guidance_scale: How closely to follow the reference character.
            shape_guidance_scale: How closely to follow the target shape.
        """
        payload = {
            "reference_image": image_utils.path_to_png_b64(reference_image_path),
            "shape_image": image_utils.path_to_png_b64(shape_image_path),
            "character": description,
            "view": view,
            "image_guidance_scale": image_guidance_scale,
            "shape_guidance_scale": shape_guidance_scale,
            "text_guidance_scale": text_guidance_scale,
            "init_image_strength": init_image_strength,
            "seed": str(seed),
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        result = await ws_client.call("generate-reshape", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, 64, 64, "reshape", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 10. Resize ────────────────────────────────────────────────────────────

    @mcp.tool()
    async def resize_generate(
        reference_image_path: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        description: str = "",
        view: str = "none",
        direction: str = "none",
        no_background: bool = False,
        init_image_strength: int = 300,
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Intelligently resize a pixel art image to new dimensions while preserving style.

        Unlike simple scaling, this regenerates the image at the target resolution.

        Args:
            reference_image_path: Original sprite to resize.
            width/height: Target output dimensions.
            description: Optional description to guide the resize.
        """
        payload = {
            "selected_reference_image": image_utils.path_to_png_b64(reference_image_path),
            "description": description,
            "image_size": {"width": width, "height": height},
            "width": width,
            "height": height,
            "view": view,
            "direction": direction,
            "no_background": no_background,
            "init_image_strength": init_image_strength,
            "isometric": False,
            "oblique_projection": False,
            "seed": str(seed),
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        result = await ws_client.call("generate-resize", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "resize", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 11. Try on ────────────────────────────────────────────────────────────

    @mcp.tool()
    async def try_on_generate(
        subject_image_path: str,
        try_on_image_path: str,
        output_dir: str,
        description: str = "",
        width: int = 64,
        height: int = 64,
        text_guidance_scale: float = 8.0,
        no_background: bool = True,
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Apply an outfit/item from one image onto a character from another image.

        Args:
            subject_image_path: The character to dress.
            try_on_image_path: The outfit or item to apply.
            description: Optional description of the item e.g. "golden helmet".
        """
        payload = {
            "subject_image": image_utils.path_to_png_b64(subject_image_path),
            "try_on_image": image_utils.path_to_png_b64(try_on_image_path),
            "description": description,
            "image_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "no_background": no_background,
            "seed": str(seed),
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        result = await ws_client.call("generate-try-on", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "try_on", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 12. Transfer outfit Pro ───────────────────────────────────────────────

    @mcp.tool()
    async def transfer_outfit_pro(
        reference_image_path: str,
        frame_image_paths: List[str],
        output_dir: str,
        no_background: bool = True,
        output_format: str = "frames",
        seed: int = 0,
    ) -> str:
        """Transfer an outfit from a reference onto all frames of an animation (Pro).

        Args:
            reference_image_path: Character wearing the target outfit.
            frame_image_paths: Animation frames to apply the outfit to.
        """
        frames_b64 = [image_utils.path_to_png_b64(p) for p in frame_image_paths]
        payload = {
            "display_reference_image": image_utils.path_to_png_b64(reference_image_path),
            "display_edit_images": frames_b64,
            "no_background": no_background,
            "output_format": output_format,
            "seed": str(seed),
        }
        result = await ws_client.call("transfer-outfit-pro", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, 64, 64, "transfer_outfit", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)
