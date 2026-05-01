"""Tools: image editing, inpainting, resizing."""
from typing import List, Optional

from PIL import Image

from . import image_utils
from . import http_client


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
            "image": {"base64": image_utils.path_to_png_b64(image_path)},
            "description": description,
            "width": width,
            "height": height,
            "text_guidance_scale": text_guidance_scale,
            "no_background": no_background,
            "seed": seed,
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        result = await http_client.call_async("edit-image", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "edit", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 2. Edit image Pro ────────────────────────────────────────────────────

    @mcp.tool()
    async def edit_image_pro(
        reference_image_path: str,
        description: str,
        output_dir: str,
        edit_image_path: Optional[str] = None,
        width: int = 256,
        height: int = 256,
        method: str = "edit_with_text",
        no_background: bool = True,
        seed: int = 0,
    ) -> str:
        """Edit a pixel art image with advanced controls (Pro quality).

        Args:
            reference_image_path: Original sprite to use as style/context reference.
            edit_image_path: The specific image to edit (can differ from reference).
            description: Edit instruction e.g. "add a sword", "change armor color to red".
            method: "edit_with_text" or "edit_with_reference".
            width/height: Output size (up to 512x512).
        """
        ref_b64 = image_utils.path_to_png_b64(reference_image_path)
        ref_img = Image.open(reference_image_path)
        rw, rh = ref_img.size

        if method == "edit_with_reference":
            payload = {
                "method": "edit_with_reference",
                "edit_images": [{"image": {"base64": ref_b64}, "size": {"width": rw, "height": rh}}],
                "reference_image": {"image": {"base64": ref_b64}, "size": {"width": rw, "height": rh}},
                "image_size": {"width": width, "height": height},
                "no_background": no_background,
                "seed": seed,
            }
        else:
            payload = {
                "method": "edit_with_text",
                "edit_images": [{"image": {"base64": ref_b64}, "size": {"width": rw, "height": rh}}],
                "image_size": {"width": width, "height": height},
                "description": description,
                "no_background": no_background,
                "seed": seed,
            }
        if edit_image_path:
            edit_b64 = image_utils.path_to_png_b64(edit_image_path)
            edit_img = Image.open(edit_image_path)
            ew, eh = edit_img.size
            payload["edit_images"] = [{"image": {"base64": edit_b64}, "size": {"width": ew, "height": eh}}]

        result = await http_client.call_async("edit-images-v2", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "edit_image_pro", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 3. Edit animation Pro ────────────────────────────────────────────────

    @mcp.tool()
    async def edit_animation_pro(
        frame_image_paths: List[str],
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        no_background: bool = True,
        seed: int = 0,
    ) -> str:
        """Edit all frames of an animation consistently using a text instruction (Pro).

        Pass all animation frames; they will all be edited in a consistent style.

        Args:
            frame_image_paths: List of animation frame paths (in order).
            description: Edit instruction applied uniformly to all frames.
        """
        frames = []
        for p in frame_image_paths:
            b64 = image_utils.path_to_png_b64(p)
            img = Image.open(p)
            w, h = img.size
            frames.append({"image": {"base64": b64}, "size": {"width": w, "height": h}})

        payload = {
            "description": description,
            "frames": frames,
            "image_size": {"width": width, "height": height},
            "no_background": no_background,
            "seed": seed,
        }
        result = await http_client.call_async("edit-animation-v2", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "edit_anim_pro", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 4. Multi-edit ────────────────────────────────────────────────────────

    @mcp.tool()
    async def multi_edit_generate(
        image_paths: List[str],
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        no_background: bool = True,
        seed: int = 0,
    ) -> str:
        """Apply a text edit instruction to multiple images at once.

        Args:
            image_paths: List of sprite paths to edit.
            description: Edit instruction e.g. "change facial expression to smiling".
        """
        edit_images = []
        for p in image_paths:
            b64 = image_utils.path_to_png_b64(p)
            img = Image.open(p)
            w, h = img.size
            edit_images.append({"image": {"base64": b64}, "size": {"width": w, "height": h}})

        payload = {
            "method": "edit_with_text",
            "edit_images": edit_images,
            "image_size": {"width": width, "height": height},
            "description": description,
            "no_background": no_background,
            "seed": seed,
        }
        result = await http_client.call_async("edit-images-v2", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "multi_edit", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 5. Inpainting ────────────────────────────────────────────────────────

    @mcp.tool()
    async def inpainting_generate(
        inpainting_image_path: str,
        mask_image_path: str,
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        view: str = "none",
        direction: str = "none",
        text_guidance_scale: float = 3.0,
        no_background: bool = True,
        outline: str = "",
        shading: str = "",
        detail: str = "",
        isometric: bool = False,
        oblique_projection: bool = False,
        init_image_strength: int = 300,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
        negative_description: Optional[str] = None,
    ) -> str:
        """Edit a region of an image using a separate mask (V2 API).

        The inpainting_image is the original image. The mask_image indicates
        which region to regenerate (white = regenerate, black = keep).

        Args:
            inpainting_image_path: The original image to edit.
            mask_image_path: Mask image (white areas = regenerate, black = keep).
            description: What to generate in the masked area.
            outline: none / single color black outline / selective outline / lineless.
            shading: none / basic shading / medium shading.
            detail: low detail / medium detail / high detail.
            isometric: True = isometric projection.
            oblique_projection: True = oblique projection.
            init_image_path: Optional init image for fine-grained control.
            negative_description: What to avoid in the generated area.
        """
        payload = {
            "inpainting_image": {"base64": image_utils.path_to_png_b64(inpainting_image_path)},
            "mask_image": {"base64": image_utils.path_to_png_b64(mask_image_path)},
            "description": description,
            "image_size": {"width": width, "height": height},
            "view": view,
            "direction": direction,
            "text_guidance_scale": text_guidance_scale,
            "no_background": no_background,
            "isometric": isometric,
            "oblique_projection": oblique_projection,
            "init_image_strength": init_image_strength,
            "seed": seed,
        }
        if outline:
            payload["outline"] = outline
        if shading:
            payload["shading"] = shading
        if detail:
            payload["detail"] = detail
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if init_image_path:
            payload["init_image"] = {"base64": image_utils.path_to_png_b64(init_image_path)}
        if negative_description:
            payload["negative_description"] = negative_description

        result = await http_client.call("inpaint", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "inpainting", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 6. Inpainting v3 ─────────────────────────────────────────────────────

    @mcp.tool()
    async def inpainting_v3_generate(
        inpainting_image_path: str,
        mask_image_path: str,
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        no_background: bool = False,
        crop_to_mask: bool = True,
        seed: int = 0,
    ) -> str:
        """Inpaint a masked region of a pixel art image (v3 - improved quality).

        Args:
            inpainting_image_path: The original image to edit.
            mask_image_path: Mask image (white areas = regenerate).
            description: Description of what to generate in the masked area.
            crop_to_mask: If true, output is cropped to the masked region.
        """
        inp_b64 = image_utils.path_to_png_b64(inpainting_image_path)
        inp_img = Image.open(inpainting_image_path)
        iw, ih = inp_img.size

        mask_b64 = image_utils.path_to_png_b64(mask_image_path)

        payload = {
            "description": description,
            "inpainting_image": {"image": {"base64": inp_b64}, "size": {"width": iw, "height": ih}},
            "mask_image": {"image": {"base64": mask_b64}, "size": {"width": iw, "height": ih}},
            "no_background": no_background,
            "crop_to_mask": crop_to_mask,
            "seed": seed,
        }
        result = await http_client.call_async("inpaint-v3", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "inpainting_v3", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 7. Remove background ─────────────────────────────────────────────────

    @mcp.tool()
    async def remove_background(
        image_path: str,
        output_dir: str,
        text: str = "",
        background_removal_task: str = "remove_simple_background",
        seed: int = 0,
    ) -> str:
        """Remove the background from a pixel art sprite.

        Args:
            image_path: Sprite to process.
            text: Description hint of the foreground object to help with removal.
            background_removal_task: "remove_simple_background" or "remove_complex_background".
        """
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size

        payload = {
            "image": {"base64": image_utils.path_to_png_b64(image_path)},
            "image_size": {"width": width, "height": height},
            "background_removal_task": background_removal_task,
            "seed": seed,
        }
        if text:
            payload["text"] = text

        result = await http_client.call("remove-background", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "remove_bg", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 8. Resize ────────────────────────────────────────────────────────────

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
        isometric: bool = False,
        oblique_projection: bool = False,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
        init_image_strength: int = 300,
    ) -> str:
        """Intelligently resize a pixel art image to new dimensions while preserving style.

        Unlike simple scaling, this regenerates the image at the target resolution.

        Args:
            reference_image_path: Original sprite to resize.
            width/height: Target output dimensions (16-200).
            description: Optional description to guide the resize.
            isometric: True = isometric perspective.
            oblique_projection: True = oblique projection (beta).
            init_image_path: Optional initial image to start from.
        """
        ref_b64 = image_utils.path_to_png_b64(reference_image_path)
        ref_img = Image.open(reference_image_path)
        rw, rh = ref_img.size

        payload = {
            "description": description,
            "reference_image": {"base64": ref_b64},
            "reference_image_size": {"width": rw, "height": rh},
            "target_size": {"width": width, "height": height},
            "view": view,
            "direction": direction,
            "isometric": isometric,
            "oblique_projection": oblique_projection,
            "no_background": no_background,
            "init_image_strength": init_image_strength,
            "seed": seed,
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if init_image_path:
            payload["init_image"] = {"base64": image_utils.path_to_png_b64(init_image_path)}

        result = await http_client.call("resize", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "resize", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 9. Transfer outfit Pro ───────────────────────────────────────────────

    @mcp.tool()
    async def transfer_outfit_pro(
        reference_image_path: str,
        frame_image_paths: List[str],
        output_dir: str,
        width: int = 64,
        height: int = 64,
        no_background: bool = True,
        seed: int = 0,
    ) -> str:
        """Transfer an outfit from a reference onto all frames of an animation (Pro).

        Args:
            reference_image_path: Character wearing the target outfit.
            frame_image_paths: Animation frames to apply the outfit to.
        """
        ref_b64 = image_utils.path_to_png_b64(reference_image_path)
        ref_img = Image.open(reference_image_path)
        rw, rh = ref_img.size

        frames = []
        for p in frame_image_paths:
            fb64 = image_utils.path_to_png_b64(p)
            fimg = Image.open(p)
            fw, fh = fimg.size
            frames.append({"image": {"base64": fb64}, "size": {"width": fw, "height": fh}})

        payload = {
            "reference_image": {"image": {"base64": ref_b64}, "size": {"width": rw, "height": rh}},
            "frames": frames,
            "image_size": {"width": width, "height": height},
            "no_background": no_background,
            "seed": seed,
        }
        result = await http_client.call_async("transfer-outfit-v2", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "transfer_outfit", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)
