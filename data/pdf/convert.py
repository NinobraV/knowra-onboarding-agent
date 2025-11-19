import os
import re
import fitz  # PyMuPDF
from PIL import Image
import io
import sys
import uuid

try:
    import pytesseract
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def sanitize_name(name):
    return re.sub(r'[^A-Za-z0-9_.-]', '_', name)

def ocr_image_file(image_path, lang='eng+vie'):
    if not OCR_AVAILABLE:
        return ""
    try:
        return pytesseract.image_to_string(Image.open(image_path), lang=lang)
    except Exception:
        return ""

def ocr_image_bytes(image_bytes, lang='eng+vie'):
    if not OCR_AVAILABLE:
        return ""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        return pytesseract.image_to_string(img, lang=lang)
    except Exception:
        return ""

def extract_images_and_ocr_from_page(page, save_images_dir, prefix, lang='eng+vie', save_images=False):
    """
    Trích ảnh nhúng của page, OCR từng ảnh, trả về list các text OCR theo thứ tự.
    Nếu save_images=True sẽ lưu ảnh vào save_images_dir (tên file dựa trên prefix + uuid).
    """
    ocr_texts = []
    image_list = page.get_images(full=True)
    for img_index, img_info in enumerate(image_list, start=1):
        xref = img_info[0]
        pix = fitz.Pixmap(page.parent, xref)
        if pix.n < 5:
            img_bytes = pix.tobytes("png")
        else:
            pix = fitz.Pixmap(fitz.csRGB, pix)
            img_bytes = pix.tobytes("png")
        # OCR from bytes
        text = ocr_image_bytes(img_bytes, lang=lang).strip()
        if text:
            ocr_texts.append(text)
        # optionally save image for debugging / reference
        if save_images:
            ensure_dir(save_images_dir)
            fname = f"{prefix}_img{img_index}_{uuid.uuid4().hex[:8]}.png"
            out_path = os.path.join(save_images_dir, fname)
            with open(out_path, "wb") as f:
                f.write(img_bytes)
        pix = None
    return ocr_texts

def render_page_and_ocr(page, save_images_dir, prefix, lang='eng+vie', save_images=False, dpi=200):
    """
    Render toàn bộ page thành ảnh, OCR toàn trang, trả về text (chuỗi).
    Nếu save_images=True sẽ lưu ảnh full-page.
    """
    pix = page.get_pixmap(dpi=dpi)
    img_bytes = pix.tobytes("png")
    text = ocr_image_bytes(img_bytes, lang=lang).strip()
    if save_images:
        ensure_dir(save_images_dir)
        fname = f"{prefix}_full_{uuid.uuid4().hex[:8]}.png"
        out_path = os.path.join(save_images_dir, fname)
        pix.save(out_path)
    pix = None
    return text

def pdf_to_markdown_embed_ocr(pdf_path, out_md_path, lang='eng+vie',
                              save_images=False, images_dir_name="images",
                              use_render_ocr=True, dpi=200):
    """
    Convert 1 PDF -> 1 Markdown, embed OCR text from images (no image links).
    - lang: lang code cho pytesseract (vd: 'eng', 'vie', 'eng+vie')
    - save_images: nếu True sẽ lưu ảnh (để tham khảo), mặc định False
    - images_dir_name: thư mục con để lưu ảnh nếu save_images=True
    - use_render_ocr: nếu True, khi không có text PDF thì render toàn page và OCR toàn trang
    """
    doc = fitz.open(pdf_path)
    md_dir = os.path.dirname(out_md_path)
    ensure_dir(md_dir)
    images_out_dir = os.path.join(md_dir, images_dir_name)

    md_lines = []
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    safe_base = sanitize_name(base)
    md_lines.append(f"# {base}\n")

    for pno in range(doc.page_count):
        page = doc.load_page(pno)
        md_lines.append(f"## Page {pno+1}\n")
        page_text = page.get_text("text").strip()

        # Nếu PDF có text, giữ nguyên text (văn bản) đầu tiên
        if page_text:
            md_lines.append(page_text + "\n")

        # Luôn cố gắng OCR ảnh nhúng (vì có thể là caption, chú thích, hình chứa text)
        page_prefix = f"{safe_base}_p{pno+1}"
        ocr_texts = extract_images_and_ocr_from_page(page, images_out_dir, page_prefix,
                                                     lang=lang, save_images=save_images)
        for t in ocr_texts:
            # Thêm phân đoạn OCR rõ ràng, có thể chỉnh format nếu cần
            md_lines.append(t + "\n")

        # Nếu trang không có text và chưa có OCR từ ảnh nhúng, dùng render toàn trang để OCR
        if (not page_text) and (not ocr_texts) and use_render_ocr:
            full_ocr = render_page_and_ocr(page, images_out_dir, page_prefix,
                                           lang=lang, save_images=save_images, dpi=dpi)
            if full_ocr:
                md_lines.append(full_ocr + "\n")

    with open(out_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    doc.close()

def convert_folder_embed_ocr(input_dir, output_dir, lang='eng+vie',
                             keep_structure=True, save_images=False,
                             images_dir_name="images", use_render_ocr=True):
    """
    Duyệt đệ quy input_dir, convert mọi .pdf sang .md trong output_dir.
    Tự động tạo folder cần thiết.
    """
    if not os.path.isdir(input_dir):
        raise ValueError(f"Input folder không tồn tại: {input_dir}")

    ensure_dir(output_dir)
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)

    for root, dirs, files in os.walk(input_dir):
        rel_root = os.path.relpath(root, input_dir)
        if keep_structure and rel_root != ".":
            target_root = os.path.join(output_dir, rel_root)
        else:
            target_root = output_dir
        ensure_dir(target_root)

        for fname in files:
            if fname.lower().endswith(".pdf"):
                in_path = os.path.join(root, fname)
                base, _ = os.path.splitext(fname)
                out_md = os.path.join(target_root, base + ".md")
                try:
                    pdf_to_markdown_embed_ocr(in_path, out_md, lang=lang,
                                              save_images=save_images, images_dir_name=images_dir_name,
                                              use_render_ocr=use_render_ocr)
                    print(f"Converted: {in_path} -> {out_md}")
                except Exception as e:
                    print(f"Error converting {in_path}: {e}", file=sys.stderr)

if __name__ == "__main__":
    # Thay đường dẫn theo nhu cầu
    INPUT = r"E:\Assignment\Knowra_Git\knowra-onboarding-agent\data\pdf\sample_pdf"
    OUTPUT = r"E:\Assignment\Knowra_Git\knowra-onboarding-agent\data\raw"
    # Ví dụ: dùng tiếng Việt + tiếng Anh, không lưu ảnh, giữ cấu trúc thư mục
    convert_folder_embed_ocr(INPUT, OUTPUT, lang='eng+vie', keep_structure=True,
                             save_images=False, images_dir_name="images", use_render_ocr=True)
