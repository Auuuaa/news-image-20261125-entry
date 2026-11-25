// THE WORLD TODAY — news-image-20261125 entry point.
//
// render.py drew the front page into entry.png ahead of time. This
// program only checks that the PNG is intact and inside the bounty
// limits (1024x1024, at most 1 MiB, all chunk CRCs valid), then
// copies it to wherever the harness requests via $MAKEFUN_OUTPUT_DIR.
//
// The PNG is located relative to this script, never relative to the
// working directory — the grader may invoke node from anywhere, so a
// bare "entry.png" lookup would fail with ENOENT outside the repo.

import { crc32 } from "node:zlib";
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_SIGNATURE = Buffer.from([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
]);
const EDGE = 1024;
const SIZE_LIMIT = 1024 * 1024;

const scriptDir = dirname(fileURLToPath(import.meta.url));
const sourcePng = join(scriptDir, "entry.png");

function fail(detail: string): never {
  console.error(`entry.png failed validation: ${detail}`);
  process.exit(1);
}

function checkPng(png: Buffer): void {
  if (png.length < PNG_SIGNATURE.length || !png.subarray(0, 8).equals(PNG_SIGNATURE)) {
    fail("missing PNG signature");
  }
  if (png.length > SIZE_LIMIT) {
    fail(`file is ${png.length} bytes, over the 1 MiB cap`);
  }
  let offset = 8;
  let sawHeader = false;
  let sawTrailer = false;
  while (offset + 12 <= png.length) {
    const length = png.readUInt32BE(offset);
    const kind = png.toString("ascii", offset + 4, offset + 8);
    const dataEnd = offset + 8 + length;
    if (dataEnd + 4 > png.length) {
      fail(`chunk ${kind} overruns the file`);
    }
    const stored = png.readUInt32BE(dataEnd);
    const computed = crc32(png.subarray(offset + 4, dataEnd));
    if (stored !== computed) {
      fail(`chunk ${kind} has a bad CRC`);
    }
    if (kind === "IHDR") {
      sawHeader = true;
      const width = png.readUInt32BE(offset + 8);
      const height = png.readUInt32BE(offset + 12);
      const bitDepth = png[offset + 16];
      const colour = png[offset + 17];
      if (width !== EDGE || height !== EDGE) {
        fail(`image is ${width}x${height}, expected ${EDGE}x${EDGE}`);
      }
      if (bitDepth !== 8 || (colour !== 2 && colour !== 6)) {
        fail(`unexpected colour setup: depth ${bitDepth}, type ${colour}`);
      }
    }
    offset = dataEnd + 4;
    if (kind === "IEND") {
      sawTrailer = true;
      break;
    }
  }
  if (!sawHeader) {
    fail("no IHDR chunk");
  }
  if (!sawTrailer) {
    fail("no IEND chunk — file is truncated");
  }
}

const destinationDir = process.env.MAKEFUN_OUTPUT_DIR ?? "./output";
const png = readFileSync(sourcePng);
checkPng(png);
mkdirSync(destinationDir, { recursive: true });
const destination = join(destinationDir, "entry.png");
copyFileSync(sourcePng, destination);
const copied = statSync(destination).size;
if (copied !== png.length) {
  fail(`copied ${copied} bytes, expected ${png.length}`);
}
console.log(`entry.png OK: ${EDGE}x${EDGE}, ${png.length} bytes -> ${destination}`);
