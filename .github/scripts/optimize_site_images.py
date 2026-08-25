from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError
import os

ROOT = Path('.')
TRIGGER_BYTES = 1_200_000
MAX_DIMENSION = 2400


def optimize_jpeg(path: Path):
    before = path.stat().st_size
    if before <= TRIGGER_BYTES:
        return None

    try:
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source)
            icc = source.info.get('icc_profile')
            if image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')
            if max(image.size) > MAX_DIMENSION:
                image.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)

            tmp = path.with_name(path.name + '.optimizing')
            quality_used = None
            for quality in (86, 82, 78):
                args = dict(format='JPEG', quality=quality, optimize=True, progressive=True, subsampling=1)
                if icc:
                    args['icc_profile'] = icc
                image.save(tmp, **args)
                quality_used = quality
                if tmp.stat().st_size <= TRIGGER_BYTES:
                    break

            after = tmp.stat().st_size
            if after < before * 0.95:
                os.replace(tmp, path)
                return before, after, quality_used
            tmp.unlink(missing_ok=True)
    except (UnidentifiedImageError, OSError) as exc:
        print(f'Hopper over {path}: {exc}')
    return None


def main():
    changed = 0
    before_total = 0
    after_total = 0

    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in {'.jpg', '.jpeg'}:
            continue
        if '.git' in path.parts or '.github' in path.parts:
            continue
        result = optimize_jpeg(path)
        if not result:
            continue
        before, after, quality = result
        changed += 1
        before_total += before
        after_total += after
        print(f'{path}: {before/1024/1024:.2f} MB -> {after/1024/1024:.2f} MB (q={quality})')

    if changed:
        print(f'Optimaliserte {changed} JPEG-er: {before_total/1024/1024:.1f} MB -> {after_total/1024/1024:.1f} MB')
    else:
        print('Alle JPEG-er er allerede innenfor webgrensen.')


if __name__ == '__main__':
    main()
