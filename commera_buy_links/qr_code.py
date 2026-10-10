import base64
import io
import os
from dataclasses import dataclass
from functools import cached_property

import frappe
import pyqrcode
from frappe.model.document import Document
from PIL import Image, ImageDraw
from pyqrcode.tables import position_adjustment

QUIET_ZONE = 4
FINDER_SIZE = 7
ALIGNMENT_SIZE = 5
PNG_PIXELS = 1200
# Error correction H recovers 30% of the code, so a logo over 22% of its width leaves room for print wear.
LOGO_SHARE = 0.22
LOGO_PIXELS = 256
FORMATS = {"svg": "image/svg+xml", "png": "image/png", "pdf": "application/pdf"}


@dataclass
class QrStyle:
	shape: str = "Square"
	color: str = "#000000"
	background: str = "#FFFFFF"
	logo: str | None = None

	@classmethod
	def from_settings(cls, settings: Document | None = None) -> "QrStyle":
		settings = settings or frappe.get_cached_doc("Buy Links Settings")
		return cls(
			shape=settings.qr_style or cls.shape,
			color=settings.qr_color or cls.color,
			background=settings.qr_background or cls.background,
			logo=settings.get_logo_url(),
		)


def read_logo(url: str) -> Image.Image:
	"""A logo from the site's files or a bundled asset, at most LOGO_PIXELS wide."""
	if url.startswith("/assets/"):
		with open(os.path.join(frappe.local.sites_path, url.lstrip("/")), "rb") as file:
			content = file.read()
	else:
		content = frappe.get_doc("File", {"file_url": url}).get_content()
	image = Image.open(io.BytesIO(content)).convert("RGBA")
	image.thumbnail((LOGO_PIXELS, LOGO_PIXELS))
	return image


class QrCode:
	"""A QR code drawn in the store's style, with a quiet zone so scanners find its edge."""

	def __init__(self, content: str, style: QrStyle | None = None):
		self.style = style or QrStyle.from_settings()
		code = pyqrcode.create(content, error="H" if self.style.logo else "M")
		self.matrix = code.code
		self.size = len(self.matrix)
		self.version = code.version

	@property
	def total(self) -> int:
		return self.size + QUIET_ZONE * 2

	def get_shapes(self) -> list[tuple[str, int, int, int]]:
		"""(kind, x, y, width) in modules. Scanners lock onto the finder and alignment patterns, so those stay
		solid squares in every style; only the data modules become dots."""
		shapes = []
		for x, y, width in self.patterns:
			shapes += [
				("pattern-outer", x, y, width),
				("pattern-gap", x + 1, y + 1, width - 2),
				("pattern-inner", x + 2, y + 2, width - 4),
			]
		for y, row in enumerate(self.matrix):
			for x, is_dark in enumerate(row):
				if is_dark and not self.is_in_pattern(x, y):
					shapes.append(("module", x, y, 1))
		return shapes

	@cached_property
	def patterns(self) -> list[tuple[int, int, int]]:
		"""(x, y, width) of the three finders and of every alignment pattern that does not overlap one."""
		far = self.size - FINDER_SIZE
		finders = [(0, 0, FINDER_SIZE), (far, 0, FINDER_SIZE), (0, far, FINDER_SIZE)]
		centres = position_adjustment[self.version]
		alignments = [
			(x - 2, y - 2, ALIGNMENT_SIZE)
			for x in centres
			for y in centres
			if not any(self.overlaps(x - 2, y - 2, ALIGNMENT_SIZE, *finder) for finder in finders)
		]
		return finders + alignments

	@staticmethod
	def overlaps(x: int, y: int, width: int, other_x: int, other_y: int, other_width: int) -> bool:
		return (
			x < other_x + other_width
			and other_x < x + width
			and y < other_y + other_width
			and other_y < y + width
		)

	@cached_property
	def logo(self) -> Image.Image | None:
		return read_logo(self.style.logo) if self.style.logo else None

	@cached_property
	def logo_box(self) -> tuple[int, int, int]:
		"""(x, y, width) in modules of the plate the logo sits on, centred on the code."""
		width = round(self.size * LOGO_SHARE)
		width += (self.size - width) % 2
		start = (self.size - width) // 2
		return start, start, width

	def get_logo_fit(self, width: float) -> tuple[float, float]:
		"""The logo's width and height inside a square of `width`, keeping its proportions."""
		scale = width / max(self.logo.size)
		return self.logo.width * scale, self.logo.height * scale

	def is_in_pattern(self, x: int, y: int) -> bool:
		return any(px <= x < px + width and py <= y < py + width for px, py, width in self.patterns)

	def get_svg(self) -> str:
		parts = [
			f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.total} {self.total}" shape-rendering="geometricPrecision">',
			f'<rect width="{self.total}" height="{self.total}" fill="{self.style.background}"/>',
		]
		for kind, x, y, width in self.get_shapes():
			x, y = x + QUIET_ZONE, y + QUIET_ZONE
			fill = self.style.background if kind == "pattern-gap" else self.style.color
			if kind == "module" and self.style.shape == "Dots":
				parts.append(f'<circle cx="{x + 0.5}" cy="{y + 0.5}" r="0.45" fill="{fill}"/>')
			else:
				radius = self.get_radius(kind, width)
				parts.append(
					f'<rect x="{x}" y="{y}" width="{width}" height="{width}" rx="{radius}" fill="{fill}"/>'
				)
		if self.logo:
			parts.append(self.get_svg_logo())
		parts.append("</svg>")
		return "".join(parts)

	def get_svg_logo(self) -> str:
		x, y, width = self.logo_box
		x, y = x + QUIET_ZONE, y + QUIET_ZONE
		buffer = io.BytesIO()
		self.logo.save(buffer, "PNG")
		source = base64.b64encode(buffer.getvalue()).decode()
		logo_width, logo_height = self.get_logo_fit(width - 2)
		return (
			f'<rect x="{x}" y="{y}" width="{width}" height="{width}" rx="{round(width * 0.18, 2)}" fill="{self.style.background}"/>'
			f'<image x="{x + (width - logo_width) / 2}" y="{y + (width - logo_height) / 2}" '
			f'width="{logo_width}" height="{logo_height}" href="data:image/png;base64,{source}"/>'
		)

	def get_radius(self, kind: str, width: int) -> float:
		if self.style.shape == "Square":
			return 0
		if kind == "module":
			return 0.3
		return round(width * 0.22, 2)

	def get_image(self) -> Image.Image:
		scale = PNG_PIXELS // self.total
		image = Image.new("RGB", (self.total * scale, self.total * scale), self.style.background)
		draw = ImageDraw.Draw(image)
		for kind, x, y, width in self.get_shapes():
			box = [
				(x + QUIET_ZONE) * scale,
				(y + QUIET_ZONE) * scale,
				(x + QUIET_ZONE + width) * scale - 1,
				(y + QUIET_ZONE + width) * scale - 1,
			]
			fill = self.style.background if kind == "pattern-gap" else self.style.color
			if kind == "module" and self.style.shape == "Dots":
				inset = scale * 0.05
				draw.ellipse([box[0] + inset, box[1] + inset, box[2] - inset, box[3] - inset], fill=fill)
			else:
				draw.rounded_rectangle(box, radius=self.get_radius(kind, width) * scale, fill=fill)
		if self.logo:
			self.paste_logo(image, draw, scale)
		return image

	def paste_logo(self, image: Image.Image, draw: ImageDraw.ImageDraw, scale: int) -> None:
		x, y, width = self.logo_box
		x, y = (x + QUIET_ZONE) * scale, (y + QUIET_ZONE) * scale
		plate = [x, y, x + width * scale - 1, y + width * scale - 1]
		draw.rounded_rectangle(plate, radius=width * scale * 0.18, fill=self.style.background)
		logo_width, logo_height = (round(side) for side in self.get_logo_fit((width - 2) * scale))
		logo = self.logo.resize((logo_width, logo_height), Image.LANCZOS)
		offset = (x + (width * scale - logo_width) // 2, y + (width * scale - logo_height) // 2)
		image.paste(logo, offset, logo)

	def get_file(self, file_format: str) -> bytes:
		if file_format == "svg":
			return self.get_svg().encode()
		buffer = io.BytesIO()
		image = self.get_image()
		if file_format == "png":
			image.save(buffer, "PNG")
		elif file_format == "pdf":
			image.save(buffer, "PDF", resolution=300)
		else:
			frappe.throw(frappe._("A QR code downloads as {0}.").format(", ".join(FORMATS)))
		return buffer.getvalue()
