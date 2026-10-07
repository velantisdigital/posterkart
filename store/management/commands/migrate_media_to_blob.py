import os
from pathlib import Path

from django.core.management.base import BaseCommand
from vercel import blob


class Command(BaseCommand):
    help = "Upload local PosterCart media files to Vercel Blob"

    def handle(self, *args, **options):
        # Project root
        base_dir = Path(__file__).resolve().parents[3]
        media_dir = base_dir / "media"

        if not media_dir.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"Media directory not found: {media_dir}"
                )
            )
            return

        # Get Blob token
        token = os.environ.get("BLOB_READ_WRITE_TOKEN")

        if not token:
            self.stdout.write(
                self.style.ERROR(
                    "BLOB_READ_WRITE_TOKEN is not set."
                )
            )
            return

        # Find all media files
        files = [
            path
            for path in media_dir.rglob("*")
            if path.is_file()
        ]

        self.stdout.write(
            self.style.WARNING(
                f"Found {len(files)} media files."
            )
        )

        uploaded = 0
        skipped = 0
        failed = 0

        for file_path in files:
            relative_path = file_path.relative_to(
                media_dir
            ).as_posix()

            blob_path = f"posterkart/{relative_path}"

            try:
                result = blob.put(
                    blob_path,
                    file_path.read_bytes(),
                    access="public",
                    token=token,
                )

                uploaded += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Uploaded: {relative_path}"
                    )
                )

                self.stdout.write(
                    f"  URL: {result.url}"
                )

            except Exception as exc:
                error_message = str(exc)

                # File already exists in Vercel Blob
                if "already exists" in error_message:
                    skipped += 1

                    self.stdout.write(
                        self.style.WARNING(
                            f"↷ Already exists: {relative_path}"
                        )
                    )

                # Any other error
                else:
                    failed += 1

                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ Failed: {relative_path}"
                        )
                    )

                    self.stdout.write(
                        f"  Error: {error_message}"
                    )

        # Final summary
        self.stdout.write("")
        self.stdout.write("=" * 50)
        self.stdout.write(
            self.style.SUCCESS(
                f"Uploaded : {uploaded}"
            )
        )
        self.stdout.write(
            self.style.WARNING(
                f"Skipped  : {skipped}"
            )
        )
        self.stdout.write(
            self.style.ERROR(
                f"Failed   : {failed}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Total    : {uploaded + skipped + failed}"
            )
        )
        self.stdout.write("=" * 50)